# -*- coding: utf-8 -*-
from scrapy.http import HtmlResponse
import requests
import re
import scrapy
import json
from hm_spider.base.spiders import BaseRedisSpider
from hm_spider.items import HMProductItem


class GapSpider(BaseRedisSpider):
    name = 'gap'
    allowed_domains = ['www.gap.cn']
    domain_url = 'https://www.gap.cn'
    goods_detail_url = 'https://www.gap.cn/gap/rest/productnew'
    goods_category_url = 'https://www.gap.cn/gap/rest/category?cid={}&store_id=1&from=top&customer_group_id=0'
    goods_page_url = 'https://www.gap.cn/gap/rest/category'
    code_prefix = 'gap-'
    start_urls = [
        # 'https://www.gap.cn/gap/rest/category?action=getTopNavs&store_id=1'
        'https://www.gap.cn/gap/rest/category?action=getTreeList&cid=4&store_id=1',
        'https://www.gap.cn/gap/rest/category?action=getTreeList&cid=3&store_id=1',
        'https://www.gap.cn/gap/rest/category?action=getTreeList&cid=6&store_id=1',
        'https://www.gap.cn/gap/rest/category?action=getTreeList&cid=5&store_id=1',
        # # 幼儿
        # 'https://www.gap.cn/gap/rest/category?action=getTreeList&cid=33748&store_id=1',
        # # 婴儿
        # 'https://www.gap.cn/gap/rest/category?action=getTreeList&cid=33758&store_id=1'
    ]

    def parse(self, response: HtmlResponse):
        if response.text and 'productnew' in response.url:
            for p in self.parse_detail_data(response):
                yield p
        self.logger.info(f'parser url: {response.url}')
        if 'getTreeList' in response.url:
            try:
                for url in self.get_product_urls(response):
                    yield scrapy.Request(url, callback=self.parse)
            except Exception as e:
                self.logger.error(msg=e)

    # 解析异步json数据
    def parse_detail_data(self, response: HtmlResponse):
        params = self.get_url_params(response.url)
        pid = params['id'][0]
        c_name = self.get_category(response.url)
        try:
            rs = json.loads(response.text)
        except RuntimeError as e:
            self.log_record_after(response.url, error=e)
            self.logger.error(e)
        if not rs['data']:
            return
        data = rs['data']
        # 商品每一种颜色生成一个商品
        for color in data['colors']:
            source_url = "https://www.gap.cn/category/"+data["rootCategoryId"]+"/product/" + \
                         str(pid)+".html?tag_category=" + c_name
            p = HMProductItem(source_url=source_url)
            p['code'] = self.code_prefix + str(pid) + '-' + str(color['colorsId'])
            p['name'] = data['productName']
            p['raw_products'] = data
            p['group_code'] = pid
            p['category'] = {'name': c_name, 'href': ''}
            p["price"] = float(data['salePrice'])
            p['white_price'] = float(data['price'])
            p['img_urls'] = self.get_img_urls(data['imageList'])
            p['size_select'], p['size_valid'] = self.get_sizes(color['size'])
            p['desc'] = data['productDetail']['productDesc']
            p['detail'] = {'composition': '', 'detailed': data['productDetail']['productFiber']}
            p['delivery'] = data['productDetail']['passMessage']
            p['tags'] = self.get_tags(data)
            p['other_style'] = self.get_other_style(data['colors'], str(pid))
            p['gender'] = self.get_gender(p['name'], p['tags'])
            yield p

    @staticmethod
    def get_img_urls(imgs: list):
        img_list = list()
        if not imgs:
            return
        for ig in imgs:
            img_list.append({
                'thumbnail': ig['productImageUrl'],
                'image': ig['productH5ImageUrl'],
                'fullscreen': ig['productBigImageUrl'],
            })
        return img_list

    # 商品尺寸
    @staticmethod
    def get_sizes(rl: list):
        if not rl:
            return
        sizes = []
        ava_size = dict()
        ava = list()
        i = 1
        for s in rl:
            size = dict()
            size['sizeCode'] = s['sizeId']
            size['size'] = i
            size['name'] = s['sizeNumber']
            sizes.append(size)
            i += 1
            if int(s['inStock']) == 1:
                ava.append(s['sizeId'])
        ava_size['availability'] = ava
        ava_size['fewPieceLeft'] = []
        return sizes, ava_size

    def parse_product_url(self, response):
        params = self.get_url_params(response.url)
        c_name = self.get_category(response.url)
        if not c_name:
            self.logger.warning('url:'+response.url+'缺少tag_category参数')
            return
        data = json.loads(response.text).get('data', None)
        if not data:
            return
        ps = data['categoryProducts']['category_' + params['cid'][0]]['products']
        for p in ps:
            pid = p['productId']
            url = self.goods_detail_url + '?id=' + str(pid) + '&store_id=1&customer_group_id=0&tag_category=' + c_name
            yield url

    @staticmethod
    def get_tags(data: dict):
        tags = list()
        if not data:
            return
        for d in data['categoriesName']:
            if '所有' in str(d):
                continue
            tag = {'name': str(d), 'href': ''}
            tags.append(tag)
        return tags

    def get_other_style(self, colors: list, pid: str):
        os = dict()
        if not colors:
            return
        for color in colors:
            code = self.code_prefix + str(pid) + '-' + str(color['colorsId'])
            os[code] = {'color': color['colorName'], 'color_code': '', 'img': color['colorImageUrl']}
        return os

    def get_product_urls(self, response: HtmlResponse):
        c_name = self.get_category_name(response.url)
        try:
            rl = json.loads(response.text)
        except RuntimeError as e:
            self.logger.error('url：'+response.url+'返回数据不为json')
        try:
            cs = rl.get('data', []).get('categories', [])[1].get('childs')
        except Exception as e:
            self.logger.warning(msg=e)
        for c in cs:
            try:
                cgs = c.get('childs', None)
            except Exception as e:
                self.logger.error(msg=e)
            if not cgs:
                cg_id = c['entity_id']
                product_count = c['product_count']
                for resp in self.get_page_data(cg_id, product_count, c_name):
                    for url in self.parse_product_url(resp):
                        yield url
                continue
            for cg in cgs:
                cg_id = cg['entity_id']
                product_count = cg['product_count']
                for resp in self.get_page_data(cg_id, product_count, c_name):
                    for url in self.parse_product_url(resp):
                        yield url

    def get_page_data(self, cid, total_num, c_name):
        params = dict()
        params['cid'] = cid
        params['action'] = 'getCategoryProduct'
        params['page'] = '1'
        params['store_id'] = '1'
        params['platform'] = 'pc'
        params['allCategoryId'] = cid
        params['lastCategoryId'] = cid
        params['lastCategoryDisplayNum'] = '0'
        params['haveDisplayAllCategoryId'] = cid
        params['lastCategoryTotalNum'] = total_num
        params['customer_group_id'] = '0'
        params['tag_category'] = c_name

        total_page = int(total_num)//60 + 1
        for page in range(1, total_page+1):
            params['page'] = page
            params['lastCategoryDisplayNum'] = 60 * (page - 1)
            resp = requests.get(self.goods_page_url, params)
            yield resp

    def get_category_name(self, url: str):
        params = self.get_url_params(url)
        cid = params.get('cid', [])[0]
        if cid == '4':
            return self.WOMAN
        elif cid == '3':
            return self.MAN
        elif cid == '5':
            return self.BOY
        elif cid == '6':
            return self.GIRL
        else:
            cid == self.OTHER

    def get_category(self, url: str):
        params = self.get_url_params(url)
        c_name = params.get('tag_category', [])
        if not c_name:
            msg = 'url:' + url + '缺少tag_category参数'
            self.logger.warning(msg)
            self.log_record_after(url, error=msg)
            raise Exception(msg)
        return c_name[0]



