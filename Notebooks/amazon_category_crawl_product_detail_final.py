import requests
from lxml import html
import pandas as pd
import re
import json
import random
import time
from datetime import datetime

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
    while http_status != 200 or proxy_retries == 4:
        # Proxy Rotate
        proxy = {}
        proxy = proxy_rotate(proxy_list)
        res = requests.get(url, headers=headers, proxies=proxy)
        http_status = res.status_code
        proxy_retries = proxy_retries + 1
    tree = html.fromstring(res.text)
    return tree, http_status, proxy, proxy_retries



def get_next_page_url(p_tree):
    next_page_url_xp = p_tree.xpath("//a[contains(@class, 's-pagination-next')]/@href")
    if next_page_url_xp:
        next_page_url = 'https://www.amazon.ae' + next_page_url_xp[0].strip()
        return next_page_url
    else:
        return ''


def product_crawl(url, page_number):
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


if __name__ == '__main__':
    # Baby Stationary Activity Centers
    final_url = 'https://www.amazon.ae/b?node=21731964031&ref=sr_nr_n_1'
    final_url = 'https://www.amazon.ae/b?node=12149537031&ref=sr_nr_n_1'

    next_page_url = final_url
    pages_to_crawl = 1000
    page_number = 1
    all_page_product_data = []
    while next_page_url != '' or page_number >= pages_to_crawl:
        prod_data_lst, next_page_url, page_number = product_crawl(next_page_url, page_number=page_number)

        all_page_product_data = all_page_product_data + prod_data_lst

    print("Succesfully crawl category !")
