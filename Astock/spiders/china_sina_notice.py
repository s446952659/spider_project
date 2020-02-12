# -*- coding: utf-8 -*-
import scrapy
import datetime
from Astock.items import CompanyNoticeItem
from Astock.tools import timelist_conversion,get_md5,get_stock


class ChinaSinaNoticeSpider(scrapy.Spider):
    name = 'ChinaSinaNotice'
    allowed_domains = ['sina.com.cn']

    def __init__(self):
        super(ChinaSinaNoticeSpider, self).__init__()
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stocks = get_stock('china_data_source')

    def start_requests(self):
        for i in self.stocks:
            stock_code = i['code']
            stock_market = i['market']
            stock_name = i['name']
            url = 'http://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllBulletin/stockid/%s.phtml' % stock_code
            yield scrapy.Request(url=url, callback=self.parse_next, dont_filter=True,
                                 meta={"info": (stock_code, stock_market, stock_name)})

    def parse_next(self,response):
        stock_code, stock_market, stock_name = response.meta.get('info')
        time_list = timelist_conversion(response.xpath("//div[@class='datelist']/ul/text()").getall())
        articles = response.xpath("//div[@class='datelist']/ul//a")
        for index, article in enumerate(articles):
            title = article.xpath("./text()").get()
            link_url = response.urljoin(article.xpath("./@href").get())
            pub_time = time_list[index]
            link_url_md5 = get_md5(stock_code+link_url)
            # if filter_url('china_notice',link_url_md5):
            #     continue
            yield scrapy.Request(url=link_url, callback=self.parse_vip_stock, #dont_filter=True,
                                     meta={"info": (stock_code, stock_market, stock_name, title, link_url, pub_time,link_url_md5)})

    def parse_vip_stock(self,response):
        stock_code, stock_market, stock_name, title, link_url, pub_time, link_url_md5 = response.meta.get('info')
        content = response.xpath("//div[@id='content']").get()
        website = '新浪财经'
        source = '新浪财经'
        item = CompanyNoticeItem(stock_code=stock_code, stock_market=stock_market, stock_name=stock_name,
                                 title=title,pub_time=pub_time, content=content,website=website,source=source,
                                 link_url=link_url,link_url_md5=link_url_md5,crawl_time=self.crawl_time)
        yield item

