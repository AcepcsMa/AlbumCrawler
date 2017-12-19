# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.conf import settings
import pymysql
from AlbumCrawler.utils import Utils
from qiniu import Auth
import redis
import time
from elasticsearch import Elasticsearch
import jieba

class AlbumcrawlerPipeline(object):
    def process_item(self, item, spider):
        return item


class AlbumPipeline(object):

    def __init__(self):

        # load redis config and build connection pool
        redisHost = settings["REDIS_HOST"]
        redisPort = settings["REDIS_PORT"]
        self.redisPool = redis.ConnectionPool(host=redisHost, port=redisPort)
        self.redisConnect = redis.Redis(connection_pool=self.redisPool)

        # load mysql config and build connection
        host = settings["MYSQL_HOST"]
        port = settings["MYSQL_PORT"]
        dbName = settings["MYSQL_DBNAME"]
        user = settings["MYSQL_USER"]
        pwd = settings["MYSQL_PWD"]
        self.mysqlConnect = pymysql.connect(host=host, port=port,
                                       db=dbName, user=user,
                                       passwd=pwd, charset="utf8")
        self.mysqlConnect.autocommit(True)

        # load qiniu config
        self.qiniuAuth = Auth(settings["QINIU_ACCESS_KEY"],
                              settings["QINIU_SECRET_KEY"])
        self.qiniuDomain = settings["QINIU_DOMAIN"]
        self.qiniuBucket = settings["QINIU_BUCKET"]

        # build es connection
        self.esConnect = Elasticsearch(hosts=[settings["ELASTIC_HOST"]],
                                  port=settings["ELASTIC_PORT"])

        self.urlRecord = set()

    def process_item(self, item, spider):
        if self.redisConnect.zscore("album_url", item["albumUrl"]) is None:
            albumData = dict(item)
            urlMD5 = Utils.md5(albumData["albumUrl"])
            if urlMD5 not in self.urlRecord:
                avatarMD5 = Utils.md5(albumData["avatarUrl"])
                if Utils.fetchImage(albumData["avatarUrl"], self.qiniuAuth, self.qiniuBucket, avatarMD5):
                    albumData["avatarUrl"] = self.qiniuDomain + avatarMD5
                    self.saveToMySql(albumData)
                    self.esIndex(albumData)  # add to elastic-search
                    self.redisConnect.zadd("album_url", # add url to redis
                                           albumData["albumUrl"],
                                           int(time.time()))
                    self.urlRecord.add(urlMD5)
        return item

    def esIndex(self, item):
        '''Save item data to elastic-search

            Args:
                item: album item
        '''
        doc = {
            "title": item["albumTitle"],
            "content": item["albumContent"],
            "pic_count": item["albumPicCount"],
            "pub_time": item["albumPubTime"],
            "avatar_url": item["avatarUrl"],
            "url": item["albumUrl"],
            "suggest": {
                "input":(",".join(jieba.cut_for_search(item["albumTitle"]))).split(",")
            }
        }
        self.esConnect.index(index="albums", doc_type="album", body=doc)
        self.esConnect.indices.refresh(index="albums")

    def saveToMySql(self, item):
        '''Save item data to mysql

            Args:
                item: album item
        '''
        cursor = self.mysqlConnect.cursor()
        cursor.callproc("insert_album",
                        [item["albumTitle"], item["albumPicCount"],
                         item["albumDescription"], item["avatarUrl"],
                         item["albumUrl"], item["albumContent"],
                         item["albumPubTime"]])
        cursor.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.mysqlConnect.close()