# -*- coding: utf-8 -*-
import scrapy
import datetime
import json
from Astock.items import FundItem
from Astock.tools import get_stock


class HistoryFundSpider(scrapy.Spider):
    name = 'HistoryFund'
    allowed_domains = ['stockpage.10jqka.com.cn']

    def __init__(self):
        super(HistoryFundSpider, self).__init__()
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stocks = get_stock('china_data_source')

    def start_requests(self):
        for i in self.stocks:
            stock_code = i['code']
            stock_market = i['market']
            stock_name = i['name']
            url = 'http://stockpage.10jqka.com.cn/%s/funds/' % stock_code
            yield scrapy.Request(url=url, callback=self.parse_next, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name)})

    def parse_next(self, response):
        stock_code, stock_market, stock_name = response.meta.get('info')
        trs = response.xpath("//table[@class='m_table_3']//tr[position()>2]")
        fund_data = []
        for tr in trs:
            date = tr.xpath(".//td[1]/text()").extract()[0]
            closePrice = tr.xpath('td[2]/text()').extract()[0]
            quoteChange = tr.xpath('td[3]/text()').extract()[0]
            inflow = tr.xpath('td[4]/text()').extract()[0]
            mainForce = tr.xpath('td[5]/text()').extract()[0]
            bigSingle = tr.xpath('td[6]/text()').extract()[0]
            bigSingle1 = tr.xpath('td[7]/text()').extract()[0]
            mediumSingle = tr.xpath('td[8]/text()').extract()[0]
            mediumSingle1 = tr.xpath('td[9]/text()').extract()[0]
            smallSingle = tr.xpath('td[10]/text()').extract()[0]
            smallSingle1 = tr.xpath('td[11]/text()').extract()[0]
            dataMap = {
                'date': date,'closePrice': closePrice,'quoteChange': quoteChange,'inflow': inflow,'mainForce': mainForce,
                'bigmap': {
                    'bigSingle': bigSingle,
                    'bigSingle1': bigSingle1,
                },
                'mediumMap': {
                    'mediumSingle': mediumSingle,
                    'mediumSingle1': mediumSingle1,
                },
                'smallMap': {
                    'smallSingle': smallSingle,
                    'smallSingle1': smallSingle1,
                }
            }
            fund_data.append(dataMap)
        item = FundItem(stock_code=stock_code, stock_market=stock_market, stock_name=stock_name,
                        fund_data=json.dumps(fund_data,ensure_ascii=False),crawl_time=self.crawl_time)
        yield item