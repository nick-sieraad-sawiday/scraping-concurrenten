from concurrent.futures import ThreadPoolExecutor
from time import sleep

import pandas as pd
from requests_html import HTMLSession


private_label_conc = pd.read_excel("private_label_omzet.xlsx")
maxaro = private_label_conc[private_label_conc["maxaro"] != "geen alternatief"]
product_urls_maxaro = list(maxaro["maxaro"].dropna())
swnl = list(maxaro["productcode_match"][:len(product_urls_maxaro)])


def get_price_maxaro(response):
    price = response.html.find('.product-detail-pricing')[0].text

    if '-' in price:
        price = float(price.replace('-', '').replace(',', ''))
    else:
        price = float(price.replace(',', '.'))

    return price


def visit_product_page(max_threads, swnl, product_urls, product_specs):
    threads = min(max_threads, len(product_urls))

    with ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(product_specs, swnl, product_urls)


def start_session(url):
    session = HTMLSession()
    response = session.get(url)

    return response


def product_specs_maxaro(sku, url):
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

        all_rows.append(row)

    except:
        if response.status_code != 200:
            sleep(10)
        print(response.status_code)
        row = [response.status_code, '', '', '', '', '', response.url]
        all_rows.append(row)


all_rows = []
visit_product_page(5, swnl, product_urls_maxaro, product_specs_maxaro)

maxaro = pd.DataFrame(all_rows, columns=['sku', 'art_nr_maxaro', 'naam', 'main_categorie', 'sub_categorie', 'prijs'])
maxaro['ean'] = [''] * len(maxaro)
maxaro['merk'] = ['Maxaro'] * len(maxaro)
maxaro['serie'] = [''] * len(maxaro)
maxaro['levertijd'] = [''] * len(maxaro)
maxaro = maxaro[
    ['sku', 'art_nr_maxaro', 'ean', 'naam', 'merk', 'serie', 'main_categorie', 'sub_categorie', 'prijs', 'levertijd']]
