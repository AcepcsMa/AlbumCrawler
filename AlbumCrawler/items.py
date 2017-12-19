# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AlbumcrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class AlbumItem(scrapy.Item):

    albumTitle = scrapy.Field()
    albumDescription = scrapy.Field()
    avatarUrl = scrapy.Field()
    albumUrl = scrapy.Field()
    albumPicCount = scrapy.Field()
    albumContent = scrapy.Field()
    albumPubTime = scrapy.Field()