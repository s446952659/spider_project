# -*- coding: utf-8 -*-
import scrapy
import pandas as pd
import datetime
import re
from Astock.settings import xredis, DBConfig
from Astock.items import CompanyNewsItem
from Astock.tools import parse_descr,parse_content,get_md5,filter_url,filter_urlkey


class ChinaSinaNewsTestApiSpider(scrapy.Spider):
    name = 'ChinaTestSinaNews'
    allowed_domains = ['sina.com.cn']
    crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    filter_keys = '按图放大|点此了解您最关注的货币对在每天最为波动的时段，保证在正确的时间进行交易|点此下载交易展望报告，提升全球金融市场交易信心，掌握高级交易策略以及工具！|如何有效利用基本面分析？点此获取掌握交易核心技能的三部曲'

    def start_requests(self):
        #print(self.settings.attributes['NOWSYSTEM'].value)
        url = 'https://www.dailyfxasia.com/cmarkets/20191227-10336.html'
        # md5 = get_md5('sz002142'+url)
        # print(xredis.sismember('china_news',md5))

        yield scrapy.Request(url=url,dont_filter=True,callback=self.parse_content,meta={'info':url})

    def parse_next(self,response):
        headers = {
            '222': '8789564'
        }
        link_url = response.meta.get('info')
        if 'vip.stock.finance.sina.com.cn' in link_url :
            yield scrapy.Request(url=link_url, callback=self.parse_vip_stock,dont_filter=True,
                                 meta={"info": (link_url)},headers=headers)
            return

        if 'stock.finance.sina.com.cn' in link_url:
            yield scrapy.Request(url=link_url, callback=self.parse_stock_finance,dont_filter=True,
                                 meta={"info": (link_url)},headers=headers)
            return

        if 'finance.sina.com.cn' in link_url or 'cj.sina.com.cn' in link_url or 'tech.sina.com.cn' in link_url:
            yield scrapy.Request(url=link_url, callback=self.parse_finance_cj,dont_filter=True,
                                 meta={"info": (link_url)},headers=headers)
            return


    def parse_finance_cj(self, response):
        link_url = response.meta.get("info")
        webside = '新浪'
        tags = response.xpath("//div[@id='artibody']/*")
        content = parse_content(tags,link_url)
        des = response.xpath("//div[@id='artibody']//p//text()").getall()
        description = parse_descr(des)
        source = response.xpath("//div[@class='date-source']/a/text()").get()
        if source == None:
            source = response.xpath("//div[@class='date-source']/span[2]//text()").get()
        if source == None:
            source = response.xpath("//div[@class='page-info']//span[@data-sudaclick='media_name']//text()").get()
        print(content)



        # item = CompanyNewsItem(stock_code='600861', stock_market='1101', stock_name='北京城乡',
        #                        title='北京城乡转型核心：商品和服务的融合', pub_time='2019-04-01 11:42', webside=webside, source=source, content=content,
        #                        description=description, link_url='https://finance.sina.com.cn/other/lejunews/2019-04-01/doc-ihtxyzsm2222201.shtml?source=cj&dv=1', link_url_md5='d8c5d06b0a7914b3174d0ccd3f5974da',
        #                        crawl_time=self.crawl_time)
        # yield item


    def parse_stock_finance(self, response):
        webside = '新浪'
        source = ''
        content = response.xpath("//div[@class='blk_container']/p").get()
        des = response.xpath("//div[@class='blk_container']/p//text()").getall()
        description = parse_descr(des)
        print(2)
        print(content)


    def parse_vip_stock(self,response):
        content = response.xpath("//div[@id='content']").get()
        des = response.xpath("//div[@id='content']/p//text()").getall()
        description = parse_descr(des)

        print(description)
        print('*'*30)
        print(content)
        print('*'*30)
        print(3)

    def parse_content(self,response):
        #title,link_url,pub_time,description,source,classify =response.meta.get("info")
        content = response.xpath(".//div[@class='dfx-article-content']").get()
        content = re.sub('<a class="dfx-article-view-image".*?</a>','',content)
        content = re.sub(self.filter_keys,'',content)
        content = re.sub('<a.*?>','<a>',content)

        content = re.sub('style="color:#333333"|style="background-color:white"','',content)

        #contents = parse_daliyfx_content(contents)
        print(content)