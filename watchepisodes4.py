import requests
#import urllib3
from bs4 import BeautifulSoup
import pandas as pd


def get_last_page(url):
    '''
    Get the last page from website www.watchepisodes4.com

    Parameters
    ----------
    url : str
        url of the website www.watchepisodes4.com

    Returns
    --------
    last_page : int
        Return last page number from website www.watchepisodes4.com
    '''
    html_text = requests.get(url)
    soup = BeautifulSoup(html_text.content, 'html.parser')
    last_page = soup.find('div', {'class': 'general-navigation'}).find_all('a')[-1].text

    return int(last_page)


def get_watchepisodes4_info(last_page):
    '''
    Return a list of Series info in the form of dictionaries

    Parameters
    ----------
    last_page : int
        last page of the the website

    Returns
    -------
    List
        return a list of Series info in the form of dictionaries
    '''
    for page_no in range(1,last_page+1):
        dynamic_url = f'https://www.watchepisodes4.com/home/series/page/{page_no}'
        dynamic_html_text = requests.get(dynamic_url)

        soup = BeautifulSoup(dynamic_html_text.content, 'html.parser')

        print(f"Fetching data for page : {page_no}")
        series_info = soup.find('div', {'class': 'wide-list'}).find_all('div', {'class': 'wide-box'})

        for series in series_info:
            series_name = series.find('h3', {'class': 'wb-name'}).find('a').text
            series_hyperlink = series.find('h3', {'class': 'wb-name'}).find('a').get('href')

            # append the list of Series data in dictionary format
            list_series_info.append({
                        'Series Name': series_name,
                        'Series Link': series_hyperlink
                    })

    return list_series_info


if __name__ == '__main__':
    #list of dictionaries used to store data as key value pair
    list_series_info = []
    url = 'https://www.watchepisodes4.com/home/series/page/'

    last_page = get_last_page(url)
    list_series_info = get_watchepisodes4_info(last_page)

    pd.DataFrame(list_series_info).to_excel('list_of_series_info.xls')
