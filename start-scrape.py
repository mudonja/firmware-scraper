#!/bin/etc/env python

import scrapy
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
# base_url="https://archive.openwrt.org/"


class FirmwareItem(scrapy.Item):
    file_urls = scrapy.Field()
    files = scrapy.Field()


class FirmwareSpider(scrapy.Spider):
    name = "firmware_spider"
    #start_urls = ['https://archive.openwrt.org/']
    start_urls = ['https://archive.openwrt.org/attitude_adjustment/12.09/adm8668/generic/']
    custom_settings = {
        'ITEM_PIPELINES': {'scrapy.pipelines.files.FilesPipeline': 1},
        'FILES_STORE': './testresult',
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
            yield {
                'name': table_row.css(self.NAME_SELECTOR).extract_first(),
                'next': table_row.css(self.NEXT_DIRECTORY_SELECTOR).extract_first(),
                'size': table_row.css(self.SIZE_SELECTOR).extract_first(),
                'md5': table_row.css(self.MD5_SELECTOR).extract_first(),
            }

            check_for_size = response.css(self.SIZE_SELECTOR).get()
            # print("SIZE EXISTS:", check_for_size)

            next_page = response.css(self.NEXT_DIRECTORY_SELECTOR).extract_first()
            print("Next Page", next_page)
            if count > 1:
                breakpoint()
            count += 1
            if check_for_size != None and check_for_size == '-':
                print("Going to next link:", response.urljoin(next_page))
                yield scrapy.Request(
                    response.urljoin(next_page),
                    callback=self.parse,
                    dont_filter=True
                )
            elif check_for_size != '-' and 'KB' in check_for_size:
                download = response.urljoin(next_page)
                yield{
                    print("I am going to download: ",download),
                }
            else:
                print("I dont know what to do with this!")
            if self.SIZE_SELECTOR == '-':
                # We descend
                pass
            else:
                # We download
                if self.MD5_SELECTOR != '-':
                    # We save MD5 SUM to be calculated after download is finished
                    pass
                else:
                    # We just download and maybe log
                    pass
                # for link in response.css(...):
                #     pass
                # loader = ItemLoader(item=FirmwareItem(),selector=table_row)
                # relative_url=response.css().extract_first() #change response to link?
                # absolute_url = response.urljoin(relative_url)
                # loader.add_value('file_urls', absolute_url)
                # yield loader.load_item()












