# -*- coding: utf-8 -*-
import scrapy
import datetime
import json
import re
from Astock.items import ResearchReportItem
from Astock.tools import filt_htmlstr,timestamptostr,get_cookies,filter_url,get_stock


class ChinaReportApiSpider(scrapy.Spider):
    name = 'ChinaReportApi'
    allowed_domains = ['xueqiu.com']
    handle_httpstatus_list = [302]

    def __init__(self):
        super(ChinaReportApiSpider, self).__init__()
        self.cookies = get_cookies()# 获取接口cookies
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.stocks = get_stock('china_data_source')

    def start_requests(self):
        for i in self.stocks:
            stock_code = i['code']
            stock_market = i['market']
            stock_name = i['name']
            if stock_market == '1101':
                stock_code = 'SH' + stock_code
            else:
                stock_code = 'SZ' + stock_code
            url = 'https://xueqiu.com/statuses/stock_timeline.json?symbol_id=%s&count=10&source=研报&page=1'%stock_code
            yield scrapy.Request(url=url, callback=self.parse_next, dont_filter=True,cookies=self.cookies,
                                 meta={"info": (stock_code, stock_market, stock_name)})

    def parse_next(self,response):
        stock_code, stock_market, stock_name = response.meta.get('info')
        content = json.loads(response.text)
        objs = content['list']
        if objs != []:
            for obj in objs:
                article_id = obj['id']
                # if filter_url('china_report',article_id):
                #     continue
                link_url = 'https://xueqiu.com' + obj['target']
                title = obj['title']
                pub_time = timestamptostr(obj['created_at'])
                description = filt_htmlstr(obj['description'])
                try:
                    status = re.search('：(.*)］', title).group(1)
                except:
                    status = None
                yield scrapy.Request(url=link_url, callback=self.parse_content, #dont_filter=True,
                                     cookies=self.cookies,
                                     meta={"info": (stock_code, stock_market, stock_name,title,pub_time,
                                                    status,description,link_url,article_id)})

    def parse_content(self,response):
        stock_code,stock_market,stock_name,title,pub_time,status,description,link_url,article_id = response.meta.get('info')
        content = response.xpath(".//div[@class='article__bd__detail']").get()
        #处理多余标签
        # res = re.sub('<p style="display:none;">.*</p>', '', content)
        # content = re.sub('<a.+?>','<a>',res)
        website = '雪球'
        source = '雪球'
        item = ResearchReportItem(stock_code=stock_code[2:], stock_market=stock_market, stock_name=stock_name,
                                  title=title, pub_time=pub_time, status=status,website=website,source=source,
                                  description=description, link_url=link_url, article_id=article_id,content=content,
                                  crawl_time=self.crawl_time)
        yield item