# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class RunScrapyItem(scrapy.Item):
	author = scrapy.Field()
	title = scrapy.Field()
	link = scrapy.Field()
	intro = scrapy.Field()
	image = scrapy.Field()
