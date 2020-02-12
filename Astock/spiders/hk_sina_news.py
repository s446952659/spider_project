# -*- coding: utf-8 -*-
import scrapy
import datetime
from Astock.items import HKCompanyNewsItem
from Astock.tools import get_md5,parse_descr,parse_content,filter_urlkey,filter_url,get_stock


class HKSinaNewsSpider(scrapy.Spider):
    name = 'HKSinaNews'
    allowed_domains = ['sina.com.cn']

    def __init__(self):
        super(HKSinaNewsSpider, self).__init__()
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stocks = get_stock('hk_data_source')

    def start_requests(self):
        for i in self.stocks:
            stock_code = i['code']
            stock_market = i['market']
            stock_name = i['name']
            url = 'http://stock.finance.sina.com.cn/hkstock/news/%s.html' % stock_code
            yield scrapy.Request(url=url, callback=self.parse_next, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name)})

    def parse_next(self,response):
        stock_code, stock_market, stock_name = response.meta.get('info')
        lis = response.xpath("//ul[@id='js_ggzx']/li")
        for li in lis:
            title = li.xpath("./a/text()").get()
            if title == None:
                continue
            link_url = li.xpath("./a/@href").get()
            if filter_urlkey(link_url):
                continue
            pub_time = li.xpath("./span/text()").get()
            link_url_md5 = get_md5(stock_code+title)
            if filter_url('hk_news',link_url_md5):
                continue
            if 'vip.stock.finance.sina.com.cn' in link_url:
                yield scrapy.Request(url=link_url, callback=self.parse_vip_stock, dont_filter=True,
                                     meta={"info": (stock_code, stock_market, stock_name, title, link_url, pub_time,link_url_md5)})
                continue
            if 'stock.finance.sina.com.cn' in link_url:
                yield scrapy.Request(url=link_url, callback=self.parse_stock_finance, dont_filter=True,
                                     meta={"info": (stock_code, stock_market, stock_name, title, link_url, pub_time,link_url_md5)})
                continue
            if 'finance.sina.com.cn' in link_url or 'cj.sina.com.cn' in link_url or 'tech.sina.com.cn' in link_url:
                yield scrapy.Request(url=link_url, callback=self.parse_finance_cj, dont_filter=True,
                                     meta={"info": (stock_code,stock_market,stock_name,title,link_url,pub_time,link_url_md5)})
                continue

    def parse_finance_cj(self,response):
        stock_code , stock_market , stock_name , title , link_url , pub_time, link_url_md5 = response.meta.get('info')
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
        item = HKCompanyNewsItem(stock_code=stock_code, stock_market=stock_market, stock_name=stock_name,
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
        item = HKCompanyNewsItem(stock_code=stock_code, stock_market=stock_market, stock_name=stock_name,
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
        item = HKCompanyNewsItem(stock_code=stock_code, stock_market=stock_market, stock_name=stock_name,
                               title=title, pub_time=pub_time, website=website, source=source, content=content,
                               description=description, link_url=link_url, link_url_md5=link_url_md5,
                               crawl_time=self.crawl_time)
        yield item

