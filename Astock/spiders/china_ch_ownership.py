# -*- coding: utf-8 -*-
import scrapy
import json
import datetime
from Astock.items import ChangeOwnershipItem
from Astock.tools import get_stock


class ChOwnershipSpider(scrapy.Spider):
    name = 'ChOwnership'
    allowed_domains = ['data.10jqka.com.cn']

    def __init__(self):
        super(ChOwnershipSpider,self).__init__()
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stocks = get_stock('china_data_source')

    def start_requests(self):
        for i in self.stocks:
            stock_code = i['code']
            stock_market = i['market']
            stock_name = i['name']
            url = 'http://data.10jqka.com.cn/financial/ggjy/op/code/code/%s/' % stock_code
            yield scrapy.Request(url=url, callback=self.parse_next, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name)})

    def parse_next(self,response):
        stock_code, stock_market, stock_name = response.meta.get('info')
        trs = response.xpath("//div[@class='page-table']//tbody//tr")
        detaileds_hold = []
        for tr in trs:
            number = tr.xpath(".//td[1]/text()").get()  # 序号
            person = tr.xpath(".//td[2]/text()").get()  # 变动人
            change_date = tr.xpath(".//td[3]/text()").get()  # 变动日期
            change_shares = tr.xpath(".//td[4]/text()").get()  # 变动股数
            price = tr.xpath(".//td[5]/text()").get()  # 成交均价
            change_reason = tr.xpath(".//td[6]/text()").get()  # 变动原因
            changes_proportion = tr.xpath(".//td[7]/text()").get()  # 变动比例
            changeafter_shares = tr.xpath(".//td[8]/text()").get()  # 变动后股数
            prison_high = tr.xpath(".//td[9]/a/text()").get()  # 董监高
            prison_highpaid = tr.xpath(".//td[10]/text()").get()  # 董监高薪酬
            prison_position = tr.xpath(".//td[11]/text()").get()  # 董监高职务
            prison_Relationship = tr.xpath(".//td[12]/text()").get()  # 董监高关系
            detail = {'number': number, 'person': person, 'change_date': change_date, 'change_shares': change_shares,
                      'price': price, 'change_reason': change_reason, 'changes_proportion': changes_proportion,
                      'changeafter_shares': changeafter_shares, 'prison_high': prison_high,'prison_highpaid': prison_highpaid,
                      'prison_position': prison_position, 'prison_Relationship': prison_Relationship}
            detaileds_hold.append(detail)
        item = ChangeOwnershipItem(stock_code=stock_code, stock_market=stock_market,
                                    stock_name=stock_name,crawl_time=self.crawl_time,
                                    detaileds_hold=json.dumps(detaileds_hold,ensure_ascii=False))
        yield item