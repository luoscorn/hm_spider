import scrapy
from scrapy.http import HtmlResponse

from hm_spider.spiders.forever21.forever21 import ForeverSpider


class ForeverNewSpider(ForeverSpider):
    name = 'forever21_new'
    start_urls = [
        'http://www.forever21.cn/Product/Category.aspx?br=f21&category=whatsnew_all_f21'
    ]

    def parse(self, response: HtmlResponse):
        if response.text and 'Product.aspx' in response.url:
            self.log_record_before(response)
            for p in self.parse_detail_data(response):
                yield p
        self.logger.info(f'parser url: {response.url}')
        if response.text and 'Category.aspx' in response.url and 'whatsnew' in response.url:
            for url in self.parse_page_url(response):
                yield scrapy.Request(url, callback=self.parse)
        for url in response.xpath('//a/@href').extract():
            if url.startswith('#'):
                continue
            if not url.startswith('http'):
                url = self.domain_url + url
            if not url.startswith(self.domain_url + '/Product'):
                continue
            if 'whatsnew' not in url:
                continue
            try:
                yield scrapy.Request(url, callback=self.parse)
            except Exception as e:
                self.logger.exception(e)
