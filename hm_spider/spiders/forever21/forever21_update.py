from scrapy.http import HtmlResponse

from hm_spider.spiders.forever21.forever21 import ForeverSpider


class ForeverUpdateSpider(ForeverSpider):
    name = 'forever21_update'
    start_urls = []

    def parse(self, response: HtmlResponse):
        if response.text and 'Product.aspx' in response.url:
            self.log_record_before(response)
            for p in self.parse_detail_data(response):
                yield p
