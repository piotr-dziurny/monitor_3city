# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import unicodedata

class OgloszeniaTrojmiastoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class OgloszenieItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    rooms = scrapy.Field()
    floor = scrapy.Field()
    year = scrapy.Field()
    price_per_sqr_meter = scrapy.Field()
    square_meters = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    area = scrapy.Field()
    coastline_distance = scrapy.Field()
    gdynia_downtown_distance = scrapy.Field()
    gdansk_downtown_distance = scrapy.Field() 
    sopot_downtown_distance = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    bbox = scrapy.Field()
    created_ts = scrapy.Field()
    scraped_ts = scrapy.Field()
    is_latest = scrapy.Field()
