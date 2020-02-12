# -*- coding: utf-8 -*-
import scrapy
import datetime
from Astock.items import CompanyProfileItem
from Astock.tools import get_stock

class CompanyProfileSpider(scrapy.Spider):
    name = 'CompanyProfile'
    allowed_domains = ['stockpage.10jqka.com.cn']

    def __init__(self):
        super(CompanyProfileSpider, self).__init__()
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stocks = get_stock('china_data_source')

    def start_requests(self):
        for i in self.stocks:
            stock_code = i['code']
            stock_market = i['market']
            stock_name = i['name']
            url = 'http://stockpage.10jqka.com.cn/%s/#gegugp_zjjp' % stock_code
            yield scrapy.Request(url=url, callback=self.parse_next, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name)})

    def parse_next(self,response):
        stock_code, stock_market, stock_name = response.meta.get('info')
        area = response.xpath("//dl[@class='company_details']//dd[1]//text()").get()  # 地区
        concept = response.xpath("//dl[@class='company_details']//dd[2]/@title").get()  # 涉及概念
        main_business = response.xpath("//dl[@class='company_details']//dd[3]//text()").get()
        main_business_1 = response.xpath("//dl[@class='company_details']//dd[4]/@title").get()
        main_business = main_business + main_business_1  # 主营业务
        launch_date = response.xpath("//dl[@class='company_details']//dd[5]//text()").get()  # 上市日期
        per_share = response.xpath("//dl[@class='company_details']//dd[6]//text()").get()  # 每股净资产
        per_earning = response.xpath("//dl[@class='company_details']//dd[7]//text()").get()  # 每股收益
        profit = response.xpath("//dl[@class='company_details']//dd[8]//text()").get()  # 净利润
        profit_growth = response.xpath("//dl[@class='company_details']//dd[9]//text()").get()  # 净利润增长率
        income = response.xpath("//dl[@class='company_details']//dd[10]//text()").get()  # 营业收入
        cash_flow = response.xpath("//dl[@class='company_details']//dd[11]//text()").get()  # 现金流
        fund = response.xpath("//dl[@class='company_details']//dd[12]//text()").get()  # 公积金
        undistributed_profit = response.xpath("//dl[@class='company_details']//dd[13]//text()").get()  # 每股未分配利润
        total_equity = response.xpath("//dl[@class='company_details']//dd[14]//text()").get()  # 总股本
        shares_outstanding = response.xpath("//dl[@class='company_details']//dd[15]//text()").get()  # 流通股
        item = CompanyProfileItem(stock_code=stock_code, stock_market=stock_market, stock_name=stock_name, area=area,
                                   concept=concept,main_business=main_business, launch_date=launch_date, per_share=per_share,
                                   per_earning=per_earning,profit=profit, profit_growth=profit_growth, income=income, cash_flow=cash_flow,
                                   fund=fund,undistributed_profit=undistributed_profit, total_equity=total_equity,
                                   shares_outstanding=shares_outstanding, crawl_time=self.crawl_time)
        yield item

