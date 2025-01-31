import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests

class RelectricCircuitBreakerScraper:
    def __init__(self):
        self.scrape_url = "https://www.relectric.com/circuit-breakers/molded-case"
        self.setup_driver()

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
        self.driver = webdriver.Chrome(options=chrome_options)

    @staticmethod
    def is_float(string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def scrape_product(self, product_url):
        print(product_url)
        self.driver.get(product_url)
        time.sleep(2)
        
        title_bar = self.driver.find_element(By.XPATH, '//div[contains(@class, "product-title-bar")]')
        title = title_bar.find_element(By.XPATH, './/h1').text

        subtitle = title_bar.find_element(By.XPATH, '//span[@class="h4"]').text.replace('Item # ', '')
        
        price_container = self.driver.find_element(By.XPATH, '//div[@id="product-buy-box"]')
        price_list = price_container.find_elements(By.XPATH, './/p[@class="price-att"]')
        re_certified_price = price_list[0].text.strip('$').replace(',', '')
        re_certified_plus_price = price_list[1].text.strip('$').replace(',', '')
        new_price = price_list[2].text.strip('$').replace(',', '')
        re_certified_price = float(re_certified_price) if self.is_float(re_certified_price) else 'NA'
        re_certified_plus_price = float(re_certified_plus_price) if self.is_float(re_certified_plus_price) else 'NA'
        new_price = float(new_price) if self.is_float(new_price) else 'NA'
        
        if re_certified_price == 'NA':
            re_certified_price = re_certified_plus_price
        elif re_certified_plus_price == 'NA':
            re_certified_price = re_certified_price
        else:
            re_certified_price = min(re_certified_price, re_certified_plus_price)
            
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
                're_certified_price': re_certified_price,
                'new_price': new_price,
                'specifications': specifications
            }
        }
        response = requests.post('http://localhost:8000/api/superbreakers', json=product_data)
        print(response.json())

    def scrape_all_products(self):
        self.driver.get(self.scrape_url)
        time.sleep(2)
        while True:
            product_container = self.driver.find_element(By.XPATH, '//ol[@class="ais-Hits-list"]')
            products = product_container.find_elements(By.XPATH, './/li[@class="ais-Hits-item"]')
            
            product_links = [product.find_element(By.XPATH, './/a').get_attribute('href') for product in products]
            
            for product_link in product_links:
                self.scrape_product(product_link)
            self.driver.close()
            self.setup_driver()
            self.driver.get(self.scrape_url)
            time.sleep(2)
            try:
                print('next')
                pagination_container = self.driver.find_element(By.XPATH, '//div[@class="ais-Pagination"]')
                next_button = pagination_container.find_element(By.XPATH, '//li[@class="ais-Pagination-item ais-Pagination-item--nextPage"]//a')
                print(next_button)
                self.driver.execute_script("arguments[0].click();", next_button)
                time.sleep(1)
            except Exception as e:
                print(e)
                break

    def cleanup(self):
        self.driver.close()
        self.driver.quit()

def main():
    scraper = RelectricCircuitBreakerScraper()
    try:
        scraper.scrape_all_products()
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()