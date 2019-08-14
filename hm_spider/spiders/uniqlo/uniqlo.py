#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import re
import requests
import scrapy
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from scrapy.http import HtmlResponse

from hm_spider.base.spiders import BaseRedisSpider
from hm_spider.items import HMProductItem


class UniqloSpider(BaseRedisSpider):
    name = 'uniqlo'
    allowed_domains = ['www.uniqlo.cn']
    domain_url = 'https://www.uniqlo.cn/'
    start_urls = [
        # 'https://www.uniqlo.cn/'
        # 男童
        'https://www.uniqlo.cn/c/1168281801.html',
        # 女童
        'https://www.uniqlo.cn/c/1168281802.html',
        # 婴儿
        'https://www.uniqlo.cn/c/XINSHENGER.html',
        'https://www.uniqlo.cn/c/NANZHUANG.html?rank=overall',
        'https://www.uniqlo.cn/c/NVZHUANG.html',
    ]
    # start_urls = ['https://www.uniqlo.cn/product-detail.html?productCode=u0000000003113']
    # start_urls = ['https://www.uniqlo.cn/c/1446931756.html']
    spu_url = 'https://www.uniqlo.cn/data/products/spu/zh_CN/{code}.json'
    price_url = 'https://d.uniqlo.cn/product/i/product/spu/pc/query/{code}/zh_CN'
    product_url = 'https://www.uniqlo.cn/data/products/zh_CN/{code}.json'
    stock_url = 'https://d.uniqlo.cn/stock/stock/query/zh_CN'
    detail_url = 'https://www.uniqlo.cn/product-detail.html?productCode={code}'
    custom_settings = {
        "DOWNLOAD_DELAY": 1
    }

    def parse(self, response: HtmlResponse):
        match = re.search(r'productCode=(?P<code>u\d+)', response.url)
        if match:
            code = match.groupdict().get('code', None)
            if code:
                self.log_record_before(response)
                for p in self.parse_detail_data(response, code):
                    yield p
        self.logger.info(f'parser url: {response.url}')
        if response.url in self.start_urls:
            self.add_urls(response)

    def add_urls(self, response: HtmlResponse):
        search_url = 'https://d.uniqlo.cn/hmall-sc-service/search/searchWithCategoryCodeAndConditions/zh_CN'
        code = re.search(r'/c/(?P<code>.*).html', response.url).group('code')
        product_count = 0
        c_name = self.get_category_by_url(response.url)
        for p in range(1, 50):
            resp = requests.post(search_url, json={
                'belongTo': 'pc', 'categoryCode': code, 'pageInfo': {'page': p, 'pageSize': 24},
                'priceRange': {'high': 0, 'low': 0}, 'rank': "overall", 'searchFlag': False,
                'url': urlparse(response.url).path
            })
            data = resp.json()
            if data['success']:
                for item in data['resp'][1]:
                    p_code = item['productCode']
                    self.server.lpush(self.redis_key, self.detail_url.format(code=p_code) + '&tag_category=' + c_name)
                product_count += data['resp'][2].get('pageSize', 20)
                if product_count >= data['resp'][2].get('productSum', 1000):
                    break

    @classmethod
    def get_spu_json(cls, code):
        """获取款式，大小的数据"""
        response = requests.get(cls.spu_url.format(code=code))
        if response.status_code == 200:
            return response.json()

    @classmethod
    def get_price_json(cls, code):
        """获取当前价格"""
        response = requests.get(cls.price_url.format(code=code))
        if response.status_code == 200:
            return response.json()['resp'][0]

    def get_stock_json(self, url, code):
        """获取库存量"""
        response = requests.post(self.stock_url, headers={'referer': url, 'content-type': 'application/json'},
                                 json={"type": "DETAIL", "distribution": "EXPRESS", "productCode": code})
        if response.status_code == 200:
            try:
                return response.json()['resp'][0]['skuStocks']
            except Exception as e:
                self.logger.exception(e)
        return {}

    @classmethod
    def get_img_json(cls, code):
        response = requests.get(cls.product_url.format(code=code))
        if response.status_code == 200:
            return response.json()

    @classmethod
    def get_images(cls, img_data, row):
        product_id = row[0]['productId']
        images = [
            {'thumbnail': cls.domain_url[:-1] + img_data['rows'][product_id]['skuPic_285'],
             'fullscreen': cls.domain_url[:-1] + img_data['rows'][product_id]['skuPic_1000']}
        ]

        if len(img_data['main1000']) == len(img_data['main561']):
            for index, pic in enumerate(img_data['main1000']):
                images.append({'thumbnail': cls.domain_url[:-1] + img_data['main561'][index],
                               'fullscreen': cls.domain_url[:-1] + pic})
        return images

    @staticmethod
    def get_size_data(row, stock):
        availability = []
        sizes = []
        for line in row:
            size_code = line['productId']
            sizes.append({
                'name': line.get('styleText', ''),
                'sizeCode': size_code,
                'dispalysize': line.get('sizeText', '')
            })
            if stock.get(size_code) != 0:
                availability.append(size_code)
        return sizes, {'availability': availability}

    def parse_detail_data(self, response: HtmlResponse, code: str):
        data = self.get_spu_json(code)
        summary = data.get('summary', {})
        rows = {}
        other_style = {}
        code = summary.get('productCode')
        for row in data.get('rows', []):
            let_code = f"{code}-{row.get('colorNo')}"
            if let_code not in rows:
                rows[let_code] = []
                img = f'https://www.uniqlo.cn/hmall/test/{code}/sku/40/{row["colorNo"]}.jpg'
                other_style[let_code] = {'color': row.get('style'), 'img': img, 'color_code': row.get('colorNo')}
            rows[let_code].append(row)
        stock = self.get_stock_json(response.url, code)
        price_data = self.get_price_json(code)
        img_data = self.get_img_json(code)

        price_dict = {row['productId']: row for row in price_data['rows']}
        ps = []  # 结果集
        for let_code, row in rows.items():
            product_id = row[0]['productId']
            white_price = float(summary.get('originPrice', 0))
            p = HMProductItem(
                html=response.text.encode('utf8', 'ignore'),
                source_url=response.url,
                name=summary.get('name'),
                code=let_code,
                group_code=code,
                raw_products=data,
                white_price=white_price,
                other_style=other_style,
                price=float(price_dict.get(product_id, {'price': white_price})['price'])
            )
            tags = [summary.get('gDeptValue'), row[0].get('style')]
            p['tags'] = [{'name': tag, 'href': ''} for tag in tags if tag]
            p['category'] = {'name': self.get_category(response.url), 'href': ''}
            p['gender'] = self.get_gender(summary.get('name'), p['tags'])
            p['img_urls'] = self.get_images(img_data, row)
            p['size_select'], p['size_valid'] = self.get_size_data(row, stock)

            instruction = data.get('desc', {}).get('instruction', '')
            p['desc'] = BeautifulSoup(instruction).get_text()
            p['detail'] = {'composition': '', 'detailed': instruction}
            ps.append(p)
        self.log_record_after(response.url)
        return ps

    def get_category_by_url(self,url: str):
        if '1168281801' in url:
            return self.BOY
        elif '1168281802' in url:
            return self.GIRL
        elif 'NANZHUANG' in url or '1448748959' in url:
            return self.WOMAN
        elif 'NVZHUANG' in url or '1448748958' in url:
            return self.MAN
        elif 'XINSHENGER' in url:
            return self.OTHER

    def get_category(self, url: str):
        params = self.get_url_params(url)
        c_name = params.get('tag_category', [])
        if not c_name:
            msg = 'url:' + url + '缺少tag_category参数'
            self.logger.warning(msg)
            self.log_record_after(url, error=msg)
            raise Exception(msg)
        return c_name[0]
