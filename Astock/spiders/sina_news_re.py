# -*- coding: utf-8 -*-
import scrapy
import datetime
import pymysql
from Astock.settings import DBConfig
from Astock.items import CompanyNewsItem,HKCompanyNewsItem
from Astock.tools import parse_descr,parse_content


class SinaNewsReSpider(scrapy.Spider):
    name = 'SinaNewsRe'
    allowed_domains = ['sina.com.cn']

    def __init__(self):
        super(SinaNewsReSpider, self).__init__()
        dbparams = DBConfig
        conn = pymysql.connect(**dbparams)
        cursor = conn.cursor()
        sql = 'SELECT * FROM china_news WHERE content is NULL'
        cursor.execute(sql)
        self.result_china = cursor.fetchall()
        sql = 'SELECT * FROM hk_news WHERE content is NULL'
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
            yield scrapy.Request(url=link_url, callback=self.parse_next, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name,
                                                title,pub_time,link_url,link_url_md5)})
        for x in self.result_hk:
            stock_code = x['stock_code']
            stock_market = x['stock_market']
            stock_name = x['stock_name']
            title = x['title']
            link_url = x['link_url']
            link_url_md5 = x['link_url_md5']
            pub_time = str(x['pub_time'])
            yield scrapy.Request(url=link_url, callback=self.parse_next, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name,
                                                title, pub_time, link_url, link_url_md5)})

    def parse_next(self,response):
        stock_code, stock_market, stock_name,\
        title,pub_time,link_url,link_url_md5 = response.meta.get('info')
        if 'vip.stock.finance.sina.com.cn' in link_url:
            yield scrapy.Request(url=link_url, callback=self.parse_vip_stock, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name, title, link_url, pub_time,link_url_md5)})
            return
        if 'stock.finance.sina.com.cn' in link_url:
            yield scrapy.Request(url=link_url, callback=self.parse_stock_finance, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name, title, link_url, pub_time,link_url_md5)})
            return
        if 'finance.sina.com.cn' in link_url or 'cj.sina.com.cn' in link_url:
            yield scrapy.Request(url=link_url, callback=self.parse_finance_cj, dont_filter=True,
                                 meta={"info": (stock_code,stock_market,stock_name,title,link_url,pub_time,link_url_md5)})
            return

    def parse_finance_cj(self,response):
        stock_code,stock_market,stock_name,title,link_url,pub_time,link_url_md5 = response.meta.get('info')
        website = '新浪财经'
        tags = response.xpath("//div[@id='artibody']/*")
        content = parse_content(tags,link_url)
        des = response.xpath("//div[@id='artibody']//p//text()").getall()
        description = parse_descr(des)
        #处理特殊页面结构
        source = response.xpath("//div[@class='date-source']/a/text()").get()
        if source == None:
            source = response.xpath("//div[@class='date-source']/span[2]//text()").get()
        if source == None:
            source = response.xpath("//div[@class='page-info']//span[@data-sudaclick='media_name']//text()").get()
        if len(stock_code) == 5:
            item = HKCompanyNewsItem(stock_code=stock_code, stock_market=stock_market, stock_name=stock_name,
                                     title=title, pub_time=pub_time, website=website, source=source, content=content,
                                     description=description, link_url=link_url, link_url_md5=link_url_md5,
                                     crawl_time=self.crawl_time)
        else:
            item = CompanyNewsItem(stock_code=stock_code[2:], stock_market=stock_market, stock_name=stock_name,
                                   title=title, pub_time=pub_time,website=website,source=source,content=content,
                                   description=description, link_url=link_url,link_url_md5=link_url_md5,
                                   crawl_time=self.crawl_time)
        yield item

    def parse_stock_finance(self,response):
        stock_code, stock_market, stock_name, title, link_url, pub_time,link_url_md5 = response.meta.get('info')
        website = '新浪财经'
        source = None
        content = response.xpath("//div[@class='blk_container']/p").get()
        des = response.xpath("//div[@class='blk_container']/p//text()").getall()
        description = parse_descr(des)
        if len(stock_code) == 5:
            item = HKCompanyNewsItem(stock_code=stock_code, stock_market=stock_market, stock_name=stock_name,
                                     title=title, pub_time=pub_time, website=website, source=source, content=content,
                                     description=description, link_url=link_url, link_url_md5=link_url_md5,
                                     crawl_time=self.crawl_time)
        else:
            item = CompanyNewsItem(stock_code=stock_code[2:], stock_market=stock_market, stock_name=stock_name,
                                   title=title, pub_time=pub_time, website=website, source=source, content=content,
                                   description=description, link_url=link_url, link_url_md5=link_url_md5,
                                   crawl_time=self.crawl_time)
        yield item

    def parse_vip_stock(self,response):
        stock_code, stock_market, stock_name, title, link_url, pub_time, link_url_md5 = response.meta.get('info')
        website = '新浪财经'
        source = None
        content = response.xpath("//div[@id='content']").get()
        des = response.xpath("//div[@id='content']/p//text()").getall()
        description = parse_descr(des)
        if len(stock_code) == 5:
            item = HKCompanyNewsItem(stock_code=stock_code, stock_market=stock_market, stock_name=stock_name,
                                     title=title, pub_time=pub_time, website=website, source=source, content=content,
                                     description=description, link_url=link_url, link_url_md5=link_url_md5,
                                     crawl_time=self.crawl_time)
        else:
            item = CompanyNewsItem(stock_code=stock_code[2:], stock_market=stock_market, stock_name=stock_name,
                                   title=title, pub_time=pub_time, website=website, source=source, content=content,
                                   description=description, link_url=link_url, link_url_md5=link_url_md5,
                                   crawl_time=self.crawl_time)
        yield item

