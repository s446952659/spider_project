# -*- coding: utf-8 -*-
import scrapy
import datetime
from Astock.items import HKCompanyNoticeItem
from Astock.tools import get_md5,list_to_str,get_stock


class HKSinaNoticeSpider(scrapy.Spider):
    name = 'HKSinaNotice'
    allowed_domains = ['sina.com.cn']

    def __init__(self):
        super(HKSinaNoticeSpider, self).__init__()
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stocks = get_stock('hk_data_source')

    def start_requests(self):
        for i in self.stocks:
            stock_code = i['code']
            stock_market = i['market']
            stock_name = i['name']
            url = 'http://stock.finance.sina.com.cn/hkstock/notice/%s.html' % stock_code
            yield scrapy.Request(url=url, callback=self.parse_next, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name)})

    def parse_next(self,response):
        stock_code, stock_market, stock_name = response.meta.get('info')
        lis = response.xpath("//ul[@class='list01']/li")
        for li in lis:
            title = li.xpath("./a/text()").get()
            if title == None:
                continue
            pub_time = li.xpath("./span/text()").get()
            link_url = li.xpath("./a/@href").get()
            link_url_md5 = get_md5(stock_code+link_url)
            # if filter_url('hk_notice',link_url_md5):
            #     continue
            yield scrapy.Request(url=link_url, callback=self.parse_stock_finance, #dont_filter=True,
                                     meta={"info": (stock_code, stock_market, stock_name, title, link_url, pub_time,link_url_md5)})

    def parse_stock_finance(self,response):
        stock_code, stock_market, stock_name, title, link_url, pub_time,link_url_md5 = response.meta.get('info')
        content = response.xpath("//div[@class='part02']/p").getall()
        content = list_to_str(content)
        website = '新浪财经'
        source = '新浪财经'
        item = HKCompanyNoticeItem(stock_code=stock_code, stock_market=stock_market, stock_name=stock_name,website=website,source=source,
                               title=title, pub_time=pub_time,content=content,link_url=link_url, link_url_md5=link_url_md5,
                               crawl_time=self.crawl_time)
        yield item
