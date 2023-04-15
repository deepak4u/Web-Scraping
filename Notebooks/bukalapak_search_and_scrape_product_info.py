import requests
import pandas as pd

def get_data(headers_dict, access_token,pages):
    url = 'https://api.bukalapak.com/multistrategy-products/'
    try:
        for page_no in range(1, pages+1):
            print(f'Fetching page {page_no} data.')
            parameter = {
                'prambanan_override': True,
                'keywords': keyword,
                'limit': 50,
                'offset': 50,
                'page': page_no,
                'facet': True,
                'access_token': access_token
            }

            res = requests.get(url, params=parameter, headers=headers_dict).json()
            products = res['data']

            for product in products:
                product_name = product['name']
                product_url = product['url']
                product_price = product['price']

                product_info_list.append({
                    'Product Name' : product_name,
                    'Product Link' : product_url,
                    'Product Price' : product_price
                })
        pd.DataFrame(product_info_list).to_excel(f'{keyword}_info_bukalapak.xlsx')
    except Exception as e:
         print('Connection refused: ',e)
    finally:
        print('Finished')


if __name__ == '__main__':
    print('*** Bukalapak Product Scraping ***')
    print('You can find access token by manually visiting API Secret Page at Bukalapak')
    print('Search any product on website -> Inspect -> Network tab Search Any product from list -> Headers/Payload -> access_token | Or search in network res tab Filter')
    # By manually visiting API Secret Page at Bukalapak
    # or
    # By API call to Authentication for Bukalapak API(Username Pass required)
    # Search Website Product -> Network tab Search Any product from list -> Headers -> access token
    # Copy access token and paste
    # keyword = 'sepatu' Shoes
    keyword = input('Enter the keyword: ')
    access_token = input(f'Enter Access Token for keyword {keyword}:')
    # access_token = 'xLFfBV4K3zLf01rjiqqRcJkbDIzfcSdAu1g6wqk2E4G7hg'
    pages = int(input('Enter number of pages to scrape: '))

    headers_dict = {
        'origin': 'https://www.bukalapak.com',
        'referer': 'https://www.bukalapak.com/',
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
    }

    # List of product details in the form of dictionaries
    product_info_list = []

    get_data(headers_dict, access_token, pages)