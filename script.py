import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests

class RelectricCircuitBreakerScraper:
    def __init__(self):
        self.scrape_url = [
            # "https://www.relectric.com/circuit-breakers/molded-case",
            "https://www.relectric.com/circuit-breakers/miniature",
            "https://www.relectric.com/circuit-breakers/insulated-case",
            "https://www.relectric.com/busway/bus-plugs",
            "https://www.relectric.com/busway/tapbox",
            "https://www.relectric.com/busway/elbows-and-tees",
            "https://www.relectric.com/busway/bus-duct",
            "https://www.relectric.com/busway/parts",
            "https://www.relectric.com/motor-control/contactors",
            "http://relectric.com/motor-control/starters",
            "https://www.relectric.com/motor-control/variable-frequency-drives",
            "https://www.relectric.com/transformers/general-purpose",
            "https://www.relectric.com/transformers/buck-boost",
            "https://www.relectric.com/transformers/control-power",
            "https://www.relectric.com/automation/plcs",
            "https://www.relectric.com/automation/sensors",
            "https://www.relectric.com/automation/control-relays",
            "https://www.relectric.com/transformers/control-power"]

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

        # Add page load timeout
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(30)
        self.driver.implicitly_wait(10)

    @staticmethod
    def is_float(string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def scrape_product(self, product_url):
        try:
            print(product_url)
            self.driver.get(product_url)
            time.sleep(2)
            
            try:
                title_bar = self.driver.find_element(By.XPATH, '//div[contains(@class, "product-title-bar")]')
                title = title_bar.find_element(By.XPATH, './/h1').text
            except:
                return

            subtitle = title_bar.find_element(By.XPATH, '//span[@class="h4"]').text.replace('Item # ', '')

            image_url = self.driver.find_element(By.XPATH, '//div[@id="main-image-wrapper"]//img').get_attribute('src')
            
            price_container = self.driver.find_element(By.XPATH, '//div[@id="product-buy-box"]')
            price_list = price_container.find_elements(By.XPATH, './/p[@class="price-att"]')
            title_list = price_container.find_elements(By.XPATH, './/span[@class="name-att"]')
            re_certified_price = 'NA'
            new_price = 'NA'
            for index, name in enumerate(title_list):
                if name.text.lower() == 're-certified':
                    re_certified_price = price_list[index].text.strip('$').replace(',', '')
                elif name.text.lower() == 're-certified plus':
                    pass
                elif name.text.lower() == 'new':
                    new_price = price_list[index].text.strip('$').replace(',', '')
                elif name.text.lower() == 'new surplus':
                    new_price = price_list[index].text.strip('$').replace(',', '')
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
            # print(product_data)
            response = requests.post('http://localhost:8000/api/superbreakers', json=product_data)
            print(response.json())
        except Exception as e:
            print(f"Error scraping product {product_url}: {str(e)}")

            try:
                self.driver.quit()
            except:
                pass
            self.setup_driver()
            return None

    def scrape_all_products(self):
        for url in self.scrape_url:
            try:
                self.driver.get(url)
                page_number = 1
                time.sleep(2)
                while True:
                    try:
                        product_container = self.driver.find_element(By.XPATH, '//ol[@class="ais-Hits-list"]')
                        products = product_container.find_elements(By.XPATH, './/li[@class="ais-Hits-item"]')
                    
                        product_links = [product.find_element(By.XPATH, './/a').get_attribute('href') for product in products]
                    
                        for product_link in product_links:
                            self.scrape_product(product_link)
                        # self.driver.quit()
                        # self.setup_driver()
                        self.driver.get(url)
                        time.sleep(2)
                    
                        for i in range(page_number):
                            print(f'click {i}')
                            pagination_container = self.driver.find_element(By.XPATH, '//div[@class="ais-Pagination"]')
                            next_button = pagination_container.find_element(By.XPATH, '//li[@class="ais-Pagination-item ais-Pagination-item--nextPage"]//a')
                            self.driver.execute_script("arguments[0].click();", next_button)
                            time.sleep(3)
                        page_number += 1
                        print(f'Page {page_number}')
                    except Exception as e:
                        print(e)
                        break
            except Exception as e:
                print(f"Error scraping {url}: {str(e)}")
                continue

    def cleanup(self):
        try:
            self.driver.close()
            self.driver.quit()
        except Exception as e:
            print(f"Error closing driver: {str(e)}")


def main():
    scraper = RelectricCircuitBreakerScraper()
    try:
        scraper.scrape_all_products()
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()