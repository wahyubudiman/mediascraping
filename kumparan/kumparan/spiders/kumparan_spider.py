import scrapy
from scrapy.selector import Selector
from bs4 import BeautifulSoup
from scrapy.http.request import Request
from kumparan.items import InaprocItem


class KumparanSpider(scrapy.Spider):
    name = "inaproc"
    allowed_domains = ["kumparan.com"]
#    start_urls = [
#        "https://kumparan.com/search/kekeringan/",
#    ]

    def start_requests(self):
        urlInaproc = "https://kumparan.com/search/kekeringan/"
        for i in range(1, 1001):
            newUrl = urlInaproc + str(i)
            yield scrapy.Request(url = newUrl, callback = self.parse)

    def parse(self, response):
        """ This function parses a property page.

#        @url https://www.kompas.com/tag/kekeringan
        @returns items
        """

        indeks = Selector(response).xpath('//div[contains(@id, "modal-")]/div')

        for indek in indeks:
            item = InaprocItem()
##            news_url = indek.xpath('div[@class="article__list__title"]/h3/a/@href').extract_first()
##            news_link = news_url + "?page=all"
            item['kegiatan'] = indek.xpath('.//tr[td/text() = "Kegiatan"]/td[2]/text()').extract_first()
##            item['link'] = news_link
            item['tahun'] = indek.xpath('.//tr[td/text() = "Tahun Anggaran"]/td[2]/text()').extract_first()
            item['pagu'] = indek.xpath('.//tr[td/text() = "Pagu"]/td[2]/div[@class="ui label green"]/text()').extract_first()
            item['sumber'] = indek.xpath('.//tr[td/text() = "Sumber Dana"]/td[2]/text()').extract_first()
            item['desc'] = indek.xpath('.//tr[td/text() = "Deskripsi"]/td[2]/text()').extract_first()

#            detail_request = Request(news_link, callback=self.parse_detail)
#            detail_request.meta['item'] = item
#            yield detail_request
            yield item


#    def parse_detail(self, response):
#        print("Crawling detail news")
#        item = response.meta['item']
#        selector = Selector(response)
#        description = selector.xpath('//div[@class="read__content"]').extract_first()
#        item['desc'] = BeautifulSoup(description).text
#        return item

