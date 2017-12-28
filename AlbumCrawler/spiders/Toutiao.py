# -*- coding: utf-8 -*-
import scrapy
import time
from scrapy import Request
import json
from AlbumCrawler.items import AlbumItem
from AlbumCrawler.utils import Utils

class ToutiaoSpider(scrapy.Spider):
    name = 'Toutiao'

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "Host": "www.toutiao.com"
    }

    def start_requests(self):
        urls = Utils.getStartUrlsFromDb(ToutiaoSpider.name)
        for url in urls:
            currentTimestamp = int(time.time())
            yield Request(url=url.format(currentTimestamp), headers=self.headers)

    def parse(self, response):

        responseJson = json.loads(response.body)
        if responseJson["message"] == "success":
            data = responseJson["data"]
            for each in data:
                album = AlbumItem()
                album["dataType"] = 0
                album["albumTitle"] = each["title"]
                album["albumDescription"] = each["title"]
                album["albumUrl"] = response.urljoin(each["source_url"])
                album["avatarUrl"] = each["middle_image"]
                album["albumPicCount"] = each["gallary_image_count"]
                album["albumPubTime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(each["behot_time"]))
                try:
                    album["albumContent"] = ",".join(each["label"])
                except:
                    album["albumContent"] = each["title"]
                yield album
