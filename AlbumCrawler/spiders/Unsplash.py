# -*- coding: utf-8 -*-
import scrapy
from AlbumCrawler.utils import Utils
from scrapy import Request
from AlbumCrawler.items import AlbumItem
import json
import re

class UnsplashSpider(scrapy.Spider):
    name = 'Unsplash'
    # allowed_domains = ['unsplash.com']
    # start_urls = ['http://unsplash.com/']

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "authorization": "Client-ID c94869b36aa272dd62dfaeefed769d4115fb3189a9d1ec88ed457207747be626"
    }

    def start_requests(self):
        urls = Utils.getStartUrlsFromDb(self.name)
        for url in urls:
            yield Request(url=url, headers=self.headers)

    def parse(self, response):

        dataJson = json.loads(response.body)["results"]
        for each in dataJson:
            album = AlbumItem()
            album["dataType"] = 0
            album["albumTitle"] = each["title"]
            album["albumDescription"] = each["title"] if each["description"] is None else each["description"]
            album["albumUrl"] = each["links"]["html"]
            album["avatarUrl"] = each["cover_photo"]["urls"]["small"]
            album["albumPicCount"] = each["total_photos"]

            contents = list()
            for tag in each["tags"]:
                contents.append(tag["title"])
            album["albumContent"] = ",".join(contents)
            album["albumPubTime"] = re.sub("T", " ", each["published_at"])[:each["published_at"].rfind("-")]
            yield album

        pageCount = int(re.findall("&page=([0-9]+)", response.url)[0])
        if pageCount < 10:
            url = re.sub("&page=[0-9]+?", "&page={}".format(pageCount+1), response.url)
            yield Request(url=url, headers=self.headers)
