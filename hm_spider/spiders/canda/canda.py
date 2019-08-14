import re

import scrapy
from scrapy.http import HtmlResponse
import json

from hm_spider.base.spiders import BaseRedisSpider
from hm_spider.items import HMProductItem


class CandaSpider(BaseRedisSpider):
    name = 'canda'
    allowed_domains = ['www.canda.cn']
    domain_url = 'http://www.canda.cn'
    code_prefix = "ca-"
    start_urls = [
        'http://www.canda.cn/women.html',
        'http://www.canda.cn/men.html',

        'http://www.canda.cn/boys.html',
        'http://www.canda.cn/girls.html',
        'http://www.canda.cn/male-baby.html',
        'http://www.canda.cn/female-baby.html',

        'http://www.canda.cn/acc-women.html',
        'http://www.canda.cn/acc-men.html',
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 1
    }

    def parse(self, response: HtmlResponse):
        if response.text and (re.search(r'\d+.html', response.url) or
                              re.search(r'catalog/product/view/id/\d+', response.url)):
            self.log_record_before(response)
            for p in self.parse_detail_data(response):
                yield p
        self.logger.info(f'parser url: {response.url}')
        if response.url in self.start_urls:
            for url in self.parse_page_url(response):
                yield scrapy.Request(url, callback=self.parse)
        for url in self.get_detail_urls(response):
            if not response.text and (re.search(r'\d+.html', response.url) or
                                      re.search(r'catalog/product/view/id/\d+', response.url)):
                continue
            yield scrapy.Request(url, callback=self.parse)

    def parse_detail_data(self, response: HtmlResponse):
        rl = re.findall(r'var spConfig = new Product.Config\((.*?)\);\n', response.text)
        if not rl or len(rl) <= 0:
            return
        try:
            data = json.loads(rl[0])
        except Exception as e:
            self.logger.exception(e)
            self.log_record_after(response.url, error=e)
            return
        colors = self.get_colors(data)
        c_name = self.get_category(response.url)
        # 不同颜色为一个商品
        for color in colors:
            p = HMProductItem(html=response.text.encode('utf8', 'ignore'), source_url=response.url)
            p['code'] = self.code_prefix+data['productId'] + '-' + color['id']
            p['name'] = data['productName']
            p['raw_products'] = data
            p['group_code'] = data['productId']
            p['category'] = {'name': c_name, 'href': ''}
            p["price"] = float(color['price'])
            p['white_price'] = float(color['white_price'])
            p['img_urls'] = color['img_urls']
            p['size_select'] = color['sizes']
            p['size_valid'] = color['ava_sizes']
            # p['desc'] = data['productDetail']['productDesc']
            p['detail'] = {'composition': '', 'detailed': data['shortDescription']}
            p['delivery'] = ''
            p['tags'] = self.get_tags(response)
            p['other_style'] = self.get_other_style(colors, data['productId'])
            p['gender'] = self.get_gender(p['name'], p['tags'])
            yield p
        self.log_record_after(response.url)

    @staticmethod
    def get_colors(data: dict):
        attributes = data['attributes']
        colors = []
        for key in attributes.keys():
            if 'color' == attributes[key]['code'].split('_')[0]:
                color_key = key
                size_key = str(int(key)+1)
                for c_option in attributes[color_key]['options']:
                    sizes = []
                    color = dict()
                    color['name'] = c_option['label']
                    color['id'] = c_option['id']
                    color['category'] = {'name': attributes[key]['label'].split('-')[1], 'href': ''}
                    # 查询pid对应的尺码
                    ava_p_ids = list()
                    for p_id in c_option['products']:
                        for s_option in attributes[size_key]['options']:
                            if p_id in s_option['products']:
                                ava_p_ids.append(p_id)
                            sizes.append({'sizeCode': s_option['id'], 'size': '', 'name': s_option['label']})
                    color['sizes'] = sizes
                    color['ava_sizes'] = {'availability': ava_p_ids, 'fewPieceLeft': []}
                    color['icon'] = data['childProducts'][p_id]['icon']
                    color['price'] = data['childProducts'][p_id]['finalPrice']
                    color['white_price'] = data['childProducts'][p_id]['price']
                    imgs = list()
                    for img in data['childProducts'][p_id]['imageUrl']:
                        imgs.append({
                            'thumbnail': img['url'],
                            'image': img['url'],
                            'fullscreen': img['url'],
                        })
                    color['img_urls'] = imgs
                    colors.append(color)
            return colors

    def get_other_style(self, colors: list, pid: str):
        os = dict()
        for color in colors:
            code = self.code_prefix + str(pid) + '-' + str(color['id'])
            os[code] = {'color': color['name'], 'color_code': '', 'img': color['icon']}
        return os

    @staticmethod
    def get_tags(response: HtmlResponse):
        tags = list()
        for t_name in response.xpath("//div[@class='main']/div[@class='breadcrumbs']/ul/"
                                     "li[contains(@class,'category')]/a/text()").extract():
            tag = {'name': str(t_name), 'href': ''}
            tags.append(tag)
        return tags

    @staticmethod
    def parse_page_url(response: HtmlResponse):
        total = response.xpath("//div[@class='toolbar_c']/p/strong/text()").extract_first().split(' ')[0]
        # 总共页数
        total_page = int(total) // 10 + 1
        for p in range(1, total_page):
            yield response.url + '?ajax-pager=1&p=' + str(p)

    def get_category_by_url(self, url: str):
        if 'women' in url:
            return self.WOMAN
        elif 'men' in url:
            return self.MAN
        elif 'female-baby' in url:
            return self.FEMALE_BABY
        elif 'male-baby' in url:
            return self.MALE_BABY
        elif 'girl' in url:
            return self.GIRL
        elif 'boy' in url:
            return self.BOY
        else:
            return self.OTHER

    def get_detail_urls(self, response: HtmlResponse):
        c_name = self.get_category_by_url(response.url)
        for url in response.xpath("//li/div[@class='product-image']/a[@class='pimg a_blank']/@href").extract():
            if '?' in url:
                url = url + '&tag_category=' + c_name
            else:
                url = url + '?tag_category=' + c_name
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
