# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy.linkextractors import LinkExtractor
from Astock.items import FlashNewsItem
from Astock.tools import list_to_str,get_md5,parse_pub_time
from Astock.settings import xredis



class FlashNewInvestSpider(scrapy.Spider):
    name = 'FlashNewInvestSpider'
    allowed_domains = ["cn.investing.com"]
    start_urls = ['https://cn.investing.com/news/']
    domin_url = 'https://cn.investing.com/news/'
    categorys = [{'name':'外汇','e_name':'forex-news'},{'name':'加密货币','e_name':'cryptocurrency-news'},
                {'name':'商品期货','e_name':'commodities-news'},{'name':'股市','e_name':'stock-market-news'},
                {'name':'经济指标','e_name':'economic-indicators'},{'name':'财经','e_name':'economy'}]

    def __init__(self):
        super(FlashNewInvestSpider, self).__init__()
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def parse(self, response):
        for category in self.categorys:
            url = self.domin_url+category['e_name']
            classify = category['name']
            e_name = category['e_name'].replace('-','_')
            yield scrapy.Request(url=url, callback=self.parse_news, dont_filter=True,
                                 meta={"info":(classify,e_name)})

    def parse_news(self,response):
        classify,e_name = response.meta.get('info')
        articles = response.xpath("//div[@class='largeTitle']//article[contains(@class,'js-article-item')]")
        for article in articles:
            link_url = article.xpath(".//div[@class='textDiv']/a/@href").get()
            link_url = response.urljoin(link_url)
            if xredis.sismember('flashnews:'+e_name, get_md5(link_url)):
                continue
            xredis.sadd('flashnews:'+e_name, get_md5(link_url))
            title = article.xpath(".//div[@class='textDiv']/a/text()").get()
            source = article.xpath(".//div[@class='textDiv']/span/span[1]/text()").get()
            source = source.replace('提供者','').strip()
            description = article.xpath(".//div[@class='textDiv']/p/text()").getall()
            description = list_to_str(description)
            yield scrapy.Request(url=link_url, callback=self.parse_time, dont_filter=True,
                                 meta={"info": (title,source,description,link_url,classify)})

    def parse_time(self,response):
        title,source,description,link_url,classify = response.meta.get('info')
        pub_time = response.xpath("//div[@class='contentSectionDetails']/span/text()").get()
        pub_time = re.search(r'\d+年\d+月\d+日 \d+:\d+', pub_time).group()
        pub_time = parse_pub_time(pub_time)
        content_list = []
        tags =  response.xpath("//div[@class='WYSIWYG articlePage']/*")
        for tag in tags:
            text = tag.xpath(".").get()
            if 'imgCarousel' in text:
                text = text.replace('visibility:hidden','')
            content_list.append(text)
        content = ''.join(content_list)
        website = '英为财情'
        item = FlashNewsItem(title=title,source=source,description=description,content=content,
                             link_url=link_url,classify=classify,pub_time=pub_time,website=website,
                             crawl_time=self.crawl_time)
        yield item