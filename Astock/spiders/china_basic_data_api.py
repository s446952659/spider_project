# -*- coding: utf-8 -*-
import scrapy
import datetime
import json
import re
from Astock.items import BasicDataItem
from Astock.tools import calculate_yi,calculate_s,calculate_z,get_stock


class ChinaBasicDataApiSpider(scrapy.Spider):
    name = 'ChinaBasicDataApi'
    allowed_domains = ['stockpage.10jqka.com.cn']
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS' : {
            'Referer': 'http: // stockpage.10jqka.com.cn / realHead_v2.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
                },
        'DOWNLOAD_DELAY' : '2'
    }

    def __init__(self):
        super(ChinaBasicDataApiSpider, self).__init__()
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stocks = get_stock('china_data_source')

    def start_requests(self):
        for i in self.stocks:
            stock_code = i['code']
            stock_market = i['market']
            stock_name = i['name']
            url = 'http://d.10jqka.com.cn/v2/realhead/hs_%s/last.js'%stock_code
            yield scrapy.Request(url=url,callback=self.parse_next,dont_filter=True,
                                meta={"info":(stock_code,stock_market,stock_name)})

    def parse_next(self,response):
        stock_code,stock_market,stock_name = response.meta.get('info')
        b = re.search(r'_last\((.*)\)', response.text)
        b = json.loads(b.group(1))
        tvalue = calculate_yi(b['items']['3541450'],2) # 总市值
        flowvalue = calculate_yi(b['items']['3475914'],2) # 流通
        trange = calculate_z(b['items']['526792'],2) # 振幅
        tchange = calculate_z(b['items']['1968584'],2) # 换手
        tvaluep = calculate_s(b['items']['592920'],2) # 市净率
        fvaluep = calculate_s(b['items']['2034120'],2) # 市盈率
        item = BasicDataItem(stock_code=stock_code, stock_market=stock_market, stock_name=stock_name,
                               trange=trange,tchange=tchange,tvalue=tvalue,tvaluep=tvaluep,
                               flowvalue=flowvalue,fvaluep=fvaluep,crawl_time=self.crawl_time)
        yield item


