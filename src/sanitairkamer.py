import warnings
from time import sleep

import pandas as pd
from src.maxaro import visit_product_page, start_session
warnings.filterwarnings("ignore")

private_label_conc = pd.read_excel("private_label_omzet.xlsx")
sanitairkamer = private_label_conc[private_label_conc["sanitairkamer"] != "geen alternatief"]
product_urls_sanitairkamer = list(sanitairkamer["sanitairkamer"].dropna())
swnl = list(sanitairkamer["productcode_match"][:len(product_urls_sanitairkamer)])


def get_price_sanitairkamer(response):
    try:
        price = response.html.find('.minimal-price')[0].text.split(' ')[1]
    except:
        try:
            price = response.html.find('.regular-price')[0].text
        except:
            price = response.html.find('.special-price')[0].text.split(' ')[1]

    if '-' in price:
        price = float(price.replace(u'\xa0', u' ').replace('€ ', '').replace('.', '').replace(',-', '.'))
    else:
        price = float(price.replace(u'\xa0', u' ').replace('€ ', '').replace('.', '').replace(',', '.'))

    return price


def product_specs_sanitairkamer(sku, url):
    try:
        # starts session and 'visits' product page
        response = start_session(url)

        row = [sku]

        name = response.html.find('.product-name')[0].text
        row.append(name)

        # product specs
        te = response.html.find('.data-table')[0].text.split('\n')
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

        all_rows.append(row)

    except:
        if response.status_code != 200:
            sleep(10)
        print(response.status_code)
        row = [response.status_code, '', '', '', '', response.url]
        all_rows.append(row)


all_rows = []
visit_product_page(5, swnl, product_urls_sanitairkamer, product_specs_sanitairkamer)

sanitairkamer = pd.DataFrame(all_rows, columns=['sku', 'naam', 'art_nr_sanitairkamer', 'merk', 'serie', 'prijs'])
sanitairkamer['ean'] = [''] * len(sanitairkamer)
sanitairkamer['main_categorie'] = [''] * len(sanitairkamer)
sanitairkamer['sub_categorie'] = [''] * len(sanitairkamer)
sanitairkamer['levertijd'] = [''] * len(sanitairkamer)
sanitairkamer = sanitairkamer[
    ['sku', 'art_nr_sanitairkamer', 'ean', 'naam', 'merk', 'serie', 'main_categorie', 'sub_categorie', 'prijs',
     'levertijd']]
