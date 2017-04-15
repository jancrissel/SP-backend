# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# class RunScrapyPipeline(object):
#     def process_item(self, item, spider):
#         return item
from twisted.enterprise import adbapi  
from scrapy.utils.project import get_project_settings
import MySQLdb.cursors
 
settings = get_project_settings()

class SQLPipeline(object):
 
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool('MySQLdb', db='newsDB',
                user='aggregator', passwd='aggregator', cursorclass=MySQLdb.cursors.DictCursor,
                charset='utf8', use_unicode=True)
 
    def process_item(self, item, spider):
        # run db query in thread pool
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        query.addErrback(self.handle_error)
 		log.msg("DATABASE----------")
        return item
 
    def _conditional_insert(self, tx, item):
        # create record if doesn't exist. 
        # all this block run on it's own thread
        tx.execute("select * from NEWS where link = %s", (item['link'], ))
        result = tx.fetchone()
        if result:
            log.msg("Item already stored in db: %s" % item, level=log.DEBUG)
        else:
            tx.execute(\
                "insert into NEWS (title, author, link, image) "
                "values (%s, %s, %s, %s)",
                (item['title'], "Inquirer" ,item['link'], item['image'])
            #      datetime.datetime.now())
             )
            log.msg("Item stored in db: %s" % item, level=log.DEBUG)
 
    def handle_error(self, e):
        log.err(e)
