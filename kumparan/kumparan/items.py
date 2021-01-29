# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

##import scrapy
from scrapy.item import Item, Field


#class InaprocItem(scrapy.Item):
class InaprocItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
#    pass
# List of fields
    kegiatan = Field()
    tahun = Field()
    pagu = Field()
    sumber = Field()
    date = Field()
    desc = Field()
