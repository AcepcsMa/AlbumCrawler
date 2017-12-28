# -*- coding: utf-8 -*-
import scrapy
from AlbumCrawler.utils import Utils
from AlbumCrawler.items import AlbumItem
from scrapy import Request
import time
import re

class PexelsSpider(scrapy.Spider):
    name = 'Pexels'

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
    }

    def start_requests(self):
        urls = Utils.getStartUrlsFromDb(PexelsSpider.name)
        for url in urls:
            yield Request(url=url, headers=self.headers)

    def parse(self, response):

        photoUrls = response.xpath("//article[@class=\'photo-item\']/a/@href")
        avatars = response.xpath("//article[@class=\'photo-item\']/a/img/@src")
        for photoUrl, avatar in zip(photoUrls, avatars):
            album = AlbumItem()
            url = response.urljoin(photoUrl.extract())
            album["avatarUrl"] = avatar.extract()
            album["albumUrl"] = url
            album["albumPicCount"] = 1
            album["dataType"] = 1
            yield Request(url=url, callback=self.parse_content,
                          meta={"album": album}, headers=self.headers)

        pageCount = int(re.findall("page=([0-9]+)", response.url)[0])
        if pageCount < 20:
            url = re.sub("page=[0-9]+", "page={}".format(pageCount+1), response.url)
            yield Request(url=url, headers=self.headers)

    def parse_content(self, response):

        tags = response.xpath("//div[@class=\'box\']/ul[contains(@class, \'list-inline\')]/li/a/text()")
        content = list()
        for tag in tags:
            content.append(tag.extract())
        content = ','.join(content)

        album = response.meta["album"]
        album["albumTitle"] = response.url[response.url[:-1].rfind("/")+1:response.url.rfind("-")]
        album["albumDescription"] = album["albumTitle"]
        album["albumContent"] = content
        album["albumPubTime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        yield album