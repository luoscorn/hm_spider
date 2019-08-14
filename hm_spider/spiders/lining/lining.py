# -*- coding: utf-8 -*-
import re
import scrapy
import json
import requests
from scrapy.http import HtmlResponse

from hm_spider.items import HMProductItem
from ...base.spiders import BaseRedisSpider
from urllib import parse


class LiningSpider(BaseRedisSpider):
    name = 'lining'
    allowed_domains = ['store.lining.com', 'www.lining.com']
    domain_url = 'https://store.lining.com'
    goods_detail_url = "https://store.lining.com/ajax/goods_details.html"
    code_prefix = "ln-"
    start_urls = [
        'https://store.lining.com/shop/goodsCate-sale,desc,1,0-0-0-0-1,4s0-0-0-min,max-0.html?tag_category=男',
        'https://store.lining.com/shop/goodsCate-sale,desc,1,0-0-0-0-2,4s0-0-0-min,max-0.html?tag_category=女',
        'https://store.lining.com/shop/goodsCate-sale,desc,1,0-0-0-0-5,3s0-0-0-min,max-0.html?tag_category=男孩',
        'https://store.lining.com/shop/goodsCate-sale,desc,1,0-0-0-0-6,3s0-0-0-min,max-0.html?tag_category=女孩'
    ]

    def parse(self, response: HtmlResponse):
        if response.text and re.search('goods-\d+.', response.url):
            self.log_record_before(response)
            yield self.parse_detail_data(response)
            for url in self.parse_urls(response):
                yield scrapy.Request(url, callback=self.parse)
        self.logger.info(f'parser url: {response.url}')
        if parse.unquote(response.url) in self.start_urls:
            for url in self.parse_page_urls(response):
                yield scrapy.Request(url, callback=self.parse)
        if 'goodsCate' in response.url:
            for url in self.get_detail_urls(response):
                yield scrapy.Request(url, callback=self.parse)

    def parse_detail_data(self, response: HtmlResponse):
        p = HMProductItem(html=response.text.encode('utf8', 'ignore'), source_url=response.url)
        data = re.findall(r'var goods = (.*?)//评价修改', response.text, re.S)
        s = data[0].strip("'").strip().replace("'", '"')
        try:
            detail_data = json.loads(str(self.get_detail_data(s).content, 'utf-8'))
        except Exception as e:
            self.logger.exception(e)
            self.log_record_after(response.url, error=e)
        # code由ln开头 避免重复
        p['code'] = 'ln-'+self.get_v('postID', s)
        p['name'] = self.get_v('goodsName', s)
        p['raw_products'] = detail_data
        p['group_code'] = self.get_v("product_mainID", s)
        p['category'] = {'name': self.get_category(response.url), 'href': ""}
        p["price"] = float(self.get_v("price", s))
        p['img_urls'] = self.get_pics(response)
        p['size_select'], p['size_valid'] = self.get_sizes(detail_data)
        p['white_price'] = float(self.get_v("marketPrice", s))
        p['desc'] = response.xpath("//div[@id='PD_desc_basic']/pre[@class='PD_desc']/span[1]/text()").get()
        p['detail'] = {'composition': '', 'detailed': response.xpath("//div[@id='PD_desc_basic']/pre[@class='PD_desc']").get()}
        p['tags'] = self.get_tags(detail_data)
        p['other_style'], _ = self.get_other_style(response)
        p['gender'] = self.get_gender(p['name'], p['tags'])
        self.log_record_after(response.url)
        return p

    @staticmethod
    def get_v(key, s):
        if not key.strip():
            return
        r = re.findall(r""+key+":.*", s)
        if r and len(r) >= 1:
            kv = r[0].strip(",").split(":")
            if kv and len(kv) == 2:
                return kv[1].strip().strip("\"").strip()
        return

    # 商品尺寸
    @staticmethod
    def get_sizes(data: dict):
        sizes = []
        ava_size = dict()
        ava = list()
        if data['data']:
            rl = data['data']['goodsData']
        i = 1
        if rl:
            for s in rl:
                size = dict()
                size['sizeCode'] = s['goodsID']
                size['size'] = i
                size['name'] = s['spec'].split(" ")[1]
                sizes.append(size)
                i += 1
                if int(s['enableSaleAmount']) > 0:
                    ava.append(s['goodsID'])
            ava_size['availability'] = ava
            ava_size['fewPieceLeft'] = []
        return sizes, ava_size

    @staticmethod
    def get_pics(response: HtmlResponse):
        sel = response.selector
        images = []
        for ig in sel.css(".box img"):
            images.append({
                'thumbnail': ig.attrib['src'],
                'image': ig.attrib['mid'],
                'fullscreen': ig.attrib['big'],
            })
        return images

    def get_detail_data(self, content):
        data = dict()
        data['postID'] = self.get_v('postID', content)
        data['sizeStr'] = self.get_v('sizeStr', content)
        data['asynchStr'] = self.get_v('asynch_goods_str', content)
        data['product_mainID'] = self.get_v('product_mainID', content)
        data['bargainTime'] = self.get_v('bargainTime', content)
        data['flg'] = self.get_v('flg', content)
        data['browseHistory'] = self.get_v('browseHistoryStr', content)
        return requests.post(self.goods_detail_url, data)

    def parse_urls(self, response: HtmlResponse):
        _, urls = self.get_other_style(response)
        return urls

    def parse_page_urls(self, response: HtmlResponse):
        params = self.get_url_params(response.url)
        c_name = params.get('tag_category', [])
        if not c_name:
            self.logger.warning('url'+response.url+'缺少参数：tag_category')
        c_name = c_name[0]
        if c_name == '男':
            total_page_str = response.xpath("//span[@class='paging']/span/text()").extract()[2]
            total_page = int(re.findall(r'\d+', total_page_str)[0])
            for page in range(2, total_page+1):
                url = "https://store.lining.com/shop/goodsCate-sale,desc,"\
                      + str(page)+",0-0-0-0-1,4s0-0-0-min,max-0.html?tag_category=男"
                yield url
        if c_name == '女':
            total_page_str = response.xpath("//span[@class='paging']/span/text()").extract()[2]
            total_page = int(re.findall(r'\d+', total_page_str)[0])
            for page in range(2, total_page + 1):
                url = "https://store.lining.com/shop/goodsCate-sale,desc," \
                      + str(page) + ",0-0-0-0-2,4s0-0-0-min,max-0.html?tag_category=女"
                yield url
        if c_name == '男孩':
            total_page_str = response.xpath("//span[@class='paging']/span/text()").extract()[2]
            total_page = int(re.findall(r'\d+', total_page_str)[0])
            for page in range(2, total_page + 1):
                url = "https://store.lining.com/shop/goodsCate-sale,desc," \
                      + str(page) + ",0-0-0-0-5,3s0-0-0-min,max-0.html?tag_category=男孩"
                yield url
        if c_name == '女孩':
            total_page_str = response.xpath("//span[@class='paging']/span/text()").extract()[2]
            total_page = int(re.findall(r'\d+', total_page_str)[0])
            for page in range(2, total_page + 1):
                url = "https://store.lining.com/shop/goodsCate-sale,desc," \
                      + str(page) + ",0-0-0-0-6,3s0-0-0-min,max-0.html?tag_category=女孩"
                yield url

    def get_other_style(self, response: HtmlResponse):
        os = dict()
        urls = list()
        c_name = self.get_category(response.url)
        for rl in response.css('#choicearea ul li'):
            p_url = rl.xpath('a/@href').extract_first()
            # code由ln开头 避免重复
            code = 'ln-' + re.findall(r'\d+', p_url)[0]
            color_name = rl.xpath('a/@title').extract_first()
            img = rl.xpath('a/img/@src').extract_first()
            os[str(code)] = {'color': color_name, 'color_code': '', 'img': img}
            # 爬取同组商品url
            if '?' in p_url:
                p_url = p_url + '&tag_category=' + c_name
            else:
                p_url = p_url + '?tag_category=' + c_name
            if response.url != self.domain_url + p_url:
                urls.append(self.domain_url+p_url)
        return os, urls

    @staticmethod
    def get_tags(data: dict):
        tags = list()
        data = data['data']
        if not data:
            return
        big_title = data.get('bigTitle', None)
        mid_title = data.get('midTitle', None)
        small_title = data.get('smallTitle', None)
        if big_title:
            tags.append({'name': big_title, 'href': ''})
        if mid_title:
            tags.append({'name': mid_title, 'href': ''})
        if small_title:
            tags.append({'name': small_title, 'href': ''})
        return tags

    def get_detail_urls(self, response: HtmlResponse):
        params = self.get_url_params(response.url)
        c_name = params.get('tag_category', [])
        if not c_name:
            self.logger.warning('url:'+response.url+'缺少tag_category参数')
            return
        c_name = c_name[0]
        for url in response.xpath("//div[@class='selItem']/div[@class='selMainPic']/a/@href").extract():
            if '?' in url:
                url = url+'&tag_category='+c_name
            else:
                url = url+'?tag_category='+c_name
            yield url

    def get_category(self, url: str):
        params = self.get_url_params(url)
        c_name = params.get('tag_category', [])
        if not c_name:
            msg = 'url:' + url + '缺少tag_category参数'
            self.logger.warning(msg)
            self.log_record_after(url, error=msg)
            raise Exception(msg)
        return c_name[0]


