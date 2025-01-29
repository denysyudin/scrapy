import requests
import scrapy

class SpiderSpider(scrapy.Spider):
    name = "spider"
    allowed_domains = ["circuitbreakerwarehouse.com"]
    start_urls = ["https://www.circuitbreakerwarehouse.com/category-s/45.htm",
                  "https://www.circuitbreakerwarehouse.com/category-s/46.htm",
                  "https://www.circuitbreakerwarehouse.com/category-s/47.htm",
                  "https://www.circuitbreakerwarehouse.com/category-s/48.htm",
                  "https://www.circuitbreakerwarehouse.com/category-s/49.htm",
                  "https://www.circuitbreakerwarehouse.com/category-s/50.htm",
                  "https://www.circuitbreakerwarehouse.com/category-s/51.htm",
                  "https://www.circuitbreakerwarehouse.com/category-s/52.htm",
                  "https://www.circuitbreakerwarehouse.com/category-s/53.htm",
                  "https://www.circuitbreakerwarehouse.com/category-s/54.htm",
                  "https://www.circuitbreakerwarehouse.com/category-s/55.htm",
                  "https://www.circuitbreakerwarehouse.com/category-s/56.htm",
                  "https://www.circuitbreakerwarehouse.com/category-s/57.htm",
                  "https://www.circuitbreakerwarehouse.com/category-s/58.htm",
                  "https://www.circuitbreakerwarehouse.com/category-s/59.htm",
                  "https://www.circuitbreakerwarehouse.com/category-s/60.htm",
                  ]

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.88 Safari/537.36",
        "ROBOTSTXT_OBEY": False,  # Disable robots.txt checking
    }
    
    def __init__(self, *args, **kwargs):
        super(SpiderSpider, self).__init__(*args, **kwargs)
        self.manufactures_list = []

    def parse(self, response):
        container = response.xpath('//section')
        products = container.xpath('.//div[@class="v-product"]')
        for product in products:
        # product = products[0]
            product_link = product.xpath('.//a[@class="v-product__img"]/@href').get()
            yield scrapy.Request(
                url=product_link, 
                callback=self.parse_product
            )
        # Handle pagination
        current_page = int(response.xpath('//input[@title="Go to page"]/@value').get())
        total_pages = int(response.xpath('//nobr/font/b/font/b/text()').re_first(r'of (\d+)'))
        if current_page <= total_pages:
            print("current_page", current_page)
            print("total_pages", total_pages)
            if current_page == 1:
                next_page = f"{response.url}?searching=Y&sort=13&cat=45&show=150&page={current_page + 1}"
            else:
                next_page = response.url.replace(f"page={current_page}", f"page={current_page + 1}")
            print(f"Following next page: {next_page}")
            yield response.follow(next_page, self.parse)

    def parse_product(self, response):
        title = response.xpath('//span[@itemprop="name"]//text()').get()
        image_url = "https:" + response.xpath('//img[@class="vCSS_img_product_photo" and @id="product_photo"]/@src').get()
        # Create a JSON structure
        our_price = 'NA'
        sale_price = 'NA'
        condition = 'NA'
        type = 'NA'
        pole = 'NA'
        amperage = 'NA'
        voltage = 'NA'
        availability = 'NA'
        product_code = 'NA'
        try:
            our_price = response.xpath('//div[@class="product_productprice"]/text()').get().strip().replace(': ', '')
        except:
            our_price = 'NA'
        try:
            sale_price ='$' + response.xpath('//span[@itemprop="price"]/text()').get()
        except:
            sale_price = 'NA'
        try:
            condition = response.xpath('//meta[@itemprop="itemCondition"]/@content').get()
        except:
            condition = 'NA'
        try:
            type = response.xpath('normalize-space(//b[contains(text(),"Type:")]/following-sibling::text())').get()
        except:
            type = 'NA'
        try:
            pole = response.xpath('normalize-space(//b[contains(text(),"Pole:")]/following-sibling::text())').get()
        except:
            pole = 'NA'
        try:
            amperage = response.xpath('normalize-space(//b[contains(text(),"Amprage:")]/following-sibling::text())').get()
        except:
            amperage = 'NA'
        try:
            voltage = response.xpath('normalize-space(//b[contains(text(),"Voltage:")]/following-sibling::text())').get()
        except:
            voltage = 'NA'
        try:
            availability = response.xpath('//meta[@itemprop="availability"]/@content').get()
        except:
            availability = 'NA'
        try:
            product_code = response.xpath('normalize-space(//span[@class="product_code"]/text())').get()
        except:
            product_code = 'NA'
        product_data = {
            "data":{
                "title": title,
                "image_url": image_url,
                "specifications": {
                    "our_price": our_price,
                    "sale_price": sale_price,
                    "condition": condition,
                    "type": type,
                    "pole": pole,
                    "amperage": amperage,
                    "voltage": voltage,
                    "availability": availability,
                    "product_code": product_code
                }
            }
        }     
        # Send the JSON data to the API
        # print(product_data)
        response = requests.post("http://127.0.0.1:8000/superbreakers", json=product_data)
        print(response.status_code)