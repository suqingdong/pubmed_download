# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

# from scrapy.conf import settings
from pubmed_download import settings



class PubmedPipeline(object):

    host = settings.MONGODB_HOST
    port = settings.MONGODB_PORT
    dbname = settings.MONGODB_DBNAME
    colname = settings.MONGODB_COLNAME

    client = pymongo.MongoClient(host=host, port=port)
    db = client[dbname]
    col = db[colname]

    def process_item(self, item, spider):

        self.col.insert(dict(item))

        return item
