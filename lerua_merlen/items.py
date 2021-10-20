# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose

def clear_price(value):
    try:
        value = int(value.replace('\xa0', ''))
    except:
        return value
    return value

class LeruaMerlenItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(clear_price), output_processor=TakeFirst())
    photo = scrapy.Field()
    link = scrapy.Field(output_processor=TakeFirst())
    _id = scrapy.Field()