# -*- coding: utf-8 -*-
import scrapy
import json
import scrapy
from scrapy.http import HtmlResponse
import re
from hm_spider.base.spiders import BaseRedisSpider
from hm_spider.items import HMProductItem


# 只爬新品行列 可另外追加url
class Fpspider(BaseRedisSpider):
    name = 'fp'
    allowed_domains = ['www.fiveplus.com']
    start_urls = ['http://www.fiveplus.com/New_In/list-1-36-inventory%20desc-0-0-0-0-0.shtml']

    def parse(self, response: HtmlResponse):
        if '/product/' in response.url:
            yield self.parse_detail_data(response)
        for url in response.xpath("//div[@class = 'chanpin-bar']/div/div/p[1]/a/@href").extract():
            new_url = 'http://www.fiveplus.com' + url
            yield scrapy.Request(new_url, callback=self.parse)

    def add_request(self):
        for i in range(36):
            url = f'http://www.fiveplus.com/New_In/list-{i}-36-inventory%20desc-0-0-0-0-0.shtml'
            self.server.lpush(self.redis_key, url)

    def setup_redis(self, crawler=None):
        super(Fpspider, self).setup_redis(crawler)
        self.add_request()

    @staticmethod
    def get_images(response):
        sels = response.xpath("//div[@class='row']/div/div/img")
        images = []
        for sel in sels:
            images.append({
                'thumbnail': sel.attrib['src'],
                'fullscreen': response.xpath("//div[@class='col-md-6 col-sm-6']/img/@src").extract_first(),
            })
        return images

    @staticmethod
    def get_size(response):
        sizes = response.xpath("//div[@class='col-md-2 col-sm-2 col-xs-2 sizebox']/a")
        size = []
        for sel in sizes:
            size.append({
                'name': sel.attrib['data-id'],
                'sizeCode': sel.xpath("div/a/text()"),
                'dispalysize': response.xpath(
                    "//div[@class='col-md-3 col-sm-3']/ul/li[3]/div[2]/div/a/text()").extract_first(),
            })
        return size

    def get_code(self, url):
        pr = re.findall('[0-9]*-[0-9]*', url)
        return pr

    def parse_detail_data(self, response: HtmlResponse):
        self.logger.info('Hi, your data is my data! %s', response.url)
        p = HMProductItem(html=response.text.encode('utf8', 'ignore'), source_url=response.url)
        p['name'] = response.xpath("//div[@class='container']/div/h2/text()").extract_first().strip().replace(' ',
                                                                                                              '').replace(
            '\n', '').replace('\t', '').replace('\r', '').strip()
        p['gender'] = 'female'
        p['code'] = self.get_code(response.url)[0]
        p['group_code'] = response.xpath("//div[@class = 'col-md-3 col-sm-3']/ul/li/div[2]/div/text()").extract_first()
        p['price'] = float(response.xpath(
            "//div[@class='col-md-3 col-sm-3']/ul/li/h2/@data-list-price").extract_first())
        p['white_price'] = float(response.xpath(
            "//div[@class='col-md-3 col-sm-3']/ul/li/h2/@data-offer-price").extract_first())
        p['raw_products'] = {}
        styles = response.xpath(
            "//div[@class ='col-md-3 col-sm-3']/ul/li/div/div/a/img")
        styless = response.xpath(
            "//div[@class ='col-md-3 col-sm-3']/ul/li/div/div/img")
        p['other_style'] = []
        for sel in styles, styless:
            p['other_style'].append({
                p['code']: {
                    'color': sel.attrib['title'], 'color_code': sel.attrib['title'],
                    'img': sel.attrib['src']}})
        p['size_select'] = {
            "name": response.xpath("//div[@class='col-md-3 col-sm-3']/ul/li[3]/div[2]/div[1]/a/text()").extract_first(),
            "sizeCode": "", "dispalysize": ""}
        p['size_valid'] = {
            "name": response.xpath("//div[@class='col-md-3 col-sm-3']/ul/li[3]/div[2]/div[1]/a/text()").extract_first(),
            "sizeCode": "", "dispalysize": ""}
        p['desc'] = response.xpath(
            "//div[@class = 'row productdesc']/div/dl[1]/dd/text()").extract_first()
        p['detail'] = {'composition': '', 'detailed': response.xpath(
            "//div[@class='col-md-6 col-sm-6 col-xs-12']").extract_first()}
        p['category'] = {'name': self.WOMAN, 'href': ''}
        p['img_urls'] = self.get_images(response)
        a = self.get_size(response)

        return p
