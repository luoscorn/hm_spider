# -*- coding: utf-8 -*-
import scrapy
import json
import scrapy
from scrapy.http import HtmlResponse

from hm_spider.base.spiders import BaseRedisSpider
from hm_spider.items import HMProductItem


class A6ixtySpider(BaseRedisSpider):
    name = '6IXTY'
    allowed_domains = ['www.6ixty8ight.cn']
    start_urls = ['https://www.6ixty8ight.cn/new-arrivals.html?p=']

    def parse(self, response: HtmlResponse):
        if '/new-arrivals/' in response.url:
            yield self.parse_detail_data(response)
        for new_url in response.xpath('//*[@id]/div/div/div/div/div[2]/div/a/@href').extract():
            yield scrapy.Request(new_url, callback=self.parse)

    def add_request(self):
        for i in range(20):
            url = 'https://www.6ixty8ight.cn/new-arrivals.html?p=' + str(i)
            self.server.lpush(self.redis_key, url)

    def setup_redis(self, crawler=None):
        super(A6ixtySpider, self).setup_redis(crawler)
        self.add_request()

    @staticmethod
    def get_images(response):
        images = []
        images.append({
            'thumbnail': response.xpath("/html/head/meta[9]/@content").extract_first(),
            'fullscreen': response.xpath(".//*[@id='image-gallery-zoom']/div/a[1]/img/@src").extract_first(),
        })
        return images

    def parse_detail_data(self, response: HtmlResponse):
        p = HMProductItem(html=response.text.encode('utf8', 'ignore'), source_url=response.url)
        img = self.get_images(response)
        p['name'] = response.xpath('.//*[@id]/div[3]/h1/text()').extract_first()
        p['gender'] = 'female'
        p['code'] = response.xpath('//*[@id="product_addtocart_form"]/div[1]/input[1]/@value').extract_first()
        p['group_code'] = response.xpath(".//*[@id='product_addtocart_form']/div[3]/p/text()").extract_first()
        p['price'] = float(response.xpath(
            "//*[@id='product_addtocart_form']/div[3]/div[1]/div/meta[2]/@content").extract_first())
        p['white_price'] = float(response.xpath(
            "//*[@id='product_addtocart_form']/div[3]/div[1]/div/meta[2]/@content").extract_first())
        p['raw_products'] = {}
        p['other_style'] = {
            p['group_code']: {
                'color': '', 'color_code': response.xpath(
                    ".//*[@id='tab-custom']/p[3]").extract_first(),
                'img': response.xpath(".//*[@id='image-gallery-zoom']/div/a[1]/img/@src").extract_first()}
        }
        p['size_select'] = {"name": response.xpath(".//*[@id='tab-custom']/p[last()]/text()").extract_first(),
                            "sizeCode": "", "dispalysize": ""}
        p['size_valid'] = {"name": response.xpath(".//*[@id='tab-custom']/p[last()]/text()").extract_first(),
                           "sizeCode": "", "dispalysize": ""}
        p['desc'] = response.xpath(
            "//div[@class='tabs-group block row-fuild product-collateral']/div/div/p[1]/text()").extract_first()
        p['detail'] = {'composition': '', 'detailed': response.xpath(
            'html/body/div[1]/div[2]/div').extract_first()}
        p['category'] = {'name': self.WOMAN, 'href': ''}
        p['img_urls'] = self.get_images(response)
        return p
