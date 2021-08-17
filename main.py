import warnings
from concurrent.futures import ThreadPoolExecutor
from time import sleep

import pandas as pd
from requests_html import HTMLSession
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

warnings.filterwarnings("ignore")

private_label_conc = pd.read_excel("private_label_omzet.xlsx")
private_label_conc.head(2)





# ## Sanitairkamer

# Notes:
# - EAN niet weergegeven
# - Categorie niet te achterhalen vanuit productpagina


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

MAX_THREADS = 5


def visit_product_page_sanitairkamer(swnl, product_urls_sanitairkamer):
    threads = min(MAX_THREADS, len(product_urls_sanitairkamer))

    with ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(product_specs_sanitairkamer, swnl, product_urls_sanitairkamer)


def product_specs_sanitairkamer(sku, url):
    try:
        # starts session and 'visits' product page
        session = HTMLSession()
        response = session.get(url)

        row = []

        row.append(sku)

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
visit_product_page_sanitairkamer(swnl, product_urls_sanitairkamer)

sanitairkamer = pd.DataFrame(all_rows, columns=['sku', 'naam', 'art_nr_sanitairkamer', 'merk', 'serie', 'prijs'])
sanitairkamer['ean'] = [''] * len(sanitairkamer)
sanitairkamer['main_categorie'] = [''] * len(sanitairkamer)
sanitairkamer['sub_categorie'] = [''] * len(sanitairkamer)
sanitairkamer['levertijd'] = [''] * len(sanitairkamer)
sanitairkamer = sanitairkamer[
    ['sku', 'art_nr_sanitairkamer', 'ean', 'naam', 'merk', 'serie', 'main_categorie', 'sub_categorie', 'prijs',
     'levertijd']]
sanitairkamer

# ## X2O

x2o = private_label_conc[private_label_conc["x2o"] != "geen alternatief"]
product_urls_x2o = list(x2o["x2o"].dropna())
swnl = list(x2o["productcode_match"][:len(product_urls_x2o)])

driver = webdriver.PhantomJS()
driver = webdriver.Chrome()


# Function that waits till element is detected

def wait(selector, element):
    delay = 10
    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((selector, element)))
    except TimeoutException:
        print("wait Loading took too much time!")


all_rows = []
for sku, url in zip(swnl, product_urls_x2o):

    row = []

    row.append(sku)

    driver.get(url)

    wait(By.CLASS_NAME, "clamp-lines.name-root-2kk")
    try:
        name = driver.find_element_by_class_name("clamp-lines.name-root-2kk").text
    except:
        continue
    row.append(name)

    price = driver.find_element_by_class_name("price-mainPrice-2vj").text
    row.append(price)

    wait(By.CLASS_NAME, "breadcrumbs-root-1tN")
    sleep(0.5)
    cats = driver.find_element_by_class_name("breadcrumbs-root-1tN").text.split('> ')
    if len(cats) == 0:
        sleep(1)
        cats = driver.find_element_by_class_name("breadcrumbs-root-1tN").text.split('> ')

    if len(cats) > 3:
        main_cat = driver.find_element_by_class_name("breadcrumbs-root-1tN").text.split('> ')[1][:-1]
        sub_cat = driver.find_element_by_class_name("breadcrumbs-root-1tN").text.split('> ')[2][:-1]
    else:
        try:
            main_cat = driver.find_element_by_class_name("breadcrumbs-root-1tN").text.split('> ')[1][:-1]
        except:
            main_cat = ""
        sub_cat = ""

    row.append(main_cat)
    row.append(sub_cat)

    merk = driver.find_elements_by_xpath("//*[contains(@id,'Merk')]")[0].get_attribute('id').split('-')[1]
    row.append(merk)

    serie = driver.find_elements_by_xpath("//*[contains(@id,'Reeks')]")[0].get_attribute('id').split('-')[1]
    row.append(serie)

    EAN = driver.find_elements_by_xpath("//*[contains(@id,'Barcode')]")[0].get_attribute('id').split('-')[1]
    row.append(EAN)

    sku = driver.find_elements_by_xpath("//*[contains(@id,'WebSKU')]")[0].get_attribute('id').split('-')[1]
    row.append(sku)

    levertijd = driver.find_element_by_class_name("deliveryStatus-label-3ul").text
    row.append(levertijd)

    all_rows.append(row)

columns_x2o = ['sku', 'naam', 'prijs', 'main_categorie', 'sub_categorie', 'merk', 'serie', 'ean', 'art_nr_conc',
               'levertijd']
x2o = pd.DataFrame(all_rows, columns=columns_x2o)
x2o = x2o[
    ['sku', 'art_nr_conc', 'ean', 'naam', 'merk', 'serie', 'main_categorie', 'sub_categorie', 'prijs', 'levertijd']]
x2o['prijs'] = x2o['prijs'].str.replace('€ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
