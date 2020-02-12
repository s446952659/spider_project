# -*- coding: utf-8 -*-
import scrapy
import datetime
import json
from Astock.items import HKChangeOwnershipItem
from Astock.tools import get_stock


class HkchOwnershipSpider(scrapy.Spider):
    name = 'HKChOwnership'
    allowed_domains = ['stockpage.10jqka.com.cn']

    def __init__(self):
        super(HkchOwnershipSpider, self).__init__()
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stocks = get_stock('hk_data_source')

    def start_requests(self):
        for i in self.stocks:
            stock_code = i['code']
            stock_market = i['market']
            stock_name = i['name']
            stock_code = stock_code.replace('0', 'HK', 1)
            url = 'http://stockpage.10jqka.com.cn/%s/holder/'%stock_code
            yield scrapy.Request(url=url, callback=self.parse_next, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name)})

    def parse_next(self, response):
        stock_code, stock_market, stock_name = response.meta.get('info')
        data = []
        trs = response.xpath("//*[@id='change']/div[2]/table/tbody/tr")
        for tr in trs:
            date = tr.xpath("./th/text()").extract()[0]
            shareholder = tr.xpath("./td[1]/text()").extract()[0]
            if tr.xpath("./td[2]/span/text()").get():
                change = tr.xpath("./td[2]/span/text()").extract()[0]
            else:
                change = tr.xpath("./td[2]/text()").extract()[0].strip()
            holding = tr.xpath("./td[3]/text()").extract()[0]
            proportion = tr.xpath("./td[4]/text()").extract()[0]
            quality = tr.xpath("./td[5]/text()").extract()[0]
            dataMap = {
                        'date': date,
                        'shareholder': shareholder,
                        'change': change,
                        'holding': holding,
                        'proportion': proportion,
                        'quality': quality,
                       }
            data.append(dataMap)
        item = HKChangeOwnershipItem(stock_code=stock_code.replace('HK','0'), stock_market=stock_market, stock_name=stock_name, detaileds_hold=json.dumps(data,ensure_ascii=False),
                      crawl_time=self.crawl_time)
        yield item
