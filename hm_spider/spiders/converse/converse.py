# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from hm_spider.base.spiders import BaseRedisSpider
from hm_spider.items import HMProductItem
import re


class CharkSpider(CrawlSpider, BaseRedisSpider):
    name = 'chark'
    allowed_domains = ['www.converse.com.cn']
    domain_url = ['http://www.converse.com.cn/']
    start_urls = [
        'http://www.converse.com.cn/',
        'https://www.converse.com.cn/men/category.htm?iid=tpnvmc0601201501',
        'https://www.converse.com.cn/women/category.htm?iid=tpnvfc0601201502',
        'https://www.converse.com.cn/kids/category.htm?iid=tpnvkc0601201503',
        'https://www.converse.com.cn/sitemap.xml',
        'https://www.converse.com.cn/all_star/764279C222/item.htm']

    rules = (
        Rule(LinkExtractor(allow=r'.*/item.htm'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'.*/detail.htm.*'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'.*/item.htm.*'), callback='parse_item', follow=True),
    )

    def get_price(self, price):
        pr = re.findall('[0-9].*', price)
        return pr

    def get_category_by_url(self, cate: str):
        if '男的' in cate:
            return self.MAN
        elif '男女同款' in cate:
            return self.OTHER
        elif '女的' in cate:
            return self.WOMAN
        elif '大童' in cate or '儿童' in cate or '小童' in cate:
            return self.MALE_BABY
        elif '婴幼儿' in cate:
            return self.MALE_BABY
        else:
            return self.OTHER

    @staticmethod
    def get_images(response):
        sels = response.xpath("//div[@class='datail-product-img']/div[3]/a")
        images = []
        for sel in sels:
            images.append({
                'thumbnail': 'https:' + sel.attrib['data-img'],
                'fullscreen': 'https:' + response.xpath("//div[@class='datail-product-img']/div/a/div/img/@src").extract_first(),
            })
        return images

    def parse_item(self, response):
        self.logger.info('Hi, your data is my data! %s', response.url)
        p = HMProductItem(html=response.text.encode('utf8', 'ignore'), source_url=response.url)
        p['name'] = response.xpath("//div[@class = 'content']/div/div[1]/h1/span/text()").extract_first()
        p['gender'] = self.get_gender(p['name'])
        p['code'] = response.xpath(
            '//*[@id="skuCode"]/@value').extract_first()
        p['group_code'] = response.xpath(
            '//*[@id="skuCode"]/@value').extract_first()
        price = response.xpath(
            "//div[@class = 'content']/div/div[1]/div/span[2]/text()").extract_first()
        p['price'] = float(self.get_price(price)[0])
        p['white_price'] = float(self.get_price(price)[0])
        p['raw_products'] = {}
        styles = response.xpath(
            "//div[@class ='content']/div[3]/div/a/img")
        p['other_style'] = []
        for sel in styles:
            p['other_style'].append({
                p['code']: {
                    'color': sel.attrib['title'], 'color_code': sel.attrib['title'],
                    'img': 'https:' + sel.attrib['src']}})
        p['size_select'] = {
            "name": response.xpath(
                "//div[@class = 'content']/div/div/div[2]/div/div/select/option/@status").extract_first(),
            "sizeCode": response.xpath(
                "//div[@class = 'content']/div/div/div[2]/div/div/select/option/@skusize").extract_first(),
            "dispalysize": ""}
        p['size_valid'] = {
            "name": response.xpath(
                "//div[@class = 'content']/div/div/div[2]/div/div/select/option/@status").extract_first(),
            "sizeCode": response.xpath(
                "//div[@class = 'content']/div/div/div[2]/div/div/select/option/@skusize").extract_first(),
            "dispalysize": ""}
        p['desc'] = response.xpath("//div[@class='content']/div/div/li/text()").extract_first()
        p['detail'] = {'composition': '', 'detailed': response.xpath(
            "//div[@class='content']/div").extract_first()}
        cate = response.xpath("//div[@class = 'content']/div/div[1]/h1/span/text()").extract_first()
        p['category'] = {'name': self.get_category_by_url(cate), 'href': ''}
        p['img_urls'] = self.get_images(response)

        return p
