# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdcsItem(scrapy.Item):
    # define the fields for your item here like:
    cates = scrapy.Field()
    from_url = scrapy.Field()
    url = scrapy.Field()