# -*- coding: utf-8 -*-
import scrapy
import datetime
import re
import json
from Astock.items import HKBasicDataItem
from Astock.tools import calculate_s,calculate_z,calculate_yi,get_stock


class HkBasicDataApiSpider(scrapy.Spider):
    name = 'HkBasicDataApi'
    allowed_domains = ['stockpage.10jqka.com.cn']
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'Referer': 'http: // stockpage.10jqka.com.cn / realHead_v2.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        },
        'DOWNLOAD_DELAY': '2'
    }

    def __init__(self):
        super(HkBasicDataApiSpider,self).__init__()
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stocks = get_stock('hk_data_source')

    def start_requests(self):
        for i in self.stocks:
            stock_code = i['code']
            stock_market = i['market']
            stock_name = i['name']
            stock_code = stock_code.replace('0', 'HK', 1)
            url = 'http://stockpage.10jqka.com.cn/%s/#gegugp_zjjp' % stock_code
            yield scrapy.Request(url=url, callback=self.parse_next, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name)})

    def parse_next(self,response):
        stock_code,stock_market,stock_name=response.meta.get('info')
        total_equity = response.xpath("//dl[@class='company_details']/dd[1]/text()").get()  # 总股本
        earnper_share = response.xpath("//dl[@class='company_details']/dd[3]/text()").get()  # 每股收益
        url = 'http://d.10jqka.com.cn/v6/realhead/hk_%s/defer/last.js'% stock_code
        yield scrapy.Request(url=url,callback=self.parse_basic_data,dont_filter=True,
                             meta={"info":(stock_code,stock_market,stock_name,total_equity,earnper_share)})

    def parse_basic_data(self,response):
        stock_code, stock_market, stock_name, total_equity, earnper_share = response.meta.get('info')
        b = re.search(r'_last\((.*)\)', response.text)
        b = json.loads(b.group(1))
        tvalue = calculate_yi(b['items']['3541450'],3)  # 总市值
        flowvalue = calculate_yi(b['items']['3475914'],3)  # 流通
        trange = calculate_z(b['items']['526792'],3)  # 振幅
        tchange = calculate_z(b['items']['1968584'],3)  # 换手
        tvaluep = calculate_s(b['items']['592920'],3)  # 市净率
        fvaluep = calculate_s(b['items']['2034120'],3)  # 市盈率
        item = HKBasicDataItem(stock_code=stock_code.replace('HK','0'), stock_market=stock_market, stock_name=stock_name,
                               tvalue=tvalue,flowvalue=flowvalue,trange=trange,tchange=tchange,tvaluep=tvaluep,fvaluep=fvaluep,
                               total_equity=total_equity, earnper_share=earnper_share,crawl_time=self.crawl_time)
        yield item
