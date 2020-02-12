# -*- coding: utf-8 -*-
import scrapy
import datetime
from Astock.items import XueqiuFinanceBenifitItem,XueqiuFinanceCashItem,XueqiuFinanceDebtItem
from Astock.tools import get_cookies,get_stock


class ChinaXueqiuFinanceSpider(scrapy.Spider):
    name = 'ChinaXueqiuFinance'
    allowed_domains = ['stock.xueqiu.com']
    handle_httpstatus_list = [302]

    def __init__(self):
        super(ChinaXueqiuFinanceSpider, self).__init__()
        self.cookies = get_cookies()# 获取接口cookies
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stocks = get_stock('china_data_source')

    def start_requests(self):
        for i in self.stocks:
            stock_code = i['code']
            stock_market = i['market']
            stock_name = i['name']
            if stock_market == '1101':
                stock_code = 'SH' + stock_code
            else:
                stock_code = 'SZ' + stock_code
            debt_report_url = 'https://stock.xueqiu.com/v5/stock/finance/cn/balance.json?symbol=%s&type=all&is_detail=true&count=200'%stock_code
            yield scrapy.Request(url=debt_report_url, callback=self.parse_debt_report, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name)})
            benifit_report_url = 'https://stock.xueqiu.com/v5/stock/finance/cn/income.json?symbol=%s&type=all&is_detail=true&count=200' % stock_code
            yield scrapy.Request(url=benifit_report_url, callback=self.parse_benifit_report, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name)})
            cash_report_url = 'https://stock.xueqiu.com/v5/stock/finance/cn/cash_flow.json?symbol=%s&type=all&is_detail=true&count=200' % stock_code
            yield scrapy.Request(url=cash_report_url, callback=self.parse_cash_report, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name)})

    #资产负债按期报告
    def parse_debt_report(self, response):
        stock_code,stock_market,stock_name = response.meta.get('info')
        debt_report = response.text
        debt_year_url = 'https://stock.xueqiu.com/v5/stock/finance/cn/balance.json?symbol=%s&type=Q4&is_detail=true&count=50'%stock_code
        yield scrapy.Request(url=debt_year_url, callback=self.parse_debt_year, dont_filter=True,
                             meta={"info":(stock_code,stock_market,stock_name,debt_report)})

    #资产负债按年度报告
    def parse_debt_year(self,response):
        stock_code,stock_market,stock_name,debt_report=response.meta.get("info")
        debt_year = response.text
        debt_quarter_url = 'https://stock.xueqiu.com/v5/stock/finance/cn/balance.json?symbol=%s&type=S0&is_detail=true&count=150'%stock_code
        yield scrapy.Request(url=debt_quarter_url, callback=self.parse_debt_quarter, dont_filter=True,
                             meta={"info":(stock_code,stock_market,stock_name,debt_report,debt_year)})

    #资产负债按季度报告
    def parse_debt_quarter(self,response):
        stock_code,stock_market,stock_name,debt_report,debt_year = response.meta.get("info")
        debt_quarter = response.text
        item = XueqiuFinanceDebtItem(stock_code=stock_code[2:],stock_market=stock_market,stock_name=stock_name,
                                     debt_report=debt_report,debt_year=debt_year,debt_quarter=debt_quarter,
                                     crawl_time=self.crawl_time)
        yield item

    #利润
    def parse_benifit_report(self,response):
        stock_code, stock_market, stock_name = response.meta.get("info")
        benifit_report = response.text
        benifit_year_url = 'https://stock.xueqiu.com/v5/stock/finance/cn/income.json?symbol=%s&type=Q4&is_detail=true&count=50'%stock_code
        yield scrapy.Request(url=benifit_year_url, callback=self.parse_benifit_year, dont_filter=True,
                             meta={"info": (stock_code, stock_market, stock_name,benifit_report)})

    def parse_benifit_year(self,response):
        stock_code,stock_market,stock_name,benifit_report = response.meta.get("info")
        benifit_year = response.text
        benifit_quarter_url = 'https://stock.xueqiu.com/v5/stock/finance/cn/income.json?symbol=%s&type=S0&is_detail=true&count=150'%stock_code
        yield scrapy.Request(url=benifit_quarter_url, callback=self.parse_benifit_quarter, dont_filter=True,
                             meta={"info": (stock_code, stock_market, stock_name, benifit_report, benifit_year)})

    def parse_benifit_quarter(self,response):
        stock_code,stock_market,stock_name,benifit_report,benifit_year= response.meta.get("info")
        benifit_quarter = response.text
        item = XueqiuFinanceBenifitItem(stock_code=stock_code[2:],stock_market=stock_market,stock_name=stock_name,
                                        benifit_report=benifit_report,benifit_year=benifit_year,benifit_quarter=benifit_quarter,
                                        crawl_time=self.crawl_time)
        yield item

    #现金流
    def parse_cash_report(self,response):
        stock_code, stock_market, stock_name = response.meta.get("info")
        cash_report = response.text
        cash_year_url = 'https://stock.xueqiu.com/v5/stock/finance/cn/cash_flow.json?symbol=%s&type=Q4&is_detail=true&count=50'%stock_code
        yield scrapy.Request(url=cash_year_url, callback=self.parse_cash_year, dont_filter=True,
                             meta={"info": (stock_code, stock_market, stock_name, cash_report,)})

    def parse_cash_year(self,response):
        stock_code, stock_market, stock_name, cash_report = response.meta.get("info")
        cash_year = response.text
        cash_quarter_url = 'https://stock.xueqiu.com/v5/stock/finance/cn/cash_flow.json?symbol=%s&type=S0&is_detail=true&count=150'%stock_code
        yield scrapy.Request(url=cash_quarter_url, callback=self.parse_cash_quarter, dont_filter=True,
                             meta={"info": (stock_code, stock_market, stock_name, cash_report, cash_year)})

    def parse_cash_quarter(self,response):
        stock_code, stock_market, stock_name, cash_report, cash_year = response.meta.get("info")
        cash_quarter = response.text
        item = XueqiuFinanceCashItem(stock_code=stock_code[2:],stock_market=stock_market,stock_name=stock_name,
                                 cash_report=cash_report,cash_year=cash_year,cash_quarter=cash_quarter,
                                 crawl_time=self.crawl_time)
        yield item



