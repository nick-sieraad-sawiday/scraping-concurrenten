import warnings
from datetime import datetime
from time import sleep

import pandas as pd

from src.maxaro import visit_product_page, start_session, add_to_all
from src.connections import get_data, write_excel

warnings.filterwarnings("ignore")

all_rows = []


def get_price_tegeldepot(response):
    """ Extracts the price from the product

    :param response: The connection with the website of the competitor
    :return: The price of the product of the competitor
    """
    try:
        price = response.html.find('.special-price')[0].text.split(' ')[1]
    except:
        try:
            price = response.html.find('.regular-price')[0].text
        except:
            price = response.html.find('.price-holder')[0].text.split(' ')[1]

    if '-' in price:
        price = float(price.replace(u'\xa0', u' ').replace('€ ', '').replace(',-', '.'))
    else:
        price = float(price.replace(u'\xa0', u' ').replace('.', '').replace('€ ', '').replace(',', '.'))

    return price


def product_specs_tegeldepot(sku: str, url: str):
    """ Extracts the specifications of the products of the competitor

    :param sku: Our sku
    :param url: The url of the alternative product of the competitor
    """
    try:
        # starts session and 'visits' product page
        response = start_session(url)

        row = [sku]

        product_name = response.html.find('.product-name')[0].text
        row.append(product_name)

        price = get_price_tegeldepot(response)
        row.append(price)

        cats = response.html.find('.breadcrumbs')[0].text.split('\n')
        if len(cats) > 3:
            main_cat = response.html.find('.breadcrumbs')[0].text.split('\n')[1]
            row.append(main_cat)

            sub_cat = response.html.find('.breadcrumbs')[0].text.split('\n')[2]
            row.append(sub_cat)

        if len(cats) == 3:
            main_cat = response.html.find('.breadcrumbs')[0].text.split('\n')[1]
            row.append(main_cat)

            sub_cat = response.html.find('.breadcrumbs')[0].text.split('\n')[2]
            row.append("")

        # product specs
        te = response.html.find('.specifications')[0].text.split('\n')
        if 'Artikelnummer (fabrikant)' in te:
            for t in range(len(te)):
                if te[t] == 'Artikelnummer (fabrikant)':
                    art_nr_fabrikant = te[t + 1]
                    row.append(art_nr_fabrikant)
        else:
            row.append("")

        if 'EAN' in te:
            for t in range(len(te)):
                if te[t] == 'EAN':
                    ean = te[t + 1]
                    if not ean.isdigit():
                        row.append("")
                    else:
                        row.append(int(ean))
        else:
            row.append("")

        if 'Merken' in te:
            for t in range(len(te)):
                if te[t] == 'Merken':
                    brand = te[t + 1]
                    row.append(brand)
        else:
            row.append("")

        if 'Serie' in te:
            for t in range(len(te)):
                if te[t] == 'Serie':
                    serie = te[t + 1]
                    row.append(serie)
        else:
            row.append("")

        row.append(url)

        all_rows.append(row)

    except:
        if response.status_code != 200:
            sleep(10)
        print(response.status_code)
        row = [sku, '', '', '', '', response.status_code, '', '', '', response.url]
        all_rows.append(row)


def create_dataframe(all_rows: list) -> pd.DataFrame:
    """ Creates a dataframe

    :param all_rows: The extracted products from the competitor
    :return: A dataframe that contains the product info of the competitor
    """
    tegeldepot = pd.DataFrame(all_rows,
                              columns=['sku', 'naam', 'prijs_tegeldepot', 'main_categorie', 'sub_categorie', 'art_nr_tegeldepot',
                                       'ean', 'merk', 'serie', 'url_tegeldepot'])
    tegeldepot['levertijd_tegeldepot'] = [''] * len(tegeldepot)
    tegeldepot["datum"] = datetime.today().date().strftime("%d-%m-%Y")
    tegeldepot = tegeldepot[
        ['sku', 'art_nr_tegeldepot', 'ean', 'naam', 'merk', 'serie', 'main_categorie', 'sub_categorie', 'prijs_tegeldepot',
         'levertijd_tegeldepot', 'url_tegeldepot', "datum"]
    ]

    return tegeldepot


def main(omnia):
    """ Main function

    Runs:
        - get_data
        - visit_product_page
        - create_dataframe
    """
    swnl, product_urls = get_data("tegeldepot")
    visit_product_page(5, swnl, product_urls, product_specs_tegeldepot)
    tegeldepot = create_dataframe(all_rows)
    tegeldepot = tegeldepot[["sku", "prijs_tegeldepot", "url_tegeldepot", "datum"]]
    tegeldepot = tegeldepot.merge(omnia, on="sku", how="left")
    tegeldepot.to_excel(
        "C:\\Users\\nick.sieraad\\Documents\\Projects\\scraping-concurrenten\\outputs\\tegeldepot.xlsx", index=False
    )


if __name__ == "__main__":
    main()
