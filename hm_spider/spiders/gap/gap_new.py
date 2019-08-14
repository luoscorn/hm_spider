import scrapy
from scrapy.http import HtmlResponse

from hm_spider.spiders.gap.gap import GapSpider
import json


# todo 未完成
class GapNewSpider(GapSpider):
    name = 'gap_new'
    start_urls = [
        # 新品
        'https://www.gap.cn/gap/rest/category?action=getTreeList&cid=2387&store_id=1'
    ]

    def parse(self, response: HtmlResponse):
        if response.text and 'productnew' in response.url:
            for p in self.parse_detail_data(response):
                yield p
        self.logger.info(f'parser url: {response.url}')
        if 'getTreeList' in response.url:
            for url in self.get_category_urls(response):
                yield scrapy.Request(url, callback=self.parse)
        if response.url and response.url.startswith(self.domain_url + '/gap/rest/category?cid'):
            for path in self.parse_product_url(response):
                if path:
                    yield scrapy.Request(path, callback=self.parse)

    def get_category_urls(self, response: HtmlResponse):
        try:
            rl = json.loads(response.text)
        except RuntimeError as e:
            self.logger.error('url：'+response.url+'返回数据不为json')
        cs = rl['data']['categories'][0]['childs']
        for c in cs:
            c_name = self.get_category_name(c['entity_id'])
            cgs = c['childs']
            for cg in cgs:
                cg_id = cg['entity_id']
                url = self.goods_category_url.format(cg_id)+'&tag_category=' + c_name
                yield url

    def get_category_name(self, entity_id: str):
        cid = entity_id
        if cid == '2388':
            return self.WOMAN
        elif cid == '2387':
            return self.MAN
        elif cid == '2389'or cid == '34842':
            return self.BOY
        elif cid == '2391' or cid == '34836':
            return self.GIRL
        elif cid == '34836':
            return self.GIRL
        elif cid == '2605':
            return self.FEMALE_BABY
        elif cid == '2604':
            return self.MALE_BABY
        else:
            cid == self.OTHER
