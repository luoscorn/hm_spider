import scrapy
from scrapy.http import HtmlResponse

from hm_spider.spiders.only.only import OnlySpider


class OnlyUpdateSpider(OnlySpider):
    name = 'only_update'
    start_urls = [
    ]

    def parse(self, response: HtmlResponse):
        if 'goodsDetails' in response.url:
            yield scrapy.Request(self.parse_url(response), callback=self.parse)
        if ('detail' in response.url) and ('json' in response.url):
            self.log_record_before(response)
            for p in self.parse_detail_data(response):
                yield p
        self.logger.info(f'parser url: {response.url}')

    def parse_url(self, response: HtmlResponse):
        params = self.get_url_params(response.url)
        design = params.get('design', [])
        # design的值为12位字符串
        if design and len(design[0]) == 12:
            # design前9位是商品id
            pid = design[0][0:9]
            url = self.detail_data_url.format(str(pid))
            return url
