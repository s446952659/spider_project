# -*- coding: utf-8 -*-
import scrapy
import datetime
from Astock.items import CompanyDetailItem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pydispatch import dispatcher
from scrapy import signals
from Astock.tools import list_to_str,get_stock


class CompanyDetailSpider(scrapy.Spider):
    name = 'CompanyDetail'
    allowed_domains = ['stockpage.10jqka.com.cn']
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {'Astock.middlewares.CompanyDetailDownloaderMiddleware': 300, }
    }
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')

    def __init__(self):
        super(CompanyDetailSpider,self).__init__()
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stocks = get_stock('china_data_source')
        dispatcher.connect(self.closeSpider,signals.spider_closed)

    def closeSpider(self):
        self.driver.quit()

    def start_requests(self):
        for i in self.stocks:
            stock_code = i['code']
            stock_market = i['market']
            stock_name = i['name']
            url = 'http://basic.10jqka.com.cn/%s/company.html#stockpage' % stock_code
            yield scrapy.Request(url=url, callback=self.parse_next, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name)})

    def parse_next(self,response):
        stock_code,stock_market,stock_name = response.meta.get('info')
        c_name = response.xpath("//table[@class='m_table']/tbody//tr[1]//td[2]/span/text()").get()
        area = response.xpath("//table[@class='m_table']/tbody//tr[1]//td[3]/span/text()").get()
        e_name = response.xpath("//table[@class='m_table']/tbody//tr[2]//td[1]/span/text()").get()
        industry = response.xpath("//table[@class='m_table']/tbody//tr[2]//td[2]/span/text()").get()  # 行业
        used_name = response.xpath("//table[@class='m_table']/tbody//tr[3]//td[1]/span/text()").get()
        web_site = response.xpath("//table[@class='m_table']/tbody//tr[3]//td[2]/span/a/text()").get()
        tbody = response.xpath("//table[@class='m_table ggintro managelist']/tbody")
        main_business = tbody.xpath(".//tr[1]//span/text()").get()  # 主营业务
        product_name_list = tbody.xpath(".//tr[2]//span[contains(@style,'color')]//text()").getall()
        product_name = list_to_str(product_name_list)  # 产品名称
        shareholder_list = tbody.xpath(".//tr[3]/td/div//text()").getall()[2:]
        shareholder = list_to_str(shareholder_list)  # 股东
        actual_controller_list = tbody.xpath(".//tr[4]/td/div//text()").getall()[2:]
        actual_controller = list_to_str(actual_controller_list)  # 实际控制人
        ultimate_controller_list = tbody.xpath(".//tr[5]/td/div//text()").getall()[2:]
        ultimate_controller = list_to_str(ultimate_controller_list)  # 最终控制人
        chairman = tbody.xpath(".//tr[6]/td[1]/span/a/text()").get()  # 董事长
        chairman_secretary = tbody.xpath(".//tr[6]/td[2]/span/a/text()").get()  # 董事长秘书
        legal_persion = tbody.xpath(".//tr[6]/td[3]/span/a/text()").get()  # 法人代表
        general_manager = tbody.xpath(".//tr[7]/td[1]/span/a/text()").get()  # 总经理
        registered_capital = tbody.xpath(".//tr[7]/td[2]/span/text()").get()  # 注册资金
        number = tbody.xpath(".//tr[7]/td[3]/span/text()").get()  # 员工人数
        telephone = tbody.xpath(".//tr[8]/td[1]/span/text()").get()  # 电话
        fax = tbody.xpath(".//tr[8]/td[2]/span/text()").get()  # 传真
        zip_code = tbody.xpath(".//tr[8]/td[3]/span/text()").get()  # 邮编
        address = tbody.xpath(".//tr[9]/td[1]/span/text()").get()  # 办公地址
        intro = tbody.xpath(".//tr[10]/td/p[2]/text()").get()  # 公司简介
        if intro == None:
            intro = tbody.xpath(".//tr[10]/td/p[1]/text()").get()
        item = CompanyDetailItem(stock_code=stock_code, stock_market=stock_market, stock_name=stock_name,
                                  c_name=c_name,
                                  area=area, e_name=e_name, industry=industry, used_name=used_name, web_site=web_site,
                                  main_business=main_business, product_name=product_name, shareholder=shareholder,
                                  actual_controller=actual_controller, ultimate_controller=ultimate_controller,
                                  chairman=chairman, chairman_secretary=chairman_secretary, legal_persion=legal_persion,
                                  general_manager=general_manager, registered_capital=registered_capital, number=number,
                                  telephone=telephone, fax=fax, zip_code=zip_code, address=address, intro=intro,
                                  crawl_time=self.crawl_time, )
        yield item




