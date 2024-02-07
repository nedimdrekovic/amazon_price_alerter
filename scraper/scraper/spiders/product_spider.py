import json
import re
import urllib.parse
from multiprocessing import Process

import math
import scrapy
from billiard import Process
from scrapy import signals
from scrapy.crawler import Crawler
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor

from products.models import Product

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
}


class CrawlerScript(Process):
    def __init__(self, spider):
        """
        Constructs a CrawlerScript object that prevents crawler from stopping the script

        :param spider: the scrapy object.
        """
        Process.__init__(self)
        settings = get_project_settings()
        self.crawler = Crawler(spider.__class__, settings)
        self.crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
        self.spider = spider

    def run(self):
        self.crawler.crawl(self.spider)
        reactor.run()


def website_exists(response):
    """ Return True if website exists."""
    try:
        status_code = response.status
        if status_code != 200:
            print("Website existiert zwar, aber es gibt einen anderen Fehler")
            return False
    except Exception:
        return False
    return True


class ProductSpider(scrapy.Spider):
    name = "products"

    def __init__(self, data):
        self.data = data

    def start_requests(self):
        """ Generates Request for the URL."""
        urls = [
            'https://www.amazon.de/Apple-MacBook-Laptop-11%E2%80%91Core-14%E2%80%91Core/dp/B0CM5Z87MP/ref=sr_1_3?__mk_de_DE=ÅMÅŽÕÑ&crid=1ITLD62CRWJND&keywords=macbook+pro&qid=1706023551&sprefix=macbook+p%2Caps%2C126&sr=8-3',
        ]

        for product_data in list(self.data.data[0]):
            url = product_data['url']
            desired_price = product_data['desired_price']
            try:
                yield scrapy.Request(url=url,
                                     callback=self.parse,
                                     meta={'url': url,
                                           'desired_price': desired_price,
                                           'status': self.data.data[-1]},
                                     headers=headers)
            except ValueError:
                print("Website'", url, "'existiert nicht.")

    def parse(self, response):
        """
        Parse the website and add/update the product.

        :param response: containts data about the current request
        :return: None.
        """
        # for adding new product
        if not website_exists(response):
            # do not parse
            return

        url = urllib.parse.unquote(response.meta['url'])
        temp = list(Product.objects.all().values_list('url', flat=True))
        temp = [urllib.parse.unquote(url) for url in temp]
        if url not in temp:
            title = response.css("#productTitle::text").get("").strip()

            price = response.xpath('//*[@id="priceblock_ourprice"]/text()').extract_first()
            if price in (None, '', []):
                # to do:
                # other method in case this one doesnt extract the price
                price = 0
            if not price:
                price = response.css('.a-price .a-offscreen ::text').get("")

            image = json.loads(re.findall(r"colorImages':.*'initial':\s*(\[.+?\])},\n", response.text)[0])[0]['hiRes']

            desired_price = response.meta['desired_price']
            desired_price = math.floor(float(desired_price) * 100) / 100.0

            price = price.replace('€', '')  # remove euro symbol in case it is added
            price = price.replace('.', '')  # remove points in case price is >= 1000
            price = price.replace(',', '.')  # replace comma with point to represent positions after decimal point
            price = float(price)

            status = response.meta['status']
            if status == 'create':
                mail_has_been_sent = price <= desired_price  # to prevent sending an email when creating a product
                # create object
                Product.objects.create(image=image,
                                       title=title,
                                       url=url,
                                       price=price,
                                       desired_price=desired_price,
                                       mail_has_been_sent=mail_has_been_sent)
            elif status == 'update':
                Product.objects.filter(url=url).update(image=image,
                                                       title=title,
                                                       price=price,
                                                       desired_price=desired_price)
            print("Object created")
