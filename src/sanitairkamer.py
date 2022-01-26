import warnings
from datetime import datetime
from time import sleep

import pandas as pd
from src.maxaro import visit_product_page, start_session
from src.connections import get_data

warnings.filterwarnings("ignore")

all_rows = []


def get_price_sanitairkamer(response) -> float:
    """ Extracts the price from the product

    :param response: The connection with the website of the competitor
    :return: The price of the product of the competitor
    """
    price = float(response.html.xpath("//span[@itemprop='price']/@content")[0])

    return price


def product_specs_sanitairkamer(sku, url):
    """ Extracts the specifications of the products of the competitor

    :param sku: Our sku
    :param url: The url of the alternative product of the competitor
    """

    try:
        # starts session and 'visits' product page
        response = start_session(url)

        row = [sku]

        name = response.html.find('.product-page__title')[0].text.split("\nArtikelnummer: ")[0]
        row.append(name)
        print(name)

        # product specs
        te = response.html.find('.additional-attributes-wrapper')[0].text.split('\n')
        if 'Artikelnummer' in te:
            for t in range(len(te)):
                if te[t] == 'Artikelnummer':
                    art_nr_fabrikant = te[t + 1]
                    row.append(art_nr_fabrikant)
        else:
            row.append("")

        if 'Merk' in te:
            for t in range(len(te)):
                if te[t] == 'Merk':
                    merk = te[t + 1]
                    row.append(merk)
        else:
            row.append("")

        if 'Serie' in te:
            for t in range(len(te)):
                if te[t] == 'Serie':
                    serie = te[t + 1]
                    row.append(serie)
        else:
            row.append("")

        price = get_price_sanitairkamer(response)
        row.append(price)

        row.append(url)

        all_rows.append(row)

    except:
        if response.status_code != 200:
            sleep(10)
        print(response.status_code, response.url)
        row = [response.status_code, '', '', '', '', response.url]
        all_rows.append(row)


def create_dataframe(all_rows: list) -> pd.DataFrame:
    """ Creates a dataframe

    :param all_rows: The extracted products from the competitor
    :return: A dataframe that contains the product info of the competitor
    """
    sanitairkamer = pd.DataFrame(
        all_rows, columns=['sku', 'naam', 'art_nr_sanitairkamer', 'merk', 'serie', 'prijs_sanitairkamer',
                           'url_sanitairkamer']
    )
    sanitairkamer['ean'] = [''] * len(sanitairkamer)
    sanitairkamer['main_categorie'] = [''] * len(sanitairkamer)
    sanitairkamer['sub_categorie'] = [''] * len(sanitairkamer)
    sanitairkamer['levertijd_sanitairkamer'] = [''] * len(sanitairkamer)
    sanitairkamer["datum"] = datetime.today().date().strftime("%d-%m-%Y")
    sanitairkamer = sanitairkamer[
        ['sku', 'art_nr_sanitairkamer', 'ean', 'naam', 'merk', 'serie', 'main_categorie', 'sub_categorie',
         'prijs_sanitairkamer', 'levertijd_sanitairkamer', 'url_sanitairkamer', "datum"]
    ]

    return sanitairkamer


def main(omnia):
    """ Main function

    Runs:
        - get_data
        - visit_product_page
        - create_dataframe
    """
    swnl, product_urls = get_data("sanitairkamer")
    visit_product_page(5, swnl, product_urls, product_specs_sanitairkamer)
    sanitairkamer = create_dataframe(all_rows)
    sanitairkamer = sanitairkamer[["sku", "prijs_sanitairkamer", "url_sanitairkamer", "datum"]]
    sanitairkamer = sanitairkamer.merge(omnia, on="sku", how="left")
    sanitairkamer.to_excel(
        "C:\\Users\\nick.sieraad\\Documents\\Projects\\scraping-concurrenten\\outputs\\sanitairkamer.xlsx", index=False
    )


if __name__ == "__main__":
    main()
