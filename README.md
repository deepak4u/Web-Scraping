## Web-Scraping Projects using Python

This repository contains multiple Python scripts for web scraping different websites to extract data related to products. The scripts utilize various libraries such as Requests, Beautiful Soup, Selenium, lxml, api, json to crawl and extract data from the following websites:
<br><br>

|Site | Notebook | Description
|--|:--:|--|
| www.imdb.com |[🔗](https://github.com/deepak4u/Web-Scraping/blob/main/Notebooks/IMDB%20Search%20and%20crawl%20metadata.ipynb) | Imdb series/movie metadata search and crawl using requests. <br>**Params:** title, type, genres, languages, runtime, YearRange, originalTitleText, total_episodes.
| www.amazon.com |[🔗](https://github.com/deepak4u/Web-Scraping/blob/main/Notebooks/Amazon.com_product_and_seller_scrape.ipynb) | Extracts products info from product page url along with it's sellers info using requests. <br>**Params:** product name, no_of_offers, old_price, new_price, amazon flags, ratings, etc.
| www.amazon.ae <br> www.amazon.eg <br> www.amazon.sa |[🔗](https://github.com/deepak4u/Web-Scraping/blob/main/Notebooks/Amazon_Category_Crawl_Final.py)
<br><br><br>[🔗](https://github.com/deepak4u/Web-Scraping/blob/main/Notebooks/amazon_category_crawl_product_detail_final.py)
| Amazon Category crawl with different level of mapping. <br>**Params:** cat_level_name (breadcrumbs style store), cat_level_url, etc.
| www.apoteket.se |[🔗](https://github.com/deepak4u/Web-Scraping/blob/main/Notebooks/apoteket%20-%20json%20data%20with%20payload.ipynb) | Extracts searched products data from Apoteket using requests with a payload in JSON format. <br>**Params:** product names, prices, and it's link.
| www.netflix.com |[🔗](https://github.com/deepak4u/Web-Scraping/blob/main/Notebooks/Netflix%20program%20id%20scrape%20using%20Selenium%20and%20MongoDB%20store.ipynb)<br><br><br>[🔗](https://github.com/deepak4u/Web-Scraping/blob/main/Notebooks/Netflix%20series%20data%20crawl%20from%20link.ipynb) | Netflix program id scrape using Selenium and Stored into MongoDb.<br>**Params:** program_id, program_name, program_url. <br><br> Extracts Netflix series info from series url. <br>**Params:** program_name, season_no, episode_no, episode_name, episode_runtime, etc.
| www.bukalapak.com |[🔗](https://github.com/deepak4u/Web-Scraping/blob/main/Notebooks/bukalapak_search_and_scrape_product_info.py) | Search and Extracts products info from Multiple Pages with Customizable Page Limit. <br>**Params:** Product Name, Product Link, Product Price.
| www.watchepisodes4.com |[🔗](https://github.com/deepak4u/Web-Scraping/blob/main/Notebooks/watchepisodes4.py) | Extracts Series info data using Beautiful Soup. <br>**Params:** series name, and it's link.

