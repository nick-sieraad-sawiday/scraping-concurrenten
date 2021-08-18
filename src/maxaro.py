import warnings
from concurrent.futures import ThreadPoolExecutor
from time import sleep

import pandas as pd
from requests_html import HTMLSession
from src.connections import get_data

warnings.filterwarnings("ignore")

all_rows = []


def get_price_maxaro(response) -> float:
    """ Extracts the price from the product

    :param response: The connection with the website of the competitor
    :return: The price of the product of the competitor
    """
    price = response.html.find('.product-detail-pricing')[0].text

    if '-' in price:
        price = float(price.replace('-', '').replace(',', ''))
    else:
        price = float(price.replace(',', '.'))

    return price


def visit_product_page(max_threads: int, swnl: list, product_urls: list, product_specs):
    """ Runs function simultaneously

    :param max_threads: The maximum amount of threads
    :param swnl: List with our sku's
    :param product_urls: List with the url's of the products of the competitor
    :param product_specs: The function that scrapes the competitor
    """
    threads = min(max_threads, len(product_urls))

    with ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(product_specs, swnl, product_urls)


def start_session(url: str):
    """ Starts a session with the website of the competitor

    :param url: The url of the website of the competitor
    :return: The connection with the website of the competitor
    """
    session = HTMLSession()
    response = session.get(url)

    return response


def product_specs_maxaro(sku: str, url: str):
    """ Extracts the specifications of the products of the competitor

    :param sku: Our sku
    :param url: The url of the alternative product of the competitor
    """
    try:
        # starts session and 'visits' product page
        response = start_session(url)

        row = [sku]

        art_nr = response.html.find('.product-header__sub')[0].text
        row.append(art_nr)

        name = response.html.find('.product-header__title')[0].text
        row.append(name)

        main_category = url.split('/')[3]
        row.append(main_category)
        sub_category = url.split('/')[4]
        row.append(sub_category)

        price = get_price_maxaro(response)
        row.append(price)

        row.append(url)

        all_rows.append(row)

    except:
        if response.status_code != 200:
            sleep(10)
        print(response.status_code)
        row = [sku, response.status_code, '', '', '', '', response.url]
        all_rows.append(row)


def create_dataframe(all_rows: list) -> pd.DataFrame:
    """ Creates a dataframe

    :param all_rows: The extracted products from the competitor
    :return: A dataframe that contains the product info of the competitor
    """
    maxaro = pd.DataFrame(
        all_rows, columns=['sku', 'art_nr_maxaro', 'naam', 'main_categorie', 'sub_categorie', 'prijs', 'url']
    )
    maxaro['ean'] = [''] * len(maxaro)
    maxaro['merk'] = ['Maxaro'] * len(maxaro)
    maxaro['serie'] = [''] * len(maxaro)
    maxaro['levertijd'] = [''] * len(maxaro)
    maxaro = maxaro[
        ['sku', 'art_nr_maxaro', 'ean', 'naam', 'merk', 'serie', 'main_categorie',
         'sub_categorie', 'prijs', 'levertijd', 'url']
    ]

    return maxaro


def main():
    """ Main function

    Runs:
        - get_data
        - visit_product_page
        - create_dataframe
    """
    swnl, product_urls = get_data("maxaro")
    visit_product_page(5, swnl, product_urls, product_specs_maxaro)
    maxaro = create_dataframe(all_rows)
    maxaro.to_excel(
        "C:\\Users\\nick.sieraad\\Documents\\Projects\\scraping-concurrenten\\outputs\\maxaro.xlsx", index=False
    )


if __name__ == "__main__":
    main()
