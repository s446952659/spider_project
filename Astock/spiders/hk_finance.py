# -*- coding: utf-8 -*-
import scrapy
import datetime
import json
from Astock.items import HKFinanceItem
from Astock.tools import get_stock


class HKFinanceSpider(scrapy.Spider):
    name = 'HKFinance'
    allowed_domains = ['stockpage.10jqka.com.cn']

    def __init__(self):
        super(HKFinanceSpider, self).__init__()
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stocks = get_stock('hk_data_source')

    def start_requests(self):
        for i in self.stocks:
            stock_code = i['code']
            stock_market = i['market']
            stock_name = i['name']
            stock_code = stock_code.replace('0', 'HK', 1)
            url = 'http://stockpage.10jqka.com.cn/%s/finance/' % stock_code
            yield scrapy.Request(url=url, callback=self.parse_next, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name)})

    def parse_next(self,response):
        stock_code, stock_market, stock_name = response.meta.get('info')
        #利润表
        benefit = response.xpath("//p[@id='benefit']/text()").get()
        benefit_ = json.loads(benefit)
        benefit_title = benefit_["title"]
        benefit_year = benefit_["year"]
        benefit_json ={}
        benefit_json['title']=benefit_title
        benefit_json['year']=benefit_year
        benefit_year = json.dumps(benefit_json,ensure_ascii=False)
        #债务表
        debt = response.xpath("//p[@id='debt']/text()").get()
        debt_ = json.loads(debt)
        debt_title = debt_['title']
        debt_year = debt_['year']
        debt_json = {}
        debt_json['title'] = debt_title
        debt_json['year'] = debt_year
        debt_year = json.dumps(debt_json,ensure_ascii=False)
        #现金表
        cash = response.xpath("//p[@id='cash']/text()").get()
        cash_ = json.loads(cash)
        cash_title = cash_['title']
        cash_year = cash_['year']
        cash_json = {}
        cash_json['title'] = cash_title
        cash_json['year'] = cash_year
        cash_year = json.dumps(cash_json,ensure_ascii=False)
        item = HKFinanceItem(stock_code=stock_code.replace('HK','0'),stock_market=stock_market,stock_name=stock_name,
                             benefit_year=benefit_year,debt_year=debt_year,cash_year=cash_year,crawl_time=self.crawl_time)
        yield item
