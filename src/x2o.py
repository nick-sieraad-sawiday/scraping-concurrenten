import warnings
from datetime import datetime
from time import sleep

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.connections import get_data

warnings.filterwarnings("ignore")


def start_driver() -> webdriver.Chrome:
    """ Starts the driver that visits the pages

    :return: The driver
    """
    # driver = webdriver.PhantomJS()
    driver = webdriver.Chrome(
        "C:\\Users\\nick.sieraad\\Documents\\Projects\\scraping-concurrenten\\executables\\chromedriver.exe"
    )

    return driver


def wait(driver, selector, element: str):
    """ Function that waits till element is detected

    :param driver: The driver that visits the pages
    :param selector: The selector, e.g. by class_name
    :param element: The element that needs to be detected
    :return:
    """

    delay = 10
    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((selector, element)))
    except TimeoutException:
        print("wait Loading took too much time!")


def get_products_x2o(driver, swnl: list, product_urls_x2o: list) -> list:
    """ Extracts the specifications of the products of the competitor

    :param driver: The driver that visits the pages
    :param swnl: List with our sku's
    :param product_urls_x2o: List with the url's of the products of the competitor
    :return: List with all the products of the competitor
    """

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

        brand = driver.find_elements_by_xpath("//*[contains(@id,'Merk')]")[0].get_attribute('id').split('-')[1]
        row.append(brand)

        serie = driver.find_elements_by_xpath("//*[contains(@id,'Reeks')]")[0].get_attribute('id').split('-')[1]
        row.append(serie)

        ean = driver.find_elements_by_xpath("//*[contains(@id,'Barcode')]")[0].get_attribute('id').split('-')[1]
        row.append(ean)

        sku = driver.find_elements_by_xpath("//*[contains(@id,'WebSKU')]")[0].get_attribute('id').split('-')[1]
        row.append(sku)

        delivery_time = driver.find_element_by_class_name("deliveryStatus-label-3ul").text
        row.append(delivery_time)

        row.append(url)

        all_rows.append(row)

    return all_rows


def create_dataframe(all_rows: list) -> pd.DataFrame:
    columns_x2o = ['sku', 'naam', 'prijs_x2o', 'main_categorie', 'sub_categorie', 'merk', 'serie', 'ean', 'art_nr_conc',
                   'levertijd_x2o', 'url_x2o']
    x2o = pd.DataFrame(all_rows, columns=columns_x2o)
    x2o["datum"] = datetime.today().date().strftime("%d-%m-%Y")
    x2o = x2o[
        ['sku', 'art_nr_conc', 'ean', 'naam', 'merk', 'serie', 'main_categorie', 'sub_categorie',
         'prijs_x2o', 'levertijd_x2o', 'url_x2o', "datum"]
    ]
    x2o = x2o[x2o['prijs_x2o'] != ""]
    x2o['prijs_x2o'] = x2o['prijs_x2o'].str.replace('€ ', '').str.replace('.', '').str.replace(',', '.').astype(float)

    return x2o


def main(omnia):
    """ Main function

    Runs:
        - get_data
        - visit_product_page
        - create_dataframe
    """
    swnl, product_urls_x2o = get_data("x2o")
    driver = start_driver()
    all_rows = get_products_x2o(driver, swnl, product_urls_x2o)
    x2o = create_dataframe(all_rows)
    x2o = x2o[["sku", "prijs_x2o", "url_x2o", "datum"]]
    x2o = x2o.merge(omnia, on="sku", how="left")
    x2o.to_excel(
        "C:\\Users\\nick.sieraad\\Documents\\Projects\\scraping-concurrenten\\outputs\\x2o.xlsx", index=False
    )


if __name__ == "__main__":
    main()
