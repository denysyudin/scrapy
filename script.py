import os
import dotenv
import pandas as pd
import numpy as np
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

dotenv.load_dotenv()

class RelectricCircuitBreakerScraper:
    def __init__(self):
        self.scrape_url = [
            # "https://www.relectric.com/circuit-breakers/molded-case",
            # "https://www.relectric.com/circuit-breakers/miniature",
            # "https://www.relectric.com/circuit-breakers/insulated-case",
            # "https://www.relectric.com/busway/bus-plugs",
            # "https://www.relectric.com/busway/tapbox",
            # "https://www.relectric.com/busway/elbows-and-tees",
            # "https://www.relectric.com/busway/bus-duct",
            # "https://www.relectric.com/busway/parts",
            # "https://www.relectric.com/motor-control/contactors",
            # "http://relectric.com/motor-control/starters",
            # "https://www.relectric.com/motor-control/variable-frequency-drives",
            # "https://www.relectric.com/transformers/general-purpose",
            # "https://www.relectric.com/transformers/buck-boost",
            # "https://www.relectric.com/transformers/control-power",
            # "https://www.relectric.com/automation/plcs",
            # "https://www.relectric.com/automation/sensors",
            # "https://www.relectric.com/automation/control-relays"
            ]

        self.setup_driver()
        self.data = pd.read_csv('products.csv')
        self.data['circuitbreakers_new'] = np.nan
        self.data['circuitbreakers_used'] = np.nan
        self.data['relectric_new'] = np.nan
        self.data['relectric_used'] = np.nan
        self.create_url()

    def setup_driver(self):
        # Set proxy environment variables
        os.environ['HTTP_PROXY'] = ''
        os.environ['HTTPS_PROXY'] = ''
        os.environ['http_proxy'] = ''
        os.environ['https_proxy'] = ''

        # Initialize WebDriver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-proxy-server")
        chrome_options.add_argument("--proxy-bypass-list=*")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        # Add page load timeout
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(30)
        self.driver.implicitly_wait(10)

    def create_url(self):
        for item in self.data['Part Number (Handle)']:
            url = f"https://www.relectric.com/{item}"
            self.scrape_url.append(url)

    @staticmethod
    def is_float(string):
        try:
            float(string)
            return True
        except ValueError:
            return False
        
    def insert_data(self, product_data, index):
        data = pd.read_csv('products.csv')
        if data['condition'][index] == 'New':
            price = float(product_data['new_price'].replace("$", "").replace(",", ""))
            data.at[index, 'relectricbreakers_new'] = price

        elif data['condition'][index] == 'Used':
            price = float(product_data['re_certified_price'].replace("$", "").replace(",", ""))
            print(f"Setting relectricbreakers_used price to {price}")
            data.at[index, 'relectricbreakers_used'] = price
            print(f"After setting, value is: {data.at[index, 'relectricbreakers_used']}")

    def scrape_product(self):
        for index_url, product_url in enumerate(self.scrape_url):
            try:
                print(product_url)
                self.driver.get(product_url)
                time.sleep(2)
                
                try:
                    title_bar = self.driver.find_element(By.XPATH, '//div[contains(@class, "product-title-bar")]')
                    title = title_bar.find_element(By.XPATH, './/h1').text
                except:
                    print(f"Error getting title for {product_url}")
                    continue

                subtitle = title_bar.find_element(By.XPATH, '//span[@class="h4"]').text.replace('Item # ', '')

                image_url = self.driver.find_element(By.XPATH, '//div[@id="main-image-wrapper"]//img').get_attribute('src')
                
                price_container = self.driver.find_element(By.XPATH, '//div[@id="product-buy-box"]')
                price_list = price_container.find_elements(By.XPATH, './/p[@class="price-att"]')
                title_list = price_container.find_elements(By.XPATH, './/span[@class="name-att"]')
                re_certified_price = 'NA'
                new_price = 'NA'
                for index, name in enumerate(title_list):
                    print(name.text.lower(), price_list[index].text)
                    if name.text.lower() == 're-certified':
                        re_certified_price = price_list[index].text.strip('$').replace(',', '')
                    if name.text.lower() == 're-certified plus':
                        pass
                    if name.text.lower() == 'new':
                        new_price = price_list[index].text.strip('$').replace(',', '')
                    if name.text.lower() == 'new surplus':
                        new_price = price_list[index].text.strip('$').replace(',', '')
                    print(re_certified_price, new_price)
                re_certified_price = float(re_certified_price) if self.is_float(re_certified_price) else 'NA'
                new_price = float(new_price) if self.is_float(new_price) else 'NA'
                    
                specification_table = self.driver.find_elements(By.XPATH, '//table//tbody//tr')
                specifications = {}
                for specification in specification_table:
                    specification_name = specification.find_element(By.XPATH, './/td[1]').text
                    specification_value = specification.find_element(By.XPATH, './/td[2]').text
                    specifications[specification_name] = specification_value

                product_data = {
                    "data":{
                        'title': title,
                        'subtitle': subtitle,
                        'image_url': image_url,
                        're_certified_price': re_certified_price,
                        'new_price': new_price,
                        'specifications': specifications
                    }
                }
                self.insert_data(product_data, index_url)
                # # print(product_data)
                # response = requests.post('http://localhost:8000/api/superbreakers', json=product_data)
                # print(response.json())
            except Exception as e:
                print(f"Error scraping product {product_url}: {str(e)}")

    def cleanup(self):
        try:
            self.driver.close()
            self.driver.quit()
        except Exception as e:
            print(f"Error closing driver: {str(e)}")


def main():
    scraper = RelectricCircuitBreakerScraper()
    try:
        scraper.scrape_product()
    finally:
        scraper.cleanup()
        scraper.data.to_csv('updated_products.csv', index=False)

if __name__ == "__main__":
    main()