# -*- coding: utf-8 -*-
import scrapy
import datetime
from Astock.items import HKCompanyProfileItem
from Astock.tools import get_stock


class HkcompanyProfileSpider(scrapy.Spider):
    name = 'HKCompanyProfile'
    allowed_domains = ['stockpage.10jqka.com.cn']

    def __init__(self):
        super(HkcompanyProfileSpider, self).__init__()
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stocks = get_stock('hk_data_source')

    def start_requests(self):
        for i in self.stocks:
            stock_code = i['code']
            stock_market = i['market']
            stock_name = i['name']
            stock_code = stock_code.replace('0', 'HK', 1)
            url = 'http://stockpage.10jqka.com.cn/%s/#gegugp_zjjp/'%stock_code
            yield scrapy.Request(url=url, callback=self.parse_next, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name)})

    def parse_next(self,response):
        stock_code, stock_market, stock_name = response.meta.get('info')
        launch_date = response.xpath("//tr[@class='table-info-top']/td[not(@class)]/text()").get()[5:]
        url = 'http://stockpage.10jqka.com.cn/%s/company/'%stock_code
        yield scrapy.Request(url=url, callback=self.parse_profile_next, dont_filter=True,
                             meta={"info": (stock_code, stock_market, stock_name, launch_date)})

    def parse_profile_next(self,response):
        stock_code, stock_market, stock_name, launch_date = response.meta.get('info')
        table = response.xpath("//table[@class='m_table']")
        c_name = table.xpath(".//tr[1]/td[1]/span/text()").get().strip()
        address = table.xpath(".//tr[4]/td[2]/span//text()").get().strip()
        telephone = table.xpath(".//tr[5]/td[1]/span/text()").get().strip()
        website = table.xpath(".//tr[6]/td[1]/span/a/text()").get()
        profile = response.xpath("//div[@class='gn-info f14']/p/text()").get().strip()
        item = HKCompanyProfileItem(stock_code=stock_code.replace('HK','0'), stock_market=stock_market, stock_name=stock_name,
                                     launch_date=launch_date, c_name=c_name, address=address, telephone=telephone,
                                     website=website, profile=profile, crawl_time=self.crawl_time)
        yield item