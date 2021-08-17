import warnings
from time import sleep

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
warnings.filterwarnings("ignore")


def get_data():

    private_label_conc = pd.read_excel("private_label_omzet.xlsx")
    x2o = private_label_conc[private_label_conc["x2o"] != "geen alternatief"]
    product_urls_x2o = list(x2o["x2o"].dropna())
    swnl = list(x2o["productcode_match"][:len(product_urls_x2o)])

    return product_urls_x2o, swnl


def start_driver():

    driver = webdriver.PhantomJS()
    driver = webdriver.Chrome()

    return driver


def wait(driver, selector, element):
    """
    Function that waits till element is detected

    :param selector: The selector, e.g. by class_name
    :param element: The element that needs to be detected
    :return:
    """

    delay = 10
    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((selector, element)))
    except TimeoutException:
        print("wait Loading took too much time!")


def get_products(driver, swnl, product_urls_x2o):

    all_rows = []
    for sku, url in zip(swnl, product_urls_x2o):

        row = [sku]

        driver.get(url)

        wait(driver, By.CLASS_NAME, "clamp-lines.name-root-2kk")
        try:
            name = driver.find_element_by_class_name("clamp-lines.name-root-2kk").text
        except:
            continue
        row.append(name)

        price = driver.find_element_by_class_name("price-mainPrice-2vj").text
        row.append(price)

        wait(driver, By.CLASS_NAME, "breadcrumbs-root-1tN")
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

    return all_rows


def create_dataframe(all_rows):

    columns_x2o = ['sku', 'naam', 'prijs', 'main_categorie', 'sub_categorie', 'merk', 'serie', 'ean', 'art_nr_conc',
                   'levertijd']
    x2o = pd.DataFrame(all_rows, columns=columns_x2o)
    x2o = x2o[
        ['sku', 'art_nr_conc', 'ean', 'naam', 'merk', 'serie', 'main_categorie', 'sub_categorie', 'prijs', 'levertijd']]
    x2o['prijs'] = x2o['prijs'].str.replace('€ ', '').str.replace('.', '').str.replace(',', '.').astype(float)

    return x2o


def main():

    product_urls_x2o, swnl = get_data()
    driver = start_driver()
    all_rows = get_products(driver, swnl, product_urls_x2o)
    x2o = create_dataframe(all_rows)


if __name__ == "__main__":
    main()
