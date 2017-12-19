# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import json
from AlbumCrawler.items import AlbumItem
from AlbumCrawler.utils import Utils
import re

class NeteaseSpider(scrapy.Spider):
    name = 'Netease'

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
    }

    def start_requests(self):
        urls = Utils.getStartUrlsFromDb(NeteaseSpider.name)
        for url in urls:
            yield Request(url=url, headers=self.headers)

    def parse(self, response):

        html = re.findall("cacheMoreData\((.+?}])\)", response.body.decode(),flags=re.S)[0]
        dataJson = json.loads(html)

        for each in dataJson:
            album = AlbumItem()
            album["albumTitle"] = each["setname"]
            album["albumDescription"] = each["setname"]
            album["albumUrl"] = each["seturl"]
            album["avatarUrl"] = each["cover"]
            album["albumPicCount"] = each["imgsum"]
            album["albumPubTime"] = each["datetime"]
            yield Request(url=each["seturl"], meta={"album":album},
                          headers=self.headers, callback=self.parse_content)

    def parse_content(self, response):

        album = response.meta["album"]
        content = ""
        contents = response.xpath("//textarea/text()").extract()
        contents = re.findall("\"note\": \"(.+?)\",", contents[0])

        for each in contents:
            content += each
        album["albumContent"] = content
        yield album
