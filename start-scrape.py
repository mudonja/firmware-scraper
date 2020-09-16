#!/bin/etc/env python

import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.files import FilesPipeline
from scrapy import Request


# TODO: Pipelines should be in a separated file
class FirmwarePipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        urls = ItemAdapter(item).get(self.files_urls_field, [])
        return [Request(u) for u in urls]

    def file_path(self, request, response=None, info=None):
        media_guid = request.url
        #print("MEDIA GUID:", media_guid)
        return 'full/%s' % media_guid


# TODO: Should also be in a separate file(e.g items.py)
class FirmwareItem(scrapy.Item):
    file_urls = scrapy.Field()
    files = scrapy.Field()
    name = scrapy.Field()
    size = scrapy.Field()
    md5 = scrapy.Field()
    next = scrapy.Field()


class FirmwareSpider(scrapy.Spider):
    name = "firmware_spider"
    start_urls = ['https://archive.openwrt.org/']
    #start_urls = ['https://archive.openwrt.org/attitude_adjustment/12.09/adm8668/generic/']
    custom_settings = {
        'LOG_ENABLED': True,
        'LOG_FILE': "log/logs.txt",
        'ITEM_PIPELINES': {'start-scrape.FirmwarePipeline': 1},
        'FILES_STORE': './testresult',
        'DOWNLOAD_MAXSIZE': 0,
        'DOWNLOAD_WARNSIZE': 0,
        'DOWNLOAD_TIMEOUT': 1200,


    }

    # Select the first column
    ELEMENT_SELECTOR = '.n'
    # Name of the first column element
    NAME_SELECTOR = '.n a ::text'
    # Link of the first column element
    NEXT_DIRECTORY_SELECTOR = '.n a ::attr(href)'
    SIZE_SELECTOR = '.s ::text'
    MD5_SELECTOR = '.sh ::text'

    # parsing rows
    def parse(self, response):
        for table_row in response.css('tr'):

            file_url = table_row.css(self.NEXT_DIRECTORY_SELECTOR).get()
            file_url = response.urljoin(file_url)
            if 'KB' not in table_row.css(self.SIZE_SELECTOR).extract_first() and '-' in table_row.css(
                    self.SIZE_SELECTOR).extract_first():
                yield scrapy.Request(
                    response.urljoin(file_url),
                    callback=self.parse,
                    dont_filter=True
                )
            elif 'KB' in table_row.css(self.SIZE_SELECTOR).extract_first():
                item = FirmwareItem()
                item['name'] = table_row.css(self.NAME_SELECTOR).extract_first()
                item['size'] = table_row.css(self.SIZE_SELECTOR).extract_first()
                item['md5'] = table_row.css(self.MD5_SELECTOR).extract_first()
                item['next'] = table_row.css(self.NEXT_DIRECTORY_SELECTOR).extract_first()
                item['file_urls'] = [file_url]
                yield item

            else:
                yield {
                    'name': table_row.css(self.NAME_SELECTOR).extract_first(),
                    'size': table_row.css(self.SIZE_SELECTOR).extract_first(),
                    'md5': table_row.css(self.MD5_SELECTOR).extract_first(),
                    'next': table_row.css(self.NEXT_DIRECTORY_SELECTOR).extract_first(),
                }
