#!/bin/env python

import scrapy
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class MySpider(CrawlSpider):
    name = 'https://archive.openwrt.org/'
    allowed_domains = ['archive.openwrt.org']
    start_urls = ['https://archive.openwrt.org/']

    rules = (
        Rule(LinkExtractor(), callback='parse', follow=True),
    )

    def parse_item(self, response):
        item = {}
        NEXT_DIRECTORY_SELECTOR = '.n a ::attr(href)'
        next_page = response.css(NEXT_DIRECTORY_SELECTOR).extract_first()
        if next_page:
            print("Going to next link:", response.urljoin(next_page))
            yield scrapy.Request(
                response.urljoin(next_page),
                callback=self.parse,
                dont_filter=True
            )
        # item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        # item['name'] = response.xpath('//div[@id="name"]').get()
        # item['description'] = response.xpath('//div[@id="description"]').get()
        return item

    def parse(self, response):
        # filename = 'testresults/' + response.url.split("/")[-2] + '.html'
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        SELECTOR = '.n a ::attr(href)'
        loader = ItemLoader(item=FirmwareItem)
        file_url = response.css(SELECTOR).extract_first()
        file_url_absolute = response.urljoin(file_url)


        item = FirmwareItem()
        item['url']=response.css(SELECTOR).extract_first()
        yield {
            'file_url': file_url_absolute
        }

        # if next_page:
        #     print("Going to next link:", response.urljoin(next_page))
        #     yield scrapy.Request(
        #         response.urljoin(next_page),
        #         callback=self.parse,
        #         dont_filter=True
        #    )
            # yield{
            #     'rel_path': element.css(NEXT_PAGE_SELECTOR).extract_first(),
            # }


class FirmwareItem(scrapy.Item):
    file_urls = scrapy.Field()
    files = scrapy.Field()


