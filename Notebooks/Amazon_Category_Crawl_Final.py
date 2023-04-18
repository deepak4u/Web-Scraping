import requests
from lxml import html
import pandas as pd
import random
import time
import re
from datetime import datetime
import glob
from itertools import groupby
import json

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

proxy_list = [
    "http://655383:df51erG@p.nohodo.com:4698",
    "http://username1:pass123@london.wonderproxy.com:11000",
    "http://username2:pass123@spain.wonderproxy.com:11000",
]

def proxy_rotate(proxy_list):
    proxy_select = random.choice(proxy_list)
    proxy = {"https": proxy_select}
    return proxy


def parse_page(url, proxy_list, headers):
    ''' Return : tree, http_status, proxy, proxy_retries'''
    http_status = ''
    proxy_retries = -1
    while http_status != 200 or proxy_retries == 6:
        # Proxy Reset and Rotate
        proxy = {}
        proxy = proxy_rotate(proxy_list)
        res = requests.get(url, headers=headers, proxies=proxy)
        http_status = res.status_code
        proxy_retries = proxy_retries + 1
    tree = html.fromstring(res.text)
    return tree, http_status, proxy, proxy_retries


# get all main category
def main_cat_crawl_level1(selected_main_category_lst:list, home_url:str):
    '''
    Main category crawl from search box

    Returns:
         cat_level(list): Main Category level data in the form of list of dictionaries
    '''
    url = home_url
    cat_level = []
    while not cat_level:
        tree, http_status, proxy_used, proxy_retries = parse_page(url, proxy_list, headers)

        main_category_lst_xp = tree.xpath("//form[@id='nav-search-bar-form']//select[@id='searchDropdownBox']//option/@value")
        if main_category_lst_xp:
            main_category_names = [cat.split("=")[1] for cat in main_category_lst_xp]
            for cat in main_category_names:
                cat_level_name = cat
                cat_level_url = home_url + '/s/ref=nb_sb_noss?url=search-alias%3D' + cat_level_name
                cat_level.append({
                    f'cat_level_name': cat_level_name,
                    f'cat_level_url': cat_level_url
                })


    print(f"Main Category count: ", len(cat_level))

    if 'all' in selected_main_category_lst and len(selected_main_category_lst) == 1:
        return cat_level
    else:
        #selected_cat_level = [cat for cat in cat_level if cat.get('cat_level_name') in selected_main_category_lst]
        selected_cat_level = []
        for cat_data in cat_level:
            if cat_data['cat_level_name'] in selected_main_category_lst:
                selected_cat_level.append(cat_data)

        return selected_cat_level


def sub_cat_crawl(cat_name_url_data:list, home_url:str):
    '''
    Sub category crawl, level 2 onwards and returns category level data.  [{'cat_level_name': str, 'cat_level_url': str}, ...]

    Parameters:
        cat_name_url_data (list): Category name
        home_url(str): Site Home Page URL

    Returns:
         cat_level(list): Category level data in the form of list of dictionaries
    '''
    cat_level = []
    # Previous Category
    for cat_name_url in cat_name_url_data:
        time.sleep(random.randint(2,3))
        tree, http_status, proxy_used, proxy_retries = parse_page(cat_name_url['cat_level_url'], proxy_list, headers)

        category_lst_xp = tree.xpath("//li[@class='a-spacing-micro apb-browse-refinements-indent-2']")
        tree_block_xp_str = "//li[@class='a-spacing-micro apb-browse-refinements-indent-2']"
        if not category_lst_xp:
            category_lst_xp = tree.xpath("//li[@class='a-spacing-micro s-navigation-indent-2']")
            tree_block_xp_str = "//li[@class='a-spacing-micro s-navigation-indent-2']"
        if category_lst_xp:
            # Next category
            cat_level_name = cat_level_url = ''
            for row, tree_block in enumerate(category_lst_xp):
                cat_level_name_xp = tree_block.xpath(f"{tree_block_xp_str}[{row+1}]//a/span[@dir='auto']/text()")
                if not cat_level_name_xp:
                    cat_level_name_xp = tree_block.xpath(f"{tree_block_xp_str}[{row+1}]//a/span[@class='a-size-base a-color-base']/text()")
                cat_level_url_xp = tree_block.xpath(f"{tree_block_xp_str}[{row+1}]//a/@href")

                if cat_level_name_xp:
                    cat_level_name = cat_name_url['cat_level_name'] + ' > ' + cat_level_name_xp[0].strip()
                if cat_level_url_xp:
                    cat_level_url = cat_level_url_xp[0].strip()
                    if home_url.split('//')[1] not in cat_level_url:
                        cat_level_url = home_url + cat_level_url

                cat_level.append({
                    f'cat_level_name': cat_level_name,
                    f'cat_level_url': cat_level_url
                })
    print(" ")
            #print(f"{cat_level['cat_level_name']} Category count: ", len(cat_level))
    return cat_level


def sub_cat_crawl_call(prev_cat_data: list, level: int):
    '''
    Level 2 onward category crawl
    Recursion category func sub_cat_crawl(). only crawl next data if previous data is available and store in csv file.
    Exclude Level 1 category - main category
    '''
    if prev_cat_data:
        next_cat_data = sub_cat_crawl(prev_cat_data, home_url)
        if next_cat_data:
            df = pd.DataFrame(next_cat_data)

            main_cat_name = df['cat_level_name'].iloc[0].split('>')[0].strip()
            df.to_csv(f"amazon_category_crawl/{country_name}/{main_cat_name}_level_{level}.csv", index=False)

            # df.to_csv(f"amazon_category_crawl/{country_name}/amazon_category_crawl_level_{level}.csv", index=False)
            print(f"Successfully save file: {main_cat_name}_level_{level}")

            return sub_cat_crawl_call(next_cat_data, level + 1)


# def all_cat_crawl_call(selected_main_category_lst:list, home_url:str):
#     '''
#     All category crawl including level 1 category- main category
#     Recursion category func sub_cat_crawl(). only crawl next data if previous data is available and store in csv file.
#     '''
#     main_cat_data_level1 = main_cat_crawl_level1(selected_main_category_lst, home_url)
#     if main_cat_data_level1:
#         df_main_cat_data_level1 = pd.DataFrame(main_cat_data_level1)
#
#         main_cat_name = df_main_cat_data_level1['cat_level_name'].iloc[0].split('>')[0].strip()
#         df_main_cat_data_level1.to_csv(f"amazon_category_crawl/{country_name}/{main_cat_name}_level_1.csv", index=False)
#
#         # df_main_cat_data_level1.to_csv(f"amazon_category_crawl/{country_name}/amazon_category_crawl_level_1.csv", index=False)
#         print(f"Successfully save file: {main_cat_name}_level_1")
#
#     # Level 2 onwards crawl
#     if main_cat_data_level1:
#         # Recursive call function start from level 2 level + 1
#         sub_cat_crawl_call(main_cat_data_level1, level=2)
#
#     print("")
#     print("All Categories Successfully Crawled !!! ")


def all_cat_crawl_call(selected_main_category_lst:list, home_url:str):
    '''
    All category crawl including level 1 category- main category
    Recursion category func sub_cat_crawl(). only crawl next data if previous data is available and store in csv file.
    '''
    main_cat_data_level1 = main_cat_crawl_level1(selected_main_category_lst, home_url)
    if main_cat_data_level1:
        for main_cat in main_cat_data_level1:
            # Create separate ist of dictionaries for separate main category
            indivisual_main_cat_lst = []
            indivisual_main_cat_lst.append(main_cat)
            df_main_cat_data_level1 = pd.DataFrame(indivisual_main_cat_lst)

            main_cat_name = df_main_cat_data_level1['cat_level_name'].iloc[0].split('>')[0].strip()
            df_main_cat_data_level1.to_csv(f"amazon_category_crawl/{country_name}/{main_cat_name}_level_1.csv", index=False)
            # Reset Dataframe
            del df_main_cat_data_level1

            # df_main_cat_data_level1.to_csv(f"amazon_category_crawl/{country_name}/amazon_category_crawl_level_1.csv", index=False)
            print(f"Successfully save file: {main_cat_name}_level_1")

            # Level 2 onwards crawl
            # Recursive call function start from level 2 level + 1
            sub_cat_crawl_call(indivisual_main_cat_lst, level=2)

    print("")
    print("All Categories Successfully Crawled !!! ")


def select_main_cat():
    ''' Returns selected main category to crawl. Used to skip the other main category after crawl '''
    # Todo Note: Main category name might change. Check and update if needed
    main_category_lst = [
        'aps', 'amazon-devices', 'fashion', 'amazon-global-store', 'warehouse-deals', 'appliances',
        'automotive', 'baby', 'beauty', 'stripbooks', 'computers', 'electronics', 'gift-cards',
        'grocery', 'hpc', 'local-services', 'garden', 'kitchen', 'fashion-luggage', 'mi', 'office-products',
        'pets', 'instant-video', 'sports', 'specialty-aps-sns', 'tools', 'toys', 'videogames'
    ]

    main_category_dict = {v + 1: k for v, k in enumerate(main_category_lst)}

    print("----- Select Numbers -----")
    print(*main_category_dict.items(), sep=', ')
    print("---------------------")
    selected_category_nums = list(map(int, (input("Select Number/Numbers: ").strip().split())))
    selected_main_category_lst = [main_category_dict[key] for key in selected_category_nums]
    print("----- Selected category ------", selected_main_category_lst, sep='\n')

    return selected_main_category_lst



# def final_combined_category():
#     # Read all csv files and collate into 1 df
#     csv_filepath_lst = glob.glob(f'amazon_category_crawl/{country_name}/*.csv')
#     # for file_name in csv_filepath_lst:
#     #     file_name = file_name.split('\\')[-1].replace('.csv', '')
#     #     df = pd.concat(map(pd.read_csv, csv_filepath_lst))
#
#     df = pd.concat(map(pd.read_csv, csv_filepath_lst))
#     main_cat_name = df['cat_level_name'].iloc[0].split('>')[0].strip()
#
#     # Level 1 - 10  Category column create and split
#     df[['Category_Level_' + str(level) for level in range(1, 11)]] = ''
#     # max count split
#     number_of_split_columns = df['cat_level_name'].str.count('>').max()
#     df[['Category_Level_' + str(level) for level in range(1, number_of_split_columns + 2)]] = df[
#         'cat_level_name'].str.split('>', expand=True)
#
#     df.to_csv(f"amazon_category_crawl/Category CSV/{main_cat_name}.csv", index=False)
#     print(f"Final Combined File saved successfully !!!")

def final_combined_category():
    # Read all csv files and collate into 1 df
    csv_filepath_lst = glob.glob(f'amazon_category_crawl/{country_name}/*.csv')
    # for file_name in csv_filepath_lst:
    #     file_name = file_name.split('\\')[-1].replace('.csv', '')
    #     df = pd.concat(map(pd.read_csv, csv_filepath_lst))

    # Groupby on main cat name and split itto separate list - list of lists
    organised_csv_filepath_lst = [list(cat) for _, cat in groupby(csv_filepath_lst, lambda x: x.split('\\')[-1].split('_')[0])]
    for main_cat_csv_filepath_lst in organised_csv_filepath_lst:
        # concat only organised list. list of lists
        df = pd.concat(map(pd.read_csv, main_cat_csv_filepath_lst))
        main_cat_name = df['cat_level_name'].iloc[0].split('>')[0].strip()

        # Level 1 - 10  Category column create and split
        df[['Category_Level_' + str(level) for level in range(1, 11)]] = ''
        # max count split
        number_of_split_columns = df['cat_level_name'].str.count('>').max()
        df[['Category_Level_' + str(level) for level in range(1, number_of_split_columns + 2)]] = df['cat_level_name'].str.split('>', expand=True)

        df.to_csv(f"amazon_category_crawl/Category CSV/{main_cat_name}.csv", index=False)
        # Delete variables for each iteration
        del df
        print(f"Final Combined File {main_cat_name} saved succesfully !!!")



# ----------------------------
# Products basic details from cat pages using pagination
def get_next_page_url(p_tree):
    ''' Return Next page url '''
    next_page_url_xp = p_tree.xpath("//a[contains(@class, 's-pagination-next')]/@href")
    if next_page_url_xp:
        next_page_url = 'https://www.amazon.ae' + next_page_url_xp[0].strip()
        return next_page_url
    else:
        return ''


def product_crawl(url:str, page_number:int):
    ''' Crawl multiple products info from category using pagination '''
    p_tree, http_status, proxy_used, proxy_retries = parse_page(url, proxy_list, headers)
    see_all_res_xp = p_tree.xpath("//div[@class='a-cardui-body']//a[@class='a-link-normal']/@href")
    if see_all_res_xp:
        # Delay for immediate new page request just for pagination page
        time.sleep(random.randint(2,3))
        # if see_all_res_xp then get new url from page for pagination
        url = 'https://www.amazon.ae' + see_all_res_xp[0].strip()
        p_tree, http_status, proxy_used, proxy_retries = parse_page(url, proxy_list, headers)

    prod_data_lst = []
    extract_date = datetime.today().strftime('%Y-%m-%d')
    products_lst_xp = p_tree.xpath("//div[@data-component-type='s-search-result']")
    # Search result count from page
    search_result_text_count_xp = p_tree.xpath("//span[@data-component-type='s-result-info-bar']//span[@dir='auto']/text()")
    search_result_text_count = ''
    if search_result_text_count_xp:
        search_result_text_count = search_result_text_count_xp[0].strip()

    if products_lst_xp:
        for row in range(0, len(products_lst_xp)):
            prod_name_xp = p_tree.xpath(f"//div[@data-component-type='s-search-result'][{row + 1}]//span[@class='a-size-base-plus a-color-base a-text-normal']/text()")
            prod_url_xp = p_tree.xpath(f"//div[@data-component-type='s-search-result'][{row + 1}]//h2//a[contains(@class, 's-underline-link-text')]/@href")
            badge_text_xp = p_tree.xpath( f"//div[@data-component-type='s-search-result'][{row + 1}]//span[@class='a-badge-text']/text()")
            prod_rating_text_xp = p_tree.xpath(f"//div[@data-component-type='s-search-result'][{row + 1}]//span[@class='a-icon-alt']/text()")
            prod_review_xp = p_tree.xpath(f"//div[@data-component-type='s-search-result'][{row + 1}]//span[@class='a-size-base s-underline-text']/text()")
            was_price_xp = p_tree.xpath(f"//div[@data-component-type='s-search-result'][{row + 1}]//span[@class='a-price a-text-price']//span[@class='a-offscreen']/text()")
            now_price_xp = p_tree.xpath(f"//div[@data-component-type='s-search-result'][{row + 1}]//span[@class='a-price']//span[@class='a-offscreen']/text()")
            shipping_days_text_xp = p_tree.xpath(f"//div[@data-component-type='s-search-result'][{row + 1}]//span[@class='a-color-base a-text-bold']/text()")
            shipping_cost_text_xp = p_tree.xpath(f"//div[@data-component-type='s-search-result'][{row + 1}]//div[@class='a-row']//span[@class='a-color-base']/text()")
            variant_urls_xp = p_tree.xpath(f"//div[@data-component-type='s-search-result'][{row + 1}]//div[@class='aok-inline-block aok-align-center']//a/@href")
            prime_tag_xp = p_tree.xpath(f"//div[@data-component-type='s-search-result'][{row + 1}]//i[@aria-label='Amazon Prime']/@aria-label")
            limited_stock_info_xp = p_tree.xpath(f"//div[@data-component-type='s-search-result'][{row + 1}]//span[@class='a-size-base a-color-price']/text()")

            prod_name = prod_url = badge_text = prod_rating_text = prod_review = was_price = now_price = shipping_days_text = shipping_cost_text = prime_tag = limited_stock_info = prod_url_asin = ''
            variant_urls = []

            if prod_name_xp:
                prod_name = prod_name_xp[0].strip()
            if prod_url_xp:
                prod_url = 'https://www.amazon.ae' + prod_url_xp[0].strip()
                if 'dp/' in prod_url:
                    prod_url_asin = prod_url.split('dp/')[1].split('/')[0]
                elif 'dp%2F' in prod_url:
                    prod_url_asin = prod_url.split('dp%2F')[1].split('%2F')[0]
            if badge_text_xp:
                badge_text = ' '.join(x.strip() for x in badge_text_xp)
            if prod_rating_text_xp:
                prod_rating_text = prod_rating_text_xp[0].strip()
            if prod_review_xp:
                prod_review = re.sub('[^0-9]+', '', prod_review_xp[0])
            if was_price_xp:
                was_price = re.sub('[^0-9.]+', '', was_price_xp[0])
            if now_price_xp:
                now_price = re.sub('[^0-9.]+', '', now_price_xp[0])
            if shipping_days_text_xp:
                shipping_days_text = ' - '.join(shipping_days_text_xp)
            if shipping_cost_text_xp:
                shipping_cost_text = shipping_cost_text_xp[0].strip()
            if variant_urls_xp:
                variant_urls = ['https://www.amazon.ae' + x.strip() for x in variant_urls_xp]
            if prime_tag_xp:
                prime_tag = prime_tag_xp[0].strip()
            if limited_stock_info_xp:
                limited_stock_info = limited_stock_info_xp[0].strip()

            prod_data_lst.append({
                'extract_date': extract_date,
                'prod_name': prod_name,
                'prod_url': prod_url,
                'prod_url_asin': prod_url_asin,
                'badge_text': badge_text,
                'prod_rating_text': prod_rating_text,
                'prod_review': prod_review,
                'was_price': was_price,
                'now_price': now_price,
                'shipping_days_text': shipping_days_text,
                'shipping_cost_text': shipping_cost_text,
                'variant_urls': variant_urls,
                'prime_tag': prime_tag,
                'limited_stock_info': limited_stock_info,
                'page_number':page_number,

                'search_result_text_count': search_result_text_count
            })


    print(f"Page {page_number} Crawl Succesfull !")
    page_number += 1
    # Get next page
    next_page_url = get_next_page_url(p_tree)

    return prod_data_lst, next_page_url, page_number






if __name__ == "__main__":
    start_time = time.time()
    home_url = country_name = ''

    print("***** Amazon Category Crawl *****")
    print("Amazon UAE: 1", "Amazon EGP: 2", "Amazon KSA: 3", sep='\n')
    selected_country = int(input("Select Country:"))
    if selected_country == 1:
        country_name = 'UAE'
        home_url = 'https://www.amazon.ae'
    elif selected_country == 2:
        country_name = 'EGP'
        home_url = 'https://www.amazon.eg/-/en'
    elif selected_country == 3:
        country_name = 'KSA'
        home_url = 'https://www.amazon.sa/-/en'

    print("---------------------")
    print("Country Name: ", country_name)
    print("Home URL: ", home_url)

    print("----- Select Category to crawl -----")
    print("Manually select: 1", "Select All: 2", sep='\n')
    selected_category = int(input("Select Option:"))
    if selected_category == 1:
        selected_main_category_lst = select_main_cat()
        # Only selected main category crawl
        all_cat_crawl_call(selected_main_category_lst, home_url)

    elif selected_category == 2:
        selected_main_category_lst = ['all']
        all_cat_crawl_call(selected_main_category_lst, home_url)

    elif selected_category == 3:
        final_combined_category()


    final_combined_category()

    print("Execution Time: ", time.time() - start_time)

    # Todo: function pass while crawling category link and append
    # # -------- Product Crawl ------------
    # # Diaper Wipes & Refills (1-24 of 141 results for "Diaper Wipes & Refills")
    # cat_url = 'https://www.amazon.ae/b?node=12198825031&ref=sr_nr_n_3'
    # next_page_url = cat_url
    # # 400 page limit
    # pages_to_crawl = 1000
    # page_number = 1
    # all_page_product_data = []
    # while next_page_url != '' or page_number >= pages_to_crawl:
    #     prod_data_lst, next_page_url, page_number = product_crawl(next_page_url, page_number=page_number)
    #
    #     all_page_product_data = all_page_product_data + prod_data_lst
    #
    # print("Succesfully Crawl Category !")



