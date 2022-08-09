# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst

def process_price(value:str):
    value = value.strip().replace(' ', '')
    try:
        value = int(value)
    except Exception as e:
        #  print(e)
        pass


class CastoramaparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    _id = scrapy.Field()
    photo = scrapy.Field()
    price = scrapy.Field(input_processor=MapCompose(process_price), output_processor=TakeFirst())
