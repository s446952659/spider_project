# -*- coding: utf-8 -*-
import scrapy
import datetime
import json
from Astock.items import ForecastsItem
from Astock.tools import get_stock


class ForecastsSpider(scrapy.Spider):
    name = 'Forecasts'
    allowed_domains = ['stockpage.10jqka.com.cn']

    def __init__(self):
        super(ForecastsSpider, self).__init__()
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stocks = get_stock('china_data_source')

    def start_requests(self):
        for i in self.stocks:
            stock_code = i['code']
            stock_market = i['market']
            stock_name = i['name']
            url = 'http://basic.10jqka.com.cn/%s/worth.html#stockpage' % stock_code
            yield scrapy.Request(url=url, callback=self.parse_next, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name)})

    def parse_next(self,response):
        stock_code,stock_market,stock_name = response.meta.get('info')
        eper_share = []  # 预测年报每股收益
        etrs = response.xpath("//div[@class='clearfix']//div[1]/table[@class='m_table m_hl']//tbody//tr")
        for tr in etrs:
            eyear = tr.xpath(".//th/text()").get()
            einstitutions = tr.xpath(".//td[1]/text()").get()  # 预测机构数
            emin = tr.xpath(".//td[2]/text()").get()
            emean = tr.xpath(".//td[3]/text()").get()
            emax = tr.xpath(".//td[4]/text()").get()
            eindust_average = tr.xpath(".//td[5]/text()").get()  # 行业平均数
            edper_share = {'eyear': eyear, 'einstitutions': einstitutions, 'emin': emin, 'emean': emean,
                           'emax': emax, 'eindust_average': eindust_average}
            eper_share.append(edper_share)
        profit = []  # 预测年报净利润
        ptrs = response.xpath("//div[@class='clearfix']//div[2]/table[@class='m_table m_hl']//tbody//tr")
        for tr in ptrs:
            pyear = tr.xpath(".//th/text()").get()
            pinstitutions = tr.xpath(".//td[1]/text()").get()  # 预测机构数
            pmin = tr.xpath(".//td[2]/text()").get()
            pmean = tr.xpath(".//td[3]/text()").get()
            pmax = tr.xpath(".//td[4]/text()").get()
            pindust_average = tr.xpath(".//td[5]/text()").get()  # 行业平均数
            pdper_share = {'eyear': pyear, 'einstitutions': pinstitutions, 'emin': pmin, 'emean': pmean,
                           'emax': pmax, 'eindust_average': pindust_average}
            profit.append(pdper_share)
        item = ForecastsItem(stock_code=stock_code, stock_market=stock_market, stock_name=stock_name,
                             eper_share=json.dumps(eper_share,ensure_ascii=False),profit=json.dumps(profit,ensure_ascii=False),
                             crawl_time=self.crawl_time)
        yield item