# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from Astock.items import FlashNewsItem
from Astock.tools import get_md5
from Astock.settings import xredis



class FlashNewYiCaiSpider(scrapy.Spider):
    name = 'FlashNewYiCaiSpider'
    allowed_domains = ["yicai.com"]

    def __init__(self):
        super(FlashNewYiCaiSpider, self).__init__()
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def start_requests(self):
        url_jr = 'https://www.yicai.com/news/jinrong/'
        yield scrapy.Request(url=url_jr, callback=self.parse_list, dont_filter=True,meta={"info":"金融"})
        url_sj = 'https://www.yicai.com/news/shijie/'
        yield scrapy.Request(url=url_sj, callback=self.parse_list, dont_filter=True,meta={"info":"全球"})

    def parse_list(self,response):
        classify = response.meta.get("info")
        articles = response.xpath("//div[@id='newslist']/a")
        for article in articles:
            article_url = response.urljoin(article.xpath("./@href").get())
            if xredis.sismember('flashnews:yicai_news', get_md5(article_url)):
                continue
            xredis.sadd('flashnews:yicai_news', get_md5(article_url))
            yield scrapy.Request(url=article_url, callback=self.parse_detail, dont_filter=True, meta={"info": classify})

    def parse_detail(self,response):
        classify = response.meta.get("info")
        title = response.xpath("//div[@class='title f-pr']/h1/text()").get()
        pub_time = response.xpath("//div[@class='title f-pr']/p/em/text()").get()
        try:
            description = response.xpath("//div[@class='intro']/text()").get().strip()
        except:
            description = None
        content_list = []
        content_list.append(response.xpath("//div[@class='intro']").get())
        tags = response.xpath("//div[@class='m-txt']/*")
        for tag in tags:
            text = tag.xpath(".").get()
            if 'statement' in text:
                continue
            content_list.append(text)
        content = ''.join(content_list)
        content = re.sub('style="color:#000000;"','',content)
        source = '第一财经'
        website = '第一财经'
        link_url = response.url
        item = FlashNewsItem(link_url=link_url, title=title, pub_time=pub_time, description=description,
                             website=website,source=source, classify=classify, content=content,
                             crawl_time=self.crawl_time)
        yield item

