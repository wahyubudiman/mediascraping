# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
#import scrapy
from scrapy.item import Item, Field

class TribunItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = Field()
    link = Field()
    images = Field()
    category = Field()
    date = Field()
    desc = Field()

