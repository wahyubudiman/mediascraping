import scrapy
import dateparser
import time
import sys
from bs4 import BeautifulSoup
from scrapy.selector import Selector
from scrapy.http.request import Request
from detik.items import DetikItem

# compatibility between python 2 and 3
#try:
#    from urllib.parse import urlparse
#except:
#    from urlparse import urlparse

class DetikSpider(scrapy.Spider):
    name = "detik"
    allowed_domains = ["detik.com"]
#    start_urls = [
#        "http://detik.com/tag/kekeringan",
#    ]

    def start_requests(self):
#        urlInaproc = "https://www.antaranews.com/tag/ibukota-baru/"
        urlInput = "https://www.detik.com/tag/"
        urlInaproc = urlInput + self.hashtag + "/?sortby=time&page="
        for i in range(1, 100):
            newUrl = urlInaproc + str(i)
            yield scrapy.Request(url = newUrl, callback = self.parse)

    def parse(self, response):
        """ This function parses a property page.

#       @url https://www.antaranews.com/tag/kekeringan/
        @returns items
        """

        indeks = Selector(response).xpath('//div[@class="list media_rows list-berita"]/article/a')

        for indek in indeks:
            item = DetikItem()
            news_link = response.urljoin(indek.xpath('@href').extract_first())
            item['title'] = indek.xpath('span/h2/text()').extract_first()
            item['link'] = news_link
            item['images'] = indek.xpath('span/span/img/@src').extract_first()
#            item['category'] = indek.xpath('p[@class="simple-share"]/a/@title').extract_first()
            item['category'] = self.hashtag
#            item['date'] = time.strftime("%d/%m/%Y")
#            item['date'] = indek.xpath('//i[@class="fa fa-clock-o"]/text()').extract_first()
#            item['desc'] = ""
            detail_request = Request(news_link, callback=self.parse_detail)
            detail_request.meta['item'] = item
            yield detail_request

# get the true next pagination link
#        next_page_text = Selector(response).xpath('//ul[@class="pagination pagination-sm"]/li/a[@aria-label="Next"]').extract_first()
#        if next_page_text == "Next":
#            next_page_link = Selector(response).xpath('//ul[@class="pagination pagination-sm"]/li/a[@aria-label="Next"]/@href').extract_first()
#        else:
#            next_page_link = Selector(response).xpath('//ul[@class="pagination pagination-sm"]/li/a[@aria-label="Next"]/@href').extract_first()
#
#        if next_page_link:
#            yield scrapy.Request(
#                response.urljoin(next_page_link),
#                callback=self.parse
#            )


    def parse_detail(self, response):
        print("Crawling detail news")
        item = response.meta['item']
        selector = Selector(response)
#        description = selector.xpath('//div[@id="detikdetailtext"]/text()').extract()
#response.selector.xpath('normalize-space(//div[@class="itp_bodycontent detail_text"])').extract()
        description = selector.xpath('normalize-space(//div[@class="itp_bodycontent detail_text"])').extract()
        tanggal = selector.xpath('//div[@class="jdl"]/div[@class="date"]/text()').extract_first()
#        item['desc'] = BeautifulSoup(description).text
        item['desc'] = description
        item['date'] = dateparser.parse(tanggal).strftime("%Y-%m-%d")
        return item