import warnings
from time import sleep

import pandas as pd
from src.maxaro import visit_product_page, start_session

warnings.filterwarnings("ignore")

private_label_conc = pd.read_excel("private_label_omzet.xlsx")
tegeldepot = private_label_conc[private_label_conc["tegeldepot"] != "geen alternatief"]
product_urls_tegeldepot = list(tegeldepot["tegeldepot"].dropna())
swnl = list(tegeldepot["productcode_match"][:len(product_urls_tegeldepot)])


def get_price_tegeldepot(response):
    try:
        price = response.html.find('.special-price')[0].text.split(' ')[1]
    except:
        price = response.html.find('.regular-price')[0].text

    if '-' in price:
        price = float(price.replace(u'\xa0', u' ').replace('€ ', '').replace(',-', '.'))
    else:
        price = float(price.replace(u'\xa0', u' ').replace('€ ', '').replace(',', '.'))

    return price


def product_specs_tegeldepot(sku, url):
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

        all_rows.append(row)

    except:
        if response.status_code != 200:
            sleep(10)
        print(response.status_code)
        row = [response.status_code, '', '', '', '', '', response.url]
        all_rows.append(row)


all_rows = []
# visits the product pages
visit_product_page(5, swnl, product_urls_tegeldepot, product_specs_tegeldepot)

tegeldepot = pd.DataFrame(all_rows,
                          columns=['sku', 'naam', 'prijs', 'main_categorie', 'sub_categorie', 'art_nr_tegeldepot',
                                   'ean', 'merk', 'serie'])
tegeldepot['levertijd'] = [''] * len(tegeldepot)
tegeldepot = tegeldepot[
    ['sku', 'art_nr_tegeldepot', 'ean', 'naam', 'merk', 'serie', 'main_categorie', 'sub_categorie', 'prijs',
     'levertijd']]
