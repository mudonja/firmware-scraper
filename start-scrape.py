#!/bin/etc/env python

import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.files import FilesPipeline
from scrapy import Request
import os


# base_url="https://archive.openwrt.org/"

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
        'LOG_FILE': "/home/imhungry/firmware-scraper/log/logs.txt",
        'ITEM_PIPELINES': {'start-scrape.FirmwarePipeline': 1},
        'FILES_STORE': './testresult',
        'DOWNLOAD_MAXSIZE': 0,
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
        # Element can either be a directory or a downloadable file
        count = 0
        for table_row in response.css('tr'):

            file_url = table_row.css(self.NEXT_DIRECTORY_SELECTOR).get()
            file_url = response.urljoin(file_url)
            if 'KB' not in table_row.css(self.SIZE_SELECTOR).extract_first() and '-' in table_row.css(
                    self.SIZE_SELECTOR).extract_first():
                #print("DIRECTORY", count)
                #print("Going to next link:", response.urljoin(file_url))
                yield scrapy.Request(
                    response.urljoin(file_url),
                    callback=self.parse,
                    dont_filter=True
                )
            elif 'KB' in table_row.css(self.SIZE_SELECTOR).extract_first():
                #print("ITS DOWNLOADABLE", count)
                #print("I will download this!")
                # loader = ItemLoader(item=FirmwareItem())
                item = FirmwareItem()
                item['name'] = table_row.css(self.NAME_SELECTOR).extract_first()
                item['size'] = table_row.css(self.SIZE_SELECTOR).extract_first()
                item['md5'] = table_row.css(self.MD5_SELECTOR).extract_first()
                item['next'] = table_row.css(self.NEXT_DIRECTORY_SELECTOR).extract_first()
                item['file_urls'] = [file_url]
                # item['original_file_name'] = file_url.split('/')[-1]

                # loader.add_value('name', table_row.css(self.NAME_SELECTOR).extract_first())
                # loader.add_value('size', table_row.css(self.SIZE_SELECTOR).extract_first())
                # loader.add_value('md5', table_row.css(self.MD5_SELECTOR).extract_first())
                # loader.add_value('next', table_row.css(self.NEXT_DIRECTORY_SELECTOR).extract_first())
                # loader.add_value('file_url', [file_url])
                yield item
                # yield loader.load_item()
            else:
                print('I dont know what to do with this', count)
                yield {
                    'name': table_row.css(self.NAME_SELECTOR).extract_first(),
                    'size': table_row.css(self.SIZE_SELECTOR).extract_first(),
                    'md5': table_row.css(self.MD5_SELECTOR).extract_first(),
                    'next': table_row.css(self.NEXT_DIRECTORY_SELECTOR).extract_first(),
                }
            # if count > 10:
            #    breakpoint()
            count += 1
            # next_page = response.css(self.NEXT_DIRECTORY_SELECTOR).extract_first()
            # print("Next Page", next_page)
            # check_for_size = response.css(self.SIZE_SELECTOR).extract_first()
            # print("SIZE EXISTS:", check_for_size)

            # if check_for_size == '-':
            #     print("Going to next link:", response.urljoin(next_page))
            #     yield scrapy.Request(
            #         response.urljoin(next_page),
            #         callback=self.parse,
            #         dont_filter=True
            #     )
            # elif check_for_size != '-' and 'KB' in check_for_size:
            #     download = response.urljoin(next_page)
            #     yield {
            #         print("I am going to download: ", download),
            #     }
            # else:
            #     print("I dont know what to do with this!")
            # if self.SIZE_SELECTOR == '-':
            #     print("WOHOOOO")
            # else:
            #     # We download
            #     if self.MD5_SELECTOR != '-':
            #         # We save MD5 SUM to be calculated after download is finished
            #         pass
            #     else:
            #         # We just download and maybe log
            #         pass
            #     # for link in response.css(...):
            #     #     pass
            #     # loader = ItemLoader(item=FirmwareItem(),selector=table_row)
            #     # relative_url=response.css().extract_first() #change response to link?
            #     # absolute_url = response.urljoin(relative_url)
            #     # loader.add_value('file_urls', absolute_url)
            #     # yield loader.load_item()
