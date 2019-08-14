from urllib import parse
import requests
import json
import time

import scrapy
from scrapy.http import HtmlResponse

from hm_spider.base.spiders import BaseRedisSpider
from hm_spider.items import HMProductItem


class OnlySpider(BaseRedisSpider):
    name = 'only'
    allowed_domains = ['www.only.cn', 'cdn.bestseller.com.cn']
    domain_url = 'http://www.only.cn'
    code_prefix = "ol-"
    detail_data_url = "https://cdn.bestseller.com.cn/detail/ONLY/{}.json"
    ajax_domain = "https://cdn.bestseller.com.cn"
    token_url = "https://www.only.cn/api/service/init?channel=6"
    page_data_url = 'https://www.only.cn/api/goods/goodsList?classifyIds=114762&currentpage={}' \
                    '&goodsHighPrice=&goodsLowPrice=&goodsSelect=&sortDirection=desc&sortType=1'
    start_url = 'https://www.only.cn/'
    start_urls = [
        'https://www.only.cn/'
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 2
    }

    @classmethod
    def get_token(cls):
        token = getattr(cls, '_token', None)
        if not token:
            jr = requests.get(cls.token_url).json()
            token = jr['data']['token']
            setattr(cls, '_token', token)
        return cls._token

    def parse(self, response: HtmlResponse):
        if ('detail' in response.url) and ('json' in response.url):
            self.log_record_before(response)
            for p in self.parse_detail_data(response):
                yield p
        self.logger.info(f'parser url: {response.url}')
        if self.start_url == response.url:
            for url in self.parse_page_urls(response):
                headers = {'token': self.get_token()}
                yield scrapy.Request(url, callback=self.parse, headers=headers)
        if ('goodsList' in response.url) and ('currentpage' in response.url):
            for url in self.parse_detail_urls(response):
                yield scrapy.Request(url, callback=self.parse)

    def parse_detail_data(self, response: HtmlResponse):
        data = json.loads(str(response.text)).get('data', None)
        if not data:
            return
        for color in data['color']:
            if color['status'] == 'OutShelf':
                continue
            source_url = "https://www.only.cn/goodsDetails.html?design="+data['projectCode']
            p = HMProductItem(source_url=source_url)
            p['code'] = self.code_prefix + color['colorCode']
            p['name'] = data['goodsName']
            p['raw_products'] = data
            p['group_code'] = data['projectCode']
            # only站只有女士服饰
            p['category'] = {'name': self.WOMAN, 'href': ''}
            p["price"] = float(color['price'])
            p['white_price'] = float(color['originalPrice'])
            p['img_urls'] = self.get_img_urls(color)
            p['size_select'], p['size_valid'] = self.get_sizes(color, data['projectCode'])
            p['desc'] = data['describe']
            p['detail'] = {'composition': '', 'detailed': data['goodsInfo']}
            p['delivery'] = ''
            p['tags'] = self.get_tags(color)
            p['other_style'] = self.get_other_style(data['color'])
            # only站只有女性服饰
            p['gender'] = 'female'
            yield p
        self.log_record_after(response.url)

    @staticmethod
    def get_tags(color: dict):
        tags = color['classifyNames'].split(',')
        tags.append(color['categoryName'])
        tags.remove('')
        return tags

    def get_img_urls(self, color: dict):
        imgs = list()
        for img_url in color['picurls']:
            img = self.ajax_domain + img_url
            imgs.append({
                'thumbnail': img,
                'image': img,
                'fullscreen': img
            })
        return imgs

    def get_sizes(self, color: dict, pid: str):
        url = "https://www.only.cn/api/goods/getStock?goodsCode="+pid+"&type=0"
        header = {'token': self.get_token()}
        data = requests.get(url, headers=header).json()['data']
        sizes = list()
        ava_sizes = dict()
        ava = list()
        for sz in color['sizes']:
            sizes.append({'sizeCode': str(sz['sku']), 'size': '', 'name': sz['sizeAlias']})
            if data[sz['sku']] > 0:
                ava.append(str(sz['sku']))
        ava_sizes['availability'] = ava
        ava_sizes['fewPieceLeft'] = []
        return sizes, ava_sizes

    def get_other_style(self, colors: dict):
        ots = dict()
        for color in colors:
            if color['status'] == 'OutShelf':
                continue
            code = self.code_prefix + color['colorCode']
            ots[code] = {'color': color['color'], 'color_code': '', 'img': self.ajax_domain + color['picurls'][2]}
        return ots

    # 分页url-只生成一次
    def parse_page_urls(self, response: HtmlResponse):
        if self.start_url != response.url:
            yield
        headers = {'token': self.get_token()}
        # 同一请求请求频率不能太高
        data = requests.get(self.page_data_url.format('5'), headers=headers).json()
        time.sleep(2)
        for page in range(1, data['totalPage']+1):
            url = self.page_data_url.format(str(page))
            yield url

    def parse_detail_urls(self, response: HtmlResponse):
        rl = json.loads(str(response.text))
        data = rl.get('data', None)
        urls = list()
        if not data:
            self.logger.warning(msg='详情数据解析错误：'+str(rl)+';url:'+response.url)
        for gs in data:
            urls.append(self.detail_data_url.format(gs['goodsCode']))
        return urls


