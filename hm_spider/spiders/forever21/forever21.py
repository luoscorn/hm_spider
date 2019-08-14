import scrapy
from scrapy.http import HtmlResponse

from hm_spider.base.spiders import BaseRedisSpider
from hm_spider.items import HMProductItem
from urllib import parse
import requests
import re
import json


# TODO 由于该网站暂时下架 -没有对分类功能进行修改
class ForeverSpider(BaseRedisSpider):
    name = 'forever21'
    allowed_domains = ['www.forever21.cn']
    domain_url = 'http://www.forever21.cn'
    change_color_url = 'http://www.forever21.cn/Ajax/Ajax_Product.aspx'
    code_prefix = 'fv-'
    start_urls = [
        'http://www.forever21.cn/Product/Category.aspx?br=f21&category=whatsnew_all_f21',
        'http://www.forever21.cn/Product/Category.aspx?br=f21&category=bestseller_all',
        'http://www.forever21.cn/Product/Category.aspx?br=f21&category=f21_app',
        'http://www.forever21.cn/Product/Category.aspx?br=f21&category=21men_app',
        'http://www.forever21.cn/Product/Category.aspx?br=f21&category=f21_acc',
        'http://www.forever21.cn/Product/Category.aspx?br=f21&category=f21_shoes',
        'http://www.forever21.cn/Product/Category.aspx?br=f21&category=f21_app_sports',
        'http://www.forever21.cn/Product/Category.aspx?br=f21&category=Promo_gwdj',
        'http://www.forever21.cn/Product/Category.aspx?br=f21&category=sale_all'
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 1
    }

    def parse(self, response: HtmlResponse):
        if response.text and 'Product.aspx' in response.url:
            for p in self.parse_detail_data(response):
                yield p
        self.logger.info(f'parser url: {response.url}')
        if response.text and 'Category.aspx' in response.url:
            for url in self.parse_page_url(response):
                yield scrapy.Request(url, callback=self.parse)
        for url in response.xpath('//a/@href').extract():
            if url.startswith('#'):
                continue
            if not url.startswith('http'):
                url = self.domain_url + url
            if not url.startswith(self.domain_url + '/Product/'):
                continue
            try:
                yield scrapy.Request(url, callback=self.parse)
            except Exception as e:
                self.logger.exception(e)

    def parse_detail_data(self, response: HtmlResponse):
        params = self.get_url_params(response.url)
        detail_data = self.get_detail_data(response)
        # 每种样式/颜色生成一个商品
        sts = self.get_other_style(response)
        if not sts:
            return
        for code in sts.keys():
            p = HMProductItem(html=response.text.encode('utf8', 'ignore'), source_url=response.url)
            color_data = self.get_color_data(code, response)
            p['code'] = code
            p['name'] = detail_data['name']
            gcl = params.get('ProductID', None)
            if not gcl:
                gcl = params.get('productid', None)
            p['group_code'] = gcl[0]
            p['category'] = detail_data['category']
            p["price"] = float(color_data['price'])
            p['white_price'] = float(color_data['white_price'])
            p['img_urls'] = color_data['imgs']
            p['size_select'] = color_data['sizes']
            p['size_valid'] = color_data['ava_sizes']
            p['desc'] = detail_data['desc']
            p['detail'] = detail_data['detail']
            p['delivery'] = detail_data['delivery']
            p['tags'] = detail_data['tags']
            p['other_style'] = self.get_other_style(response)
            p['raw_products'] = {}
            p['gender'] = self.get_gender(p['name'], p['tags'])
            yield p

    def get_other_style(self, response: HtmlResponse):
        os = dict()
        for itm in response.xpath("//ul[@id='ulProductColor']/li"):
            es = re.findall('\(.*\)', itm.xpath('a/@href').extract()[0])[0].strip('\(').strip('\)').split(',')
            color_img = itm.xpath('a/img/@src').extract_first()
            code = self.code_prefix + str(es[1].strip(r'\\\'')) + '-' + str(es[2].strip(r'\\\''))
            os[str(code)] = {'color': es[3].strip(r'\\\''), 'color_code': '', 'img': color_img}
        return os

    @staticmethod
    def get_detail_data(response: HtmlResponse):
        p = dict()
        p['name'] = response.xpath("//div[@class='pdp_title']/h1[@class='item_name_p']/child::text()").extract_first()
        # 获取category
        c_node = response.xpath("//div[@id='div_breadcrumb']/a")
        if len(c_node) > 1:
            c_name = c_node[1].xpath('u/child::text()').extract()
        else:
            c_name = c_node[0].xpath('u/child::text()').extract()
        p['category'] = {'name': c_name[0], 'href': ''}
        # 获取tag
        tags = list()
        for t_name in response.xpath("//div[@id='div_breadcrumb']/a/u/child::text()").extract():
            if t_name == 'Home':
                continue
            tag = {'name': str(t_name), 'href': ''}
            tags.append(tag)
        p['tags'] = tags
        p['desc'] = ''
        p['detail'] = response.xpath("//div[@class='itemdetailcontent']")[0].extract()
        p['delivery'] = response.xpath("//div[@class='center_text event_msg']/text()").extract_first()
        return p

    # 获取各颜色商品信息
    def get_color_data(self, code: str, response: HtmlResponse):
        params = dict()
        params['method'] = 'CHANGEPRODUCTCOLOR'
        ct1 = self.get_url_params(response.url).get('Category', None)
        ct2 = self.get_url_params(response.url).get('category', None)
        if ct1:
            params['category'] = ct1[0]
        elif ct2:
            params['category'] = ct2[0]
        else:
            return
        params['productid'] = code.split('-')[1]
        params['colorid'] = code.split('-')[2]
        rl = requests.get(self.change_color_url, params)
        data = json.loads(rl.text)
        if not data:
            return
        # 获取图片信息
        img_sel = scrapy.Selector(text=data['ProductButtonImageHTML'])
        imgs = list()
        for img in img_sel.xpath('//li/a/img/@src').extract():
            imgs.append({
                'thumbnail': img,
                'image': img,
                'fullscreen': img,
            })
        # 获取价格信息
        price_sel = scrapy.Selector(text=data['ProductListPriceHTML'])
        if price_sel.xpath("//span[@class='price_c original']/child::text()"):
            white_price = price_sel.xpath("//span[@class='price_c original']/child::text()").extract_first().strip('元')
            price = price_sel.xpath("//span[@class='price_c sale']/child::text()").extract_first().strip('元')
        else:
            white_price = re.findall(r'\d+\.\d+', data['ProductListPriceHTML'])[0]
            price = white_price
        # 获取size信息
        size_sel = scrapy.Selector(text=data['ProductSizeHTML'])
        sizes = list()
        ava_sizes = dict()
        i = 1
        size_codes = list()
        for e in size_sel.xpath('//li'):
            size = dict()
            size['sizeCode'] = e.xpath('input/@value').extract_first()
            size['size'] = i
            size['name'] = e.xpath('//li/label/child::text()').extract_first()
            sizes.append(size)
            i += 1
            size_codes.append(size['sizeCode'])
        ava_sizes['availability'] = size_codes
        ava_sizes['fewPieceLeft'] = []
        r_data = dict()
        r_data['white_price'] = white_price
        r_data['price'] = price
        r_data['sizes'] = sizes
        r_data['ava_sizes'] = ava_sizes
        r_data['imgs'] = imgs
        return r_data

    # 处理分页
    @staticmethod
    def parse_page_url(response: HtmlResponse):
        for page in response.xpath("//div[@id='ctl00_MainContent_bottom_filter']/"
                                   "div/span[@class='p_number']/button/@onclick").extract():
            path = re.findall(r'\'.*?\'', page)
            if len(path) <= 0:
                continue
            url = 'http://www.forever21.cn/Product/Category.aspx' + re.findall(r'\'.*?\'', page)[0].strip(r'\\\'')
            yield url

