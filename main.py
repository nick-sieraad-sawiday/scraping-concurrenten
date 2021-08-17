import csv
from time import sleep
import datetime
from datetime import date
import pandas as pd
import time
import sys
import glob
import requests
from concurrent.futures import ThreadPoolExecutor
from requests import session
from requests_html import HTMLSession
from functools import reduce
import math
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
import warnings
warnings.filterwarnings("ignore")


# ## Private labels

# In[54]:


private_label_conc = pd.read_excel("private_label_omzet.xlsx")
private_label_conc.head(2)


# ## Maxaro

# Notes: 
# - Serie kan niet gescraped worden (javascript)
# - EAN weergeven ze niet

# In[57]:


maxaro = private_label_conc[private_label_conc["maxaro"] != "geen alternatief"]
product_urls_maxaro = list(maxaro["maxaro"].dropna())
swnl = list(maxaro["productcode_match"][:len(product_urls_maxaro)])


# In[58]:


def get_price_maxaro(response):

    price = response.html.find('.product-detail-pricing')[0].text

    if '-' in price:
        price = float(price.replace('-', '').replace(',', ''))
    else:
        price = float(price.replace(',', '.'))
    
    return price


# In[69]:


MAX_THREADS = 5
def visit_product_page_maxaro(swnl, product_urls_maxaro):
    threads = min(MAX_THREADS, len(product_urls_maxaro))
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(product_specs_maxaro, swnl, product_urls_maxaro)


# In[70]:


def product_specs_maxaro(sku, url):
    try:
        # starts session and 'visits' product page
        session = HTMLSession()
        response = session.get(url)
        
        row = []
        
        row.append(sku)

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
        print(response.status_code, e)
        row = [response.status_code, '', '', '', '', '', response.url]
        all_rows.append(row)


# In[72]:


all_rows = []
visit_product_page_maxaro(swnl, product_urls_maxaro)


# In[74]:


maxaro = pd.DataFrame(all_rows, columns=['sku', 'art_nr_maxaro', 'naam', 'main_categorie', 'sub_categorie', 'prijs'])
maxaro['ean'] = [''] * len(maxaro)
maxaro['merk'] = ['Maxaro'] * len(maxaro)
maxaro['serie'] = [''] * len(maxaro)
maxaro['levertijd'] = [''] * len(maxaro)
maxaro = maxaro[['sku', 'art_nr_maxaro', 'ean', 'naam', 'merk', 'serie', 'main_categorie', 'sub_categorie', 'prijs', 'levertijd']]
maxaro


# ## Tegeldepot

# In[81]:


tegeldepot = private_label_conc[private_label_conc["tegeldepot"] != "geen alternatief"]
product_urls_tegeldepot = list(tegeldepot["tegeldepot"].dropna())
swnl = list(tegeldepot["productcode_match"][:len(product_urls_x2o)])


# In[82]:


def get_price_tegeldepot(response):

    try:
        price = response.html.find('.special-price')[0].text.split(' ')[1]
    except:
        price = response.html.find('.regular-price')[0].text
        
    if '-' in price:
        price = float(price.replace(u'\xa0', u' ').replace('€ ', '').replace(',-','.'))
    else:
        price = float(price.replace(u'\xa0', u' ').replace('€ ', '').replace(',','.'))
    
    return price


# In[83]:


MAX_THREADS = 5
def visit_product_page_tegeldepot(swnl, product_urls_tegeldepot):
    threads = min(MAX_THREADS, len(product_urls_tegeldepot))
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(product_specs_tegeldepot, swnl, product_urls_tegeldepot)


# In[84]:


def product_specs_tegeldepot(sku, url):

    try:
        # starts session and 'visits' product page
        session = HTMLSession()
        response = session.get(url)
        
        row = []
        
        row.append(sku)
        
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
                    art_nr_fabrikant = te[t+1]
                    row.append(art_nr_fabrikant)
        else:
            row.append("")

        if 'EAN' in te:
            for t in range(len(te)):
                if te[t] == 'EAN':
                    EAN = te[t+1]
                    if EAN.isdigit() == False:
                        row.append("")
                    else:
                        row.append(int(EAN))              
        else:
            row.append("")

        if 'Merken' in te:
            for t in range(len(te)):
                if te[t] == 'Merken':
                    brand = te[t+1]
                    row.append(brand)
        else:
            row.append("")

        if 'Serie' in te:
            for t in range(len(te)):
                if te[t] == 'Serie':
                    serie = te[t+1]
                    row.append(serie)
        else:
            row.append("")  
            
        all_rows.append(row)
            
    except:
        if response.status_code != 200: 
            sleep(10)
        print(response.status_code, e)
        row = [response.status_code, '', '', '', '', '', response.url]
        all_rows.append(row)


# In[86]:


all_rows = []
# visits the product pages
visit_product_page_tegeldepot(swnl, product_urls_tegeldepot)


# In[87]:


tegeldepot = pd.DataFrame(all_rows, columns=['sku', 'naam', 'prijs', 'main_categorie', 'sub_categorie', 'art_nr_tegeldepot', 'ean', 'merk', 'serie'])
tegeldepot['levertijd'] = [''] * len(tegeldepot)
tegeldepot = tegeldepot[['sku', 'art_nr_tegeldepot', 'ean', 'naam', 'merk', 'serie', 'main_categorie', 'sub_categorie', 'prijs', 'levertijd']]
tegeldepot


# ## Sanitairkamer

# Notes:
# - EAN niet weergegeven
# - Categorie niet te achterhalen vanuit productpagina

# In[89]:


sanitairkamer = private_label_conc[private_label_conc["sanitairkamer"] != "geen alternatief"]
product_urls_sanitairkamer = list(sanitairkamer["sanitairkamer"].dropna())
swnl = list(sanitairkamer["productcode_match"][:len(product_urls_sanitairkamer)])


# In[90]:


def get_price_sanitairkamer(response):

    try:
        price = response.html.find('.minimal-price')[0].text.split(' ')[1]
    except:
        try:
            price = response.html.find('.regular-price')[0].text
        except:
            price = response.html.find('.special-price')[0].text.split(' ')[1]
        
    if '-' in price:
        price = float(price.replace(u'\xa0', u' ').replace('€ ', '').replace('.','').replace(',-','.'))
    else:
        price = float(price.replace(u'\xa0', u' ').replace('€ ', '').replace('.','').replace(',','.'))
    
    return price


# In[95]:


MAX_THREADS = 5
def visit_product_page_sanitairkamer(swnl, product_urls_sanitairkamer):
    threads = min(MAX_THREADS, len(product_urls_sanitairkamer))
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(product_specs_sanitairkamer, swnl, product_urls_sanitairkamer)


# In[96]:


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
                    art_nr_fabrikant = te[t+1]
                    row.append(art_nr_fabrikant)
        else:
            row.append("")

        if 'Merk' in te:
            for t in range(len(te)):
                if te[t] == 'Merk':
                    merk = te[t+1]
                    row.append(merk)
        else:
            row.append("")
            
        if 'Serie' in te:
            for t in range(len(te)):
                if te[t] == 'Serie':
                    serie = te[t+1]
                    row.append(serie)
        else:
            row.append("")

        price = get_price_sanitairkamer(response)
        row.append(price)
        
        all_rows.append(row)
        
    except:
        if response.status_code != 200: 
            sleep(10)
        print(response.status_code, e)
        row = [response.status_code, '', '', '', '', response.url]
        all_rows.append(row)


# In[97]:


all_rows = []
visit_product_page_sanitairkamer(swnl, product_urls_sanitairkamer)


# In[98]:


sanitairkamer = pd.DataFrame(all_rows, columns=['sku', 'naam', 'art_nr_sanitairkamer', 'merk', 'serie', 'prijs'])
sanitairkamer['ean'] = [''] * len(sanitairkamer)
sanitairkamer['main_categorie'] = [''] * len(sanitairkamer)
sanitairkamer['sub_categorie'] = [''] * len(sanitairkamer)
sanitairkamer['levertijd'] = [''] * len(sanitairkamer)
sanitairkamer = sanitairkamer[['sku', 'art_nr_sanitairkamer', 'ean', 'naam', 'merk', 'serie', 'main_categorie', 'sub_categorie', 'prijs', 'levertijd']]
sanitairkamer


# ## X2O

# In[29]:


x2o = private_label_conc[private_label_conc["x2o"] != "geen alternatief"]
product_urls_x2o = list(x2o["x2o"].dropna())
swnl = list(x2o["productcode_match"][:len(product_urls_x2o)])


# In[46]:


driver = webdriver.PhantomJS()
driver = webdriver.Chrome()


# In[47]:


# Function that waits till element is detected

def wait(selector, element):
    delay = 10
    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((selector, element)))
    except TimeoutException:
        print("wait Loading took too much time!")


# In[48]:


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


# In[52]:


columns_x2o = ['sku', 'naam', 'prijs', 'main_categorie', 'sub_categorie', 'merk', 'serie', 'ean', 'art_nr_conc', 'levertijd']
x2o = pd.DataFrame(all_rows, columns=columns_x2o)
x2o = x2o[['sku', 'art_nr_conc', 'ean', 'naam', 'merk', 'serie', 'main_categorie', 'sub_categorie', 'prijs', 'levertijd']]
x2o['prijs'] = x2o['prijs'].str.replace('€ ', '').str.replace('.','').str.replace(',','.').astype(float)
x2o


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




