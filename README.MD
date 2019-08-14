# hm spider 文档

# 项目组成
hm_django: web
hm_spider: 爬虫

# run
web端
```bash
$ pip install -r requirements.txt
$ cd hm_django
$ cp hm_django/settings/locals.py.example hm_django/settings/locals.py # 自己的配置放在locals
$ python manage.py migrate
$ python manage.py createsuperuser
$ python manage.py runserver
```
spider 端
```bash
python main.py
```

# 爬虫调度爬虫
## 爬虫调度是基于celery，django orm调度
新增爬虫， 首次需要运行，需要定时运行的更新爬虫，需要在admin中添加定时任务

## 需要填写的字段
```json 
{
  "name(名称)": "爬虫的名字",
  "Task (registered)": "product.tasks.update_product",
  "interval(Interval)": "和Crontab任选其一， 可参考已有选项",
  "crontab(Crontab)": "和Interval任选其一， 可参考已有选项",
  "args(Arguments)": ["爬虫的名字", ["爬虫初始化url", "url2"]],
  "kwargs(Keyword arguments)": {
      "spider_name": "爬虫名字",
      "urls": []
      }
}
```
- name(名称): 必填
- task: 必填
- crontab | interval: 二选一
- args | kwargs: 二选一

example:
```json
{
  "name": "hm_update",
  "task": "product.tasks.update_product",
  "crontab": "和Interval任选其一， 可参考已有选项",
  "args(Arguments)": ["hm_update", [
            "https://www2.hm.com/zh_cn/sale/ladies/view-all.html",
            "https://www2.hm.com/zh_cn/sale/shopbyproductdivided/view-all.html",
            "https://www2.hm.com/zh_cn/sale/men/view-all.html",
            "https://www2.hm.com/zh_cn/sale/home/view-all.html"
        ]]
}
```

#单元测试
## 运行
## django
hm_django/runtests
```bash
export DJANGO_SETTINGS_MODULE=hm_django.settings
pytest
```


# 测试商品数据
```bash
cd hm_django
python manage.py test_product
-b # 指定品牌(-b hm)
-l # 检测级别(-l warning)选项('debug', 'waring', 'error')

```
# 新增爬虫数据格式
```
name: 商品名称 
gender：性别 （目前版本分类模糊）
code 商品编号或则id 
group_code  分类类别
source_url 商品详情地址
html 商品详情页面源码
white_price 变动价格
price 商品价格  src  浮点型float
raw_products {}相关产品数据包括本身
other-style  其他风格 json格式
img_urls    图片地址 json格式
size_select 型号大全json
size_valid 型号选择json
desc 商品介绍 
detail 商品介绍详细均为html 
category 商品分类 {'href': '', 'name': '男'}
tags:标签分类 

```