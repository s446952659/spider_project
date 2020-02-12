# -*- coding: utf-8 -*-
import scrapy
import datetime
import pymysql
from Astock.settings import DBConfig
from Astock.items import CompanyNoticeItem,HKCompanyNoticeItem
from Astock.tools import list_to_str


class SinaNoticeReSpider(scrapy.Spider):
    name = 'SinaNoticeRe'
    allowed_domains = ['sina.com.cn']

    def __init__(self):
        super(SinaNoticeReSpider, self).__init__()
        dbparams = DBConfig
        conn = pymysql.connect(**dbparams)
        cursor = conn.cursor()
        sql = 'SELECT * FROM china_notice WHERE content is NULL'
        cursor.execute(sql)
        self.result_china = cursor.fetchall()
        sql = 'SELECT * FROM hk_notice WHERE content is NULL'
        cursor.execute(sql)
        self.result_hk = cursor.fetchall()
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.close()
        conn.close()

    def start_requests(self):
        for x in self.result_china:
            stock_code = x['stock_code']
            stock_market = x['stock_market']
            stock_name = x['stock_name']
            title = x['title']
            link_url = x['link_url']
            link_url_md5 = x['link_url_md5']
            pub_time = str(x['pub_time'])
            yield scrapy.Request(url=link_url, callback=self.parse_vip_stock, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name, title, link_url, pub_time, link_url_md5)})
        for x in self.result_hk:
            stock_code = x['stock_code']
            stock_market = x['stock_market']
            stock_name = x['stock_name']
            title = x['title']
            link_url = x['link_url']
            link_url_md5 = x['link_url_md5']
            pub_time = str(x['pub_time'])
            yield scrapy.Request(url=link_url, callback=self.parse_stock_finance, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name, title, link_url, pub_time, link_url_md5)})

    def parse_vip_stock(self,response):
        stock_code, stock_market, stock_name, title, link_url, pub_time, link_url_md5 = response.meta.get('info')
        content = response.xpath("//div[@id='content']").get()
        website = '新浪财经'
        source = '新浪财经'
        item = CompanyNoticeItem(stock_code=stock_code, stock_market=stock_market, stock_name=stock_name,
                                 title=title,pub_time=pub_time, content=content,website=website,source=source,
                                 link_url=link_url,link_url_md5=link_url_md5,crawl_time=self.crawl_time)
        yield item

    def parse_stock_finance(self,response):
        stock_code, stock_market, stock_name, title, link_url, pub_time, link_url_md5 = response.meta.get('info')
        content = response.xpath("//div[@class='part02']/p").getall()
        content = list_to_str(content)
        website = '新浪财经'
        source = '新浪财经'
        item = HKCompanyNoticeItem(stock_code=stock_code, stock_market=stock_market, stock_name=stock_name,website=website,source=source,
                               title=title, pub_time=pub_time,content=content,link_url=link_url, link_url_md5=link_url_md5,
                               crawl_time=self.crawl_time)
        yield item