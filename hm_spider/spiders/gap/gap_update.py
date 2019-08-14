import scrapy
from scrapy.http import HtmlResponse

from hm_spider.spiders.gap.gap import GapSpider
import re


class GapUpdateSpider(GapSpider):
    name = 'gap_update'
    start_urls = []

    def parse(self, response: HtmlResponse):
        if response.text and re.search(r'product/\d+.html', response.url):
            ajax_url = self.parse_ajax_url(response.url)
            yield scrapy.Request(ajax_url, callback=self.parse)
        if response.text and 'productnew' in response.url:
            self.log_record_before(response)
            for p in self.parse_detail_data(response):
                yield p

    # 获取商品详情ajax url
    def parse_ajax_url(self, html_url: str):
        pid = re.findall(r'product/(\d+).html', html_url)[0]
        ajax_url = self.goods_detail_url + '?id=' + str(pid) + '&store_id=1&customer_group_id=0'
        return ajax_url
