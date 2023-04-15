import requests
from lxml import html
import pandas as pd

headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
    }

url = 'https://www.indiamart.com/multidimensions/electricals-mechanical-products.html'

res = requests.get(url, headers=headers)
tree = html.fromstring(res.text)

# For block-wise picking product - Won't mismatch the data
prod_block_xp = tree.xpath("//div[contains(@class, 'FM_m9')]//h3[contains(@class, 'FM_c1')]")

prod_info_list = []
# append the list of Product data in dictionary format
for count, product in enumerate(prod_block_xp):
    prod_title = prod_link = prod_img_link = ''
    home_url = 'https://www.indiamart.com/multidimensions/'

    prod_title_xp1 = tree.xpath("//div[contains(@class, 'FM_m9')]//h3[contains(@class, 'FM_c1')]/a/text()")
    prod_link_xp1 = tree.xpath("//div[contains(@class, 'FM_m9')]//h3[contains(@class, 'FM_c1')]/a/@href")
    prod_img_link_xp1 = tree.xpath("//div[contains(@class, 'FM_m9')]//div[contains(@class, 'main_img-1')]//a[@class='FM_ds5 FM_ds7']/img/@data-dataimg")

    if prod_title_xp1:
        prod_title = prod_title_xp1[count].strip()
    if prod_link_xp1:
        prod_link = home_url + prod_link_xp1[count].strip()
    if prod_img_link_xp1:
        prod_img_link = prod_img_link_xp1[count].strip()

    prod_info_list.append({
        'Product_Title': prod_title,
        'Product_Link': prod_link,
        'Product_Image_Link': prod_img_link
    })

# Store it into csv
file_name = 'Indiamart_electricals-mechanical-products.csv'
pd.DataFrame(prod_info_list).to_csv(file_name, index=False)
print(f"Successfully save {file_name}")