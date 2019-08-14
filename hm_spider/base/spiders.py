#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from scrapy.http import HtmlResponse
from scrapy_redis.spiders import RedisSpider

from records.models import SpiderRecord
from urllib import parse


class BaseRedisSpider(RedisSpider):
    domain_url = ''

    MAN = '男'
    WOMAN = '女'
    GIRL = '女孩'
    BOY = '男孩'
    MALE_BABY = '男婴'
    FEMALE_BABY = '女婴'
    OTHER = '其他'

    def setup_redis(self, crawler=None):
        super(BaseRedisSpider, self).setup_redis(crawler)
        for url in self.start_urls:
            self.server.lpush(self.redis_key, url)

    def parse(self, response):
        return super(BaseRedisSpider, self).parse(response)

    @staticmethod
    def log_record_before(response: HtmlResponse):
        """解析详情页之前记录"""
        return SpiderRecord.objects.create(url=response.url, html=response.text.encode('utf8', 'ignore'))

    @staticmethod
    def log_record_after(url, info=None, error=None):
        """解析详情页完成，修改状态"""
        sr = SpiderRecord.objects.filter(url=url).order_by('-created_time').first()
        sr.parse_status = 'fail' if error else 'ok'
        if error:
            sr.error = error
        if info:
            sr.info = info
        sr.save()

    @staticmethod
    def get_gender(name, tags: [[str], [dict]] = None):
        """
        计算性别
        :param name: 商品名
        :param tags: 标签列表，字符串或者 {"name":""}格式
        :return:
        """

        def check_mail(x, d=0):
            if '男' in x or 'male' in x:
                return 2 + d
            return 0

        def check_female(x, d=0):
            if '裙' in x:
                d += 1
            if '女' in x or 'female' in x:
                return 2 + d
            return 0

        male = 0
        female = 0
        male += check_mail(name, 1)
        female += check_female(name, 1)
        if tags:
            for tag in tags:
                if isinstance(tag, dict):
                    tag = tag.get('name')
                male += check_mail(tag)
                female += check_female(tag)

        if male > female:
            return 'male'
        if female > male:
            return 'female'
        return 'other'

    @classmethod
    def check_url(cls, url: str):
        if url.startswith('//'):
            return ''
        url = url.strip('\\').strip('"').strip('\\').strip('/')
        if not url or 'javascript:' in url or url.startswith('#'):
            return ''
        if not url.startswith('http'):
            url = cls.domain_url + url
        if not url.startswith(cls.domain_url):
            return ''
        return url

    # 获取url参数
    @staticmethod
    def get_url_params(url):
        """
        获取url参数
        :param url: url
        :return:
        """
        return parse.parse_qs(parse.urlparse(url).query)
