# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from hm_spider.base.spiders import BaseRedisSpider
from hm_spider.items import HMProductItem
import re


class CkSpider(CrawlSpider, BaseRedisSpider):
    name = 'ck'
    allowed_domains = ['www.calvinklein.cn']
    domain_url = ['http://www.calvinklein.cn/']
    start_urls = ['http://www.calvinklein.cn/',
                  'https://www.calvinklein.cn/sitemap.xml',
                  'https://www.calvinklein.cn/category/list?tg=newarrival&g=men&pid=1-2#top',
                  'https://www.calvinklein.cn/category/list?tg=newarrival&g=women&pid=1-13#top',
                  'https://www.calvinklein.cn/category/list?f=26-47&tg=newarrival&pid=1-206#top',
                  'https://www.calvinklein.cn/category/list?t=ckjas&tg=newarrival&pid=1-26#top',
                  'https://www.calvinklein.cn/category/list?c=ckj&tg=newarrival&g=women&id=37-40#top',
                  'https://www.calvinklein.cn/category/list?c=cku&tg=newarrival&g=women&id=69-72#top',
                  'https://www.calvinklein.cn/category/list?c=ckp&tg=newarrival&g=women&id=92-95#top',
                  'https://www.calvinklein.cn/category/list?c=ckja&tg=newarrival&g=women&id=114-117#top',
                  'https://www.calvinklein.cn/category/list?c=ckck&tg=newarrival&g=men&id=171-173#top',
                  'https://www.calvinklein.cn/category/list?c=ckck&tg=newarrival&g=women&id=171-174#top'
                  ]

    rules = (
        Rule(LinkExtractor(allow=r'https://www.calvinklein.cn/item/.*'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'/item/.*'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'.*/item/.*'), callback='parse_item', follow=True),
    )

    def get_category_by_url(self, cate: str):
        if '男孩' in cate or '男童' in cate:
            return self.BOY
        elif '男士' in cate or '男子' in cate:
            return self.MAN
        elif '女童' in cate or '女孩' in cate:
            return self.GIRL
        elif '女子' in cate or '女士' in cate:
            return self.WOMAN
        else:
            return self.OTHER

    @staticmethod
    def get_images(response):
        sels = response.xpath("//div[@class='scroll-background-image']/a/img")
        images = []
        for sel in sels:
            images.append({
                'thumbnail': sel.attrib['data-cloudzoom'],
                'fullscreen': sel.attrib['src'],
            })
        return images

    @staticmethod
    def get_size(response):
        sizes = response.xpath("//div[@class='product-select']/div[2]/ul/li")
        size = []
        for sel in sizes:
            size.append({
                'name': sel.xpath('text()').extract_first(),
                'sizeCode': sel.attrib['skuid'],
                'dispalysize': sel.xpath('text()').extract_first()
            })
        return size

    def get_price(self, price):
        pr = re.findall('[0-9].*', price)
        return pr

    def get_code(self, url):
        pr = re.findall('[A-Z0-9]*-[0-9]*', url)
        return pr

    def parse_item(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)
        p = HMProductItem(html=response.text.encode('utf8', 'ignore'), source_url=response.url)
        p['name'] = response.xpath('/html/head/title/text()').extract_first()
        p['gender'] = self.get_gender(p['name'])
        p['code'] = self.get_code(response.url)[0]
        p['group_code'] = self.get_code(response.url)[0]
        price = response.xpath(
            "//div[contains(@class,'product-right-con')]/div[@class='product-price-pdp']/span/text()").extract_first()
        p['price'] = float(self.get_price(price)[0])
        p['white_price'] = float(self.get_price(price)[0])
        p['raw_products'] = {}
        p['size_select'] = self.get_size(response)
        p['size_valid'] = self.get_size(response)
        p['desc'] = response.xpath(
            "/html/body/div[1]/div[2]/div[1]/div[2]/div/div[8]/div[2]/div/div/ul/li/p/text()").extract()
        p['detail'] = {'composition': '', 'detailed': response.xpath(
            "//div[@class='product-selection-box']").extract_first()}
        cate = response.xpath('//div[@class ="bread-crumbs"]/a[3]/text()').extract_first()
        p['category'] = {'name': self.get_category_by_url(cate), 'href': ''}
        p['img_urls'] = self.get_images(response)
        sizes = response.xpath(
            "//div[contains(@class,'product-right-con')]/div[@class='product-color']/ul/li/a/span/img")
        p['other_style'] = []
        for sel in sizes:
            p['other_style'].append({
                p['code']: {
                    'color': sel.attrib['title'], 'color_code': sel.attrib['title'],
                    'img': sel.attrib['src']}})

        return p
