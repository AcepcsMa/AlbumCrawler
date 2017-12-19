# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from AlbumCrawler import items
from AlbumCrawler.utils import Utils
import json

class SinaSpider(scrapy.Spider):
    name = 'Sina'

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
    }

    def start_requests(self):
        urls = Utils.getStartUrlsFromDb(SinaSpider.name)
        for url in urls:
            yield Request(url=url, headers=self.headers)

    def parse(self, response):

        albumData = json.loads(response.body)["data"]
        for each in albumData:
            album = items.AlbumItem()
            album["albumTitle"] = each["name"]
            album["albumDescription"] = each["short_intro"]
            album["albumUrl"] = each["url"]
            album["avatarUrl"] = each["cover_img"]
            album["albumPicCount"] = each["img_count"]
            album["albumPubTime"] = each["createtime"]
            yield Request(url=each["url"], meta={"album": album},
                          callback=self.parse_content, headers=self.headers)

    def parse_content(self, response):
        '''Parse text content of each picture in the given album

        Args:
            response: the response from downloader
        Returns:
            an album data
        '''
        album = response.meta["album"]

        content = ""
        contentNodes = response.xpath("//div[@id='eData']/dl/dd[5]/text()")
        for contentNode in contentNodes:
            content += contentNode.extract()
        album["albumContent"] = content
        yield album
