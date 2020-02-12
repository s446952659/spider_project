# -*- coding: utf-8 -*-
import scrapy
import datetime
import re
from Astock.items import FlashNewsItem
from Astock.settings import xredis
from Astock.tools import get_md5,parse_daliyfx_content,parse_pub_time


class FlashNewDailyFxSpider(scrapy.Spider):
    name = 'FlashNewDailyFx'
    allowed_domains = ['dailyfxasia.com']
    start_urls = ['https://www.dailyfxasia.com/market-news-articles']

    def __init__(self):
        super(FlashNewDailyFxSpider, self).__init__()
        self.filter_keys = '按图放大|点此了解您最关注的货币对在每天最为波动的时段，保证在正确的时间进行交易|点此下载交易展望报告，提升全球金融市场交易信心，掌握高级交易策略以及工具！|如何有效利用基本面分析？点此获取掌握交易核心技能的三部曲'
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def parse(self, response):
        lis = response.xpath("//ul[@id='dfx-scrolled-block']//li")
        for li in lis:
            link_url = li.xpath(".//div[2]/h3/a/@href").get().strip()
            if xredis.sismember('flashnews:forex_news', get_md5(link_url)):
                continue
            xredis.sadd('flashnews:forex_news', get_md5(link_url))
            title = li.xpath(".//div[2]/h3/a/text()").get().strip()
            pub_time =li.xpath(".//div[1]/h3/text()").get()
            pub_time = parse_pub_time(pub_time)
            description =li.xpath(".//div[2]/div/text()").get().strip()
            yield scrapy.Request(url=link_url, callback=self.parse_content, dont_filter=True,
                                meta={"info": (title,link_url,pub_time,description)})

    def parse_content(self,response):
        title,link_url,pub_time,description =response.meta.get("info")
        content = response.xpath(".//div[@class='dfx-article-content']").get()
        content = re.sub('<a class="dfx-article-view-image".*?</a>','',content)
        content = re.sub(self.filter_keys,'',content)
        content = re.sub('style="color:#333333"|style="background-color:white"', '', content)
        if '<table' in content:
            table_content = re.compile('<table[\d\D]*?/table>')
            result = table_content.findall(content)
            for text in result:
                text_br = '<br><br>' + text + '<br>'
                content = content.replace(text,text_br)
        #content = re.sub('<a.*?>', '<a>', content)
        website = 'dailyfx'
        source = 'dailyfx'
        classify = '外汇'
        item = FlashNewsItem(link_url=link_url,title=title,pub_time=pub_time,description=description,website=website,
                             source=source,classify=classify,content=content,crawl_time=self.crawl_time)
        yield item





