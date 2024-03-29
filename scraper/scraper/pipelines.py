# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from products.models import Product
import logging, coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level="WARN", logger=logger)


class ScraperPipeline:
    def process_item(self, item, spider):
        try:
            Product.objects.create(**item)
            logger.warn("Loaded product {}".format(item['ASIN']))
        except Exception as e:
            logger.error("\nFailed to load quote, Reason For Failure:{}".format(e))

        return item
