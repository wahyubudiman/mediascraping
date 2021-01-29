import scrapy
import dateparser
from scrapy.selector import Selector
from bs4 import BeautifulSoup
from scrapy.http.request import Request
from tribun.items import TribunItem


class TribunSpider(scrapy.Spider):
    name = "tribun"
    allowed_domains = ["tribunnews.com"]
#    start_urls = [
#        "https://www.kompas.com/tag/kekeringan",
#    ]

#percobaan parsing argument dari commandline
#    urlInput = raw_input("Masukkan Url berdasarkan tag-nya (default kekeringan) : ")
#    def __init__(self, hashtag=None, *args, **kwargs):
#        super(TribunSpider, self).__init__(*args, **kwargs)
#        self.start_urls = ['https://www.tribunnews.com/tag/%s' % hashtag]
#        urlInput = self.start_urls

    def start_requests(self):
#        urlInaproc = "https://www.tribunnews.com/tag/kekeringan?page="
        urlInput = "https://www.tribunnews.com/tag/"
        urlInaproc = urlInput + self.hashtag + "?page="
        for i in range(1, 20):
            newUrl = urlInaproc + str(i)
            yield scrapy.Request(url = newUrl, callback = self.parse)

    def parse(self, response):
        """ This function parses a property page.

#        @url https://www.kompas.com/tag/kekeringan
        @returns items
        """

        indeks = Selector(response).xpath('//li[@class="ptb15"]')

        for indek in indeks:
            item = TribunItem()
            news_url = indek.xpath('div/a/@href').extract_first()
            news_link = news_url + "?page=all"
#            item['title'] = indek.xpath('//div[@class="mr140"]/h3/a/@title').extract_first()
            item['link'] = news_link
            item['images'] = indek.xpath('div/a/img/@src').extract_first()
#            item['category'] = indek.xpath('div[@class="article__list__info"]/div[@class="article__subtitle article__subtitle--inline"]/text()').extract_first()
#            item['date'] = indek.xpath('div/div/time/text()').extract_first()
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
        description = selector.xpath('//div[@class="side-article txt-article"]').extract_first()
        tagar = selector.xpath('//h5[@class="tagcloud3"]/a/text()').extract_first()
        titel = selector.xpath('//h1[@class="f50 black2 f400 crimson"]/text()').extract_first()
        tanggal = selector.xpath('//time[@class="grey"]/text()').extract_first()
        item['desc'] = BeautifulSoup(description).text
        item['category'] = self.hashtag
        item['title'] = titel
        item['date'] = dateparser.parse(tanggal).strftime("%Y-%m-%d")
        return item


class MySpider(scrapy.Spider):
    name = 'myspider'

    def start_requests(self):
        yield scrapy.Request('https://www.kompas.com/tag/%s' % self.category)
