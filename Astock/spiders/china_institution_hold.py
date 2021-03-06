# -*- coding: utf-8 -*-
import scrapy
import json
import datetime
from Astock.items import InstitutionalHoldItem
from Astock.tools import get_stock


class InstitutionHoldSpider(scrapy.Spider):
    name = 'InstitutionHold'
    allowed_domains = ['stockpage.10jqka.com.cn']

    def __init__(self):
        super(InstitutionHoldSpider, self).__init__()
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stocks = get_stock('china_data_source')


    def start_requests(self):
        for i in self.stocks:
            stock_code = i['code']
            stock_market = i['market']
            stock_name = i['name']
            url = 'http://basic.10jqka.com.cn/%s/position.html#stockpage/' % stock_code
            yield scrapy.Request(url=url, callback=self.parse_next, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name)})

    def parse_next(self,response):
        stock_code, stock_market, stock_name = response.meta.get('info')
        table = response.xpath("//div[@class='m_tab_content']//table[@class='m_table m_hl']")
        if table:
            date = table.xpath(".//thead/tr/th[2]/text()").get()
            institutions = table.xpath(".//tbody/tr[1]/td[1]/text()").get().strip()  # 机构数量(家)
            accum_hold = table.xpath(".//tbody/tr[2]/td[1]/text()").get()  # 累计持有数量(股)
            market_value = table.xpath(".//tbody/tr[3]/td[1]/text()").get()  # 累计市值(元)
            position_proportion = table.xpath(".//tbody/tr[4]/td[1]/text()").get()  # 持仓比例
            change_period = table.xpath(".//tbody/tr[5]/td[1]/span/text()").get()  # 较上期变化(股)
            last_institutions = table.xpath(".//tbody/tr[1]/td[2]/text()").get()  # 上次机构数量(家)
            if last_institutions != None:
                last_institutions = last_institutions.strip()
            last_position_proportion = table.xpath(".//tbody/tr[4]/td[2]/text()").get()  # 上次持仓比例
            summary_hold = {
                'date': date, 'institutions': institutions, 'last_institutions': last_institutions,
                'last_position_proportion':last_position_proportion,
                'accum_hold': accum_hold, 'market_value': market_value,
                'position_proportion': position_proportion, 'change_period': change_period
            }
        else:
            summary_hold = []
        ddate = response.xpath("//div[@class='m_tab mt15 fl']/ul/li[@class='cur']/a/text()").get()
        trs = response.xpath("//tbody[@id='organInfo_1']//tr")
        detail_hold = []
        for tr in trs:
            institution_name = tr.xpath(".//th/span/text()").get().strip()  # 机构或基金名称
            institutional_type = tr.xpath(".//td[1]/text()").get()  # 机构类型
            number_shares = tr.xpath(".//td[2]/text()").get()  # 持有数量
            share_market = tr.xpath(".//td[3]/text()").get()  # 持股市值
            proportion_shares = tr.xpath(".//td[4]/text()").get()  # 占流通股比例
            increase_decrease = tr.xpath(".//td[5]//text()").getall()
            increase_decrease = ''.join(increase_decrease).strip()# 增减情况
            income_rank = tr.xpath(".//td[6]/text()").get()  # 基金收益排行
            ddetail_hold = {
                'ddate': ddate, 'institution_name': institution_name, 'institutional_type': institutional_type,
                'number_shares': number_shares, 'share_market': share_market, 'proportion_shares': proportion_shares,
                'increase_decrease': increase_decrease, 'income_rank': income_rank
            }
            detail_hold.append(ddetail_hold)
        item = InstitutionalHoldItem(stock_code=stock_code, stock_market=stock_market, stock_name=stock_name,
                                      summary_hold=json.dumps(summary_hold, ensure_ascii=False),
                                      detail_hold=json.dumps(detail_hold, ensure_ascii=False),
                                      crawl_time=self.crawl_time)
        yield item
