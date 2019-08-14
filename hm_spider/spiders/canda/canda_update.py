import re

from scrapy.http import HtmlResponse

from hm_spider.spiders.canda.canda import CandaSpider


class CandaUpdateSpider(CandaSpider):
    name = 'canda_update'
    start_urls = [
    ]

    def parse(self, response: HtmlResponse):
        if response.text and (re.search(r'\d+.html', response.url) or re.search(r'catalog/product/view/id/\d+', response.url)):
            self.log_record_before(response)
            for p in self.parse_detail_data(response):
                yield p
