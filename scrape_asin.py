import time
import sqlite3
import urllib.parse
# import pandas as pd
from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options


conn = sqlite3.connect('Amazon.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS Amazon_products (EAN text PRIMARY KEY, ASIN text, Price text,date_time text )''')
conn = sqlite3.connect('data//data.db')
c = conn.cursor()
conn.commit()
conn.close()

# c.execute('CREATE TABLE Alledaten_new (EAN_GTIN TEXT, other_column TEXT)')
EAN_list = []
conn = sqlite3.connect('data//data.db')
c = conn.cursor()
c.execute('SELECT DISTINCT "EAN/GTIN" FROM Alledaten WHERE "EAN/GTIN" IS NOT NULL ORDER BY 1 DESC')
rows = c.fetchall()
for row in rows:
    EAN_list.append(row[0])
# set_list = set(EAN_list)
# EAN_list = list(set_list) 
    
conn.close()
def getLastEAN():
    conn = sqlite3.connect('Amazon.db')
    c = conn.cursor()
    c.execute(f"SELECT * FROM Amazon_products ORDER BY date_time  DESC LIMIT 1")
    result = c.fetchall()
    conn.commit()
    conn.close()
    return result
    
def link_Transform(link):
    parsed_url = urllib.parse.urlparse(link)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    amazon_url = query_params['url'][0]
    decoded_amazon_url = urllib.parse.unquote(amazon_url)
    starter_url = 'https://www.amazon.de'
    final_url = starter_url + decoded_amazon_url
    return final_url
    
def get_ASIN(link):
    driver.get(link)
    try:
        button = driver.find_element(By.ID, 'sp-cc-accept')
        if button:
            button.click()
    except NoSuchElementException:
        pass
    parent_ASIN = driver.find_element(By.ID, 'productDetails_detailBullets_sections1')
    child1 = parent_ASIN.find_element(By.CSS_SELECTOR, ".a-size-base.prodDetAttrValue")
    text = child1.text
    return text


def saveToDB(EAN, ASIN, PRICE, datetime):
    conn = sqlite3.connect('Amazon.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO Amazon_products (EAN,ASIN, Price, date_time) VALUES (?, ?, ?, ?)", (EAN,ASIN, PRICE, datetime))
    conn.commit()
    conn.close()



result = getLastEAN()
if not result:
    current_time = datetime.now()
    saveToDB(EAN_list[0], '', '',current_time)
    result = getLastEAN()

current_EAN = EAN_list.index(result[0][0])
print(result[0][0])
print(current_EAN)
for i in  range(current_EAN, len(EAN_list)):
    EAN = EAN_list[i]
    try:
        options = Options()
        options.headless = False
        driver = webdriver.Firefox(options=options)
        driver.get(f'https://www.amazon.de/s?k={EAN}')
        try:
            button = driver.find_element(By.ID, 'sp-cc-accept')
            if button:
                button.click()
        except NoSuchElementException:
            pass
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.s-main-slot.s-result-list.s-search-results.sg-row')))
            divs = driver.find_elements(By.CSS_SELECTOR, '.s-main-slot.s-result-list.s-search-results.sg-row')

            if len(divs) == 1:
                try:
                    no_result = driver.find_element(By.CSS_SELECTOR, '.sg-col-inner')
                    no_result1 = no_result.find_element(By.CSS_SELECTOR, '.a-section.a-spacing-none.s-result-item.s-flex-full-width.s-border-bottom-none.s-widget.s-widget-spacing-large')
                    no_result2 = no_result1.find_element(By.CSS_SELECTOR, '.s-no-outline')
                    no_result3 = no_result2.find_element(By.CSS_SELECTOR, '.a-row')
                    all_components = no_result3.find_elements(By.CSS_SELECTOR, '.a-size-medium.a-color-base')
                    print(all_components)
                    for component in all_components:
                        text = component.text
                        if text == "Keine Ergebnisse für":
                            continue

                except:
                    pass


            try:
                child_elements = divs[0].find_elements(By.CSS_SELECTOR, '.sg-col-4-of-24.sg-col-4-of-12.s-result-item.s-asin.sg-col-4-of-16.AdHolder.sg-col.s-widget-spacing-small.sg-col-4-of-20')

                if len(child_elements)>1:
                    for i, current in enumerate(child_elements):
                        child1 = current.find_element(By.CSS_SELECTOR, '.sg-col-inner')
                        child2 = child1.find_element(By.CSS_SELECTOR, ".a-section.a-spacing-small.puis-padding-left-small.puis-padding-right-small")
                        try:
                            amount_element = child2.find_element(By.CSS_SELECTOR, '.a-section.a-spacing-none.a-spacing-top-small.s-price-instructions-style')
                            child3 = amount_element.find_element(By.CSS_SELECTOR, '.a-price')
                            element = child3.find_element(By.CSS_SELECTOR, ".a-price-whole")
                            value = element.text
                            value = value.strip()
                            child3 = amount_element.find_element(By.CSS_SELECTOR,'.a-size-base.a-link-normal.s-no-hover.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')
                            href_value = child3.get_attribute('href')
                            if float(value.replace(',', '.')) > 0:
                                print('search returned many products')
                                print(href_value, value)
                                product_url = link_Transform(href_value)
                                ASIN = get_ASIN(product_url)
                                print(EAN, ASIN, price)
                                print('storing in db1')
                                current_time = datetime.now()
                                saveToDB(EAN, ASIN, price,current_time) 

                                break
                        except:
                            pass
            except NoSuchElementException:
                pass
        except:
            pass

        try:
            children = driver.find_elements(By.CSS_SELECTOR, '.sg-col-20-of-24.s-matching-dir.sg-col-16-of-20.sg-col.sg-col-8-of-12.sg-col-12-of-16')
            print(len(children))
            if len(children) == 1:
                print('search returned a single result')
                child1 = children[0].find_elements(By.CSS_SELECTOR, ".s-main-slot.s-result-list.s-search-results.sg-row")
                print(child1)
                child2 = child1[0].find_elements(By.CSS_SELECTOR, ".a-section.a-spacing-base")
                if len(child2) > 0:
                    child3 = child2[0].find_elements(By.CSS_SELECTOR, ".a-section.a-spacing-small.puis-padding-left-small.puis-padding-right-small")
                    child4 = child3[0].find_element(By.CSS_SELECTOR, ".a-section.a-spacing-none.a-spacing-top-small.s-title-instructions-style")
                    child5 = child4.find_element(By.CSS_SELECTOR, ".a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal")
            #         print(len(child5))
                    price_child1 = child3[0].find_element(By.CSS_SELECTOR, ".a-section.a-spacing-none.a-spacing-top-small.s-price-instructions-style")
                    price_child2 = price_child1.find_element(By.CSS_SELECTOR, ".a-row.a-size-base.a-color-base")
                    price_child3 = price_child2.find_element(By.CSS_SELECTOR, ".a-size-base.a-link-normal.s-no-hover.s-underline-text.s-underline-link-text.s-link-style.a-text-normal")
                    price_child4 = price_child3.find_element(By.CSS_SELECTOR, ".a-price-whole")
                    print(price_child4)
                    PRICE = price_child4.text
                    href_value = child5.get_attribute('href')
                    print(href_value)
                    ASIN = get_ASIN(href_value)
                    current_time = datetime.now()
                    print(EAN, ASIN,PRICE,current_time)
                    print('storing in db2')
                    saveToDB(EAN, ASIN, PRICE,current_time)
        except NoSuchElementException:
            pass

        try:
            parent1 = driver.find_element(By.CSS_SELECTOR, '.s-desktop-width-max.s-desktop-content.s-wide-grid-style-t3.s-opposite-dir.s-wide-grid-style.sg-row')
            parent2 = parent1.find_elements(By.CSS_SELECTOR, '.sg-col-20-of-24.s-matching-dir.sg-col-16-of-20.sg-col.sg-col-8-of-12.sg-col-12-of-16')
            parent3 = parent2[0].find_element(By.CSS_SELECTOR, ".sg-col-inner")
            parent4 = parent3.find_element(By.CSS_SELECTOR, ".s-main-slot.s-result-list.s-search-results.sg-row")
            parent5 = parent4.find_element(By.CSS_SELECTOR, ".sg-col-20-of-24.s-result-item.s-asin.sg-col-0-of-12.sg-col-16-of-20.sg-col.s-widget-spacing-small.sg-col-12-of-16")
            parent6 = parent5.find_element(By.CSS_SELECTOR, ".sg-col-inner")
            parent7 = parent6.find_elements(By.CSS_SELECTOR, ".sg-col.sg-col-4-of-12.sg-col-8-of-16.sg-col-12-of-20.sg-col-12-of-24.s-list-col-right")
            parent8 = parent7[0].find_elements(By.CSS_SELECTOR, ".a-section.a-spacing-small.a-spacing-top-small")
            parent_price1 = parent8[0].find_elements(By.CSS_SELECTOR, ".sg-row")
            parent_anchor1 = parent7[0].find_elements(By.CSS_SELECTOR, ".a-section.a-spacing-none.puis-padding-right-small.s-title-instructions-style")
            child_anchor =  parent_anchor1[0].find_element(By.CSS_SELECTOR, ".a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal")
            href_value = child_anchor.get_attribute('href')
            child1 = parent_price1[0].find_elements(By.CSS_SELECTOR, ".sg-col.sg-col-4-of-12.sg-col-4-of-16.sg-col-4-of-20.sg-col-4-of-24")
            child2 = child1[0].find_elements(By.CSS_SELECTOR, ".a-section.a-spacing-none.a-spacing-top-micro.puis-price-instructions-style")
            child3 = child2[0].find_element(By.CSS_SELECTOR, ".a-price-whole")
            price = child3.text
            ASIN = get_ASIN(href_value)
            print(EAN,ASIN,price)
            print('saving to db3')
            current_time = datetime.now()
            saveToDB(EAN, ASIN, price,current_time)
        except NoSuchElementException:
            pass
        driver.quit()
    
    except TimeoutException as ex:
        print(ex.Message)
        webDriver.navigate().refresh()
