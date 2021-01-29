import scrapy
import time
import sys
import dateparser
from bs4 import BeautifulSoup
from scrapy.selector import Selector
from scrapy.http.request import Request
from antara.items import AntaraItem


class AntaraKeringSpider(scrapy.Spider):
    name = "antarakering"
    allowed_domains = ["antaranews.com"]
#    start_urls = [
#        "https://www.antaranews.com/tag/kekeringan/",
#    ]

    def start_requests(self):
        urlInaproc = "https://www.antaranews.com/tag/kekeringan/"
        for i in range(1, 500):
            newUrl = urlInaproc + str(i)
            yield scrapy.Request(url = newUrl, callback = self.parse)

    def parse(self, response):
        """ This function parses a property page.

#       @url https://www.antaranews.com/tag/kekeringan/
        @returns items
        """

        indeks = Selector(response).xpath('//div[@class="simple-thumb"]/a')

        for indek in indeks:
            item = AntaraItem()
            news_link = response.urljoin(indek.xpath('@href').extract_first())
            item['title'] = indek.xpath('@title').extract_first()
            item['link'] = news_link
            item['images'] = indek.xpath('/picture/img/@src').extract_first()
#            item['category'] = indek.xpath('p[@class="simple-share"]/a/@title').extract_first()
            item['category'] = "kekeringan"
#            item['date'] = time.strftime("%d/%m/%Y")
#            item['date'] = indek.xpath('//i[@class="fa fa-clock-o"]/text()').extract_first()
#            item['desc'] = ""
            detail_request = Request(news_link, callback=self.parse_detail)
            detail_request.meta['item'] = item
            yield detail_request

# get the true next pagination link
        next_page_text = Selector(response).xpath('//ul[@class="pagination pagination-sm"]/li/a[@aria-label="Next"]').extract_first()
        if next_page_text == "Next":
            next_page_link = Selector(response).xpath('//ul[@class="pagination pagination-sm"]/li/a[@aria-label="Next"]/@href').extract_first()
        else:
            next_page_link = Selector(response).xpath('//ul[@class="pagination pagination-sm"]/li/a[@aria-label="Next"]/@href').extract_first()

        if next_page_link:
            yield scrapy.Request(
                response.urljoin(next_page_link),
                callback=self.parse
            )


    def parse_detail(self, response):
        print("Crawling detail news")
        item = response.meta['item']
        selector = Selector(response)
        description = selector.xpath('//div[@class="post-content clearfix"]').extract_first()
        tanggal = selector.xpath('//span[@class="article-date"]/text()').extract_first()
        item['desc'] = BeautifulSoup(description).text
        item['date'] = dateparser.parse(tanggal).strftime("%Y-%m-%d")
        return item
