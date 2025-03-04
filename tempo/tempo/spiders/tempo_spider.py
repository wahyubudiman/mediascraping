import scrapy
import dateparser
from bs4 import BeautifulSoup
from scrapy.selector import Selector
from scrapy.http.request import Request
from tempo.items import TempoItem


class VivaSpider(scrapy.Spider):
    name = "tempo"
    allowed_domains = ["tempo.co"]
#    start_urls = [
#        "https://www.tempo.co/tag/kekeringan",
#    ]

    def start_requests(self):
#        urlInaproc = "https://www.antaranews.com/tag/ibukota-baru/"
        urlInput = "https://www.tempo.co/tag/"
        urlInaproc = urlInput + self.hashtag + "/"
        yield scrapy.Request(url = urlInaproc, callback = self.parse)
#        for i in range(1, 2):
#            newUrl = urlInaproc + str(i)
#            yield scrapy.Request(url = newUrl, callback = self.parse)

    def parse(self, response):
        """ This function parses a property page.

        @url https://www.tempo.co/tag/kekeringan
        @returns items
        """

        indeks = Selector(response).xpath('//ul[@class="wrapper"]/li')

        for indek in indeks:
            item = TempoItem()
            news_link = indek.xpath('div/div/a[2]/@href').extract_first()
            item['title'] = indek.xpath('div/div/a[2]/h2/text()').extract_first()
            item['link'] = news_link
            item['images'] = indek.xpath('div/div/a[1]/img/@src').extract_first()
            item['category'] = self.hashtag
            tanggal = indek.xpath('div/div/a[2]/span/text()').extract_first()
            item['date'] = dateparser.parse(tanggal).strftime("%Y-%m-%d") 
            detail_request = Request(news_link, callback=self.parse_detail)
            detail_request.meta['item'] = item
            yield detail_request
    
    def parse_detail(self, response):
        print("Crawling detail news")
        item = response.meta['item']
        selector = Selector(response)
        description = selector.xpath('//article').extract_first()
        item['desc'] = BeautifulSoup(description).text
        return item
