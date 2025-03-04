import scrapy
import dateparser
from scrapy.selector import Selector
from bs4 import BeautifulSoup
from scrapy.http.request import Request
from kompas.items import KompasItem


class KompasSpider(scrapy.Spider):
    name = "kompas"
    allowed_domains = ["kompas.com"]
#    start_urls = [
#        "https://www.kompas.com/tag/kekeringan",
#    ]
    
    def start_requests(self):
#        urlInaproc = "https://www.kompas.com/tag/ibu-kota-baru/desc/"
        urlInput = "https://www.kompas.com/tag/"
        urlInaproc = urlInput + self.hashtag + "/desc/"
        for i in range(1, 100):
            newUrl = urlInaproc + str(i)
            yield scrapy.Request(url = newUrl, callback = self.parse)

    def parse(self, response):
        """ This function parses a property page.

#        @url https://www.kompas.com/tag/kekeringan
        @returns items
        """

        indeks = Selector(response).xpath('//div[@class="article__list clearfix"]')

        for indek in indeks:
            item = KompasItem()
            news_url = indek.xpath('div[@class="article__list__title"]/h3/a/@href').extract_first()
            news_link = news_url + "?page=all"
            item['title'] = indek.xpath('div[@class="article__list__title"]/h3/a/text()').extract_first()
            item['link'] = news_link
            item['images'] = indek.xpath('div[@class="article__list__asset clearfix"]/div/img/@src').extract_first()
#            item['category'] = indek.xpath('div[@class="article__list__info"]/div[@class="article__subtitle article__subtitle--inline"]/text()').extract_first()
            item['category'] = self.hashtag
            tanggal = indek.xpath('div[@class="article__list__info"]/div[@class="article__date"]/text()').extract_first()
            item['date'] = dateparser.parse(tanggal).strftime("%Y-%m-%d")
#            item['desc'] = ""
            detail_request = Request(news_link, callback=self.parse_detail)
            detail_request.meta['item'] = item
            yield detail_request

# get the true next pagination link
#        next_page_text = Selector(response).xpath('//div[@class="paging__item"]/a[@class="paging__link paging__link--next"]/text()').extract_first()
#        if next_page_text == "Next":
#            next_page_link = Selector(response).xpath('//div[@class="paging__item"]/a[@rel="next"]/@href').extract_first()
#        else:
#            next_page_link = Selector(response).xpath('//div[@class="paging_item"][4]/a/@href').extract_first()

#        if next_page_link:
#            yield scrapy.Request(
#                response.urljoin(next_page_link),
#                callback=self.parse
#            )

    def parse_detail(self, response):
        print("Crawling detail news")
        item = response.meta['item']
        selector = Selector(response)
        description = selector.xpath('//div[@class="read__content"]').extract_first()
        item['desc'] = BeautifulSoup(description).text
        return item
