from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import re
import time
import csv

csv_file = "scraped_data.csv"
with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["title", "new_price", "re_certified_price"])
# Add these lines before initializing the WebDriver
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

# Initialize WebDriver
chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-proxy-server")
chrome_options.add_argument("--proxy-bypass-list=*")
driver = webdriver.Chrome(options=chrome_options)

# Load environment variables
api_url = os.getenv("API_URL")
auth_token = os.getenv("AUTH_TOKEN")

# Define the URL to scrape
scrape_url = "https://www.relectric.com/circuit-breakers/molded-case"
# Open the scrape URL
driver.get(scrape_url)

product_links = []

product_container = driver.find_element(By.XPATH, '//ol[@class="ais-Hits-list"]')
products = product_container.find_elements(By.XPATH, './/li[@class="ais-Hits-item"]')

def write_Data(title, new_price, re_certified_price):
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(title, new_price, re_certified_price)

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

while True:
    product_link = []
    for product in products:
        product_link.append("https://www.relectric.com/circuit-breakers/molded-case" + product.find_element(By.XPATH, './/a').get_attribute('href'))
    for product in product_link:
        driver.get(product)
        time.sleep(2)
        title_bar = driver.find_element(By.XPATH, '//div[@class="row product-title-bar"]')
        title = title_bar.find_element(By.XPATH, './/h1').text
        print(title)
        re_certified_price = driver.find_elements(By.XPATH, '//div[contains(@class, "has-price")]')[0].find_elements(By.XPATH, './/p[@class= "price-att"]').text
        re_certified_plus_price = driver.find_elements(By.XPATH, '//div[contains(@class, "has-price")]')[1].find_elements(By.XPATH, './/p[@class= "price-att"]').text
        new_price = driver.find_elements(By.XPATH, '//div[contains(@class, "has-price")]')[2].find_elements(By.XPATH, './/p[@class= "price-att"]').text
        if not is_float(re_certified_price):
            re_certified_price = 0
        if not is_float(re_certified_plus_price):
            re_certified_plus_price = 0
        if not is_float(new_price):
            new_price = 0
        re_certified_plus_price = float(re_certified_plus_price)
        re_certified_price = float(re_certified_price)
        new_price = float(new_price)
        re_certified_price = re_certified_price if re_certified_price < re_certified_plus_price else re_certified_plus_price
        write_Data(title, new_price, re_certified_price)
    driver.get(scrape_url)
    time.sleep(1)
    try:
        next_button = driver.find_element(By.XPATH, '//li[@class="ais-Pagination-item ais-Pagination-item--nextPage"]//a')
        next_button.click()
        time.sleep(1)
    except:
        break
# Cleanup
driver.quit()