# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import time
import base64
import random
from scrapy.http.response.html import HtmlResponse
from scrapy.exceptions import IgnoreRequest
import logging


class ChinaBasicDataDownloaderMiddleware(object):
    def process_request(self, request, spider):
        spider.driver.get(request.url)
        spider.driver.refresh()
        time.sleep(2)
        source = spider.driver.page_source
        response = HtmlResponse(url=spider.driver.current_url, body=source, request=request, encoding='utf-8')
        return response


class CompanyDetailDownloaderMiddleware(object):
    def process_request(self, request, spider):
        spider.driver.get(request.url)
        time.sleep(1)
        source = spider.driver.page_source
        response = HtmlResponse(url=spider.driver.current_url, body=source, request=request, encoding='utf-8')
        return response


class HKBasicDataDownloaderMiddleware(object):
    def process_request(self,request,spider):
        spider.driver.get(request.url)
        spider.driver.refresh()
        time.sleep(2)
        source = spider.driver.page_source
        response = HtmlResponse(url=spider.driver.current_url,body=source,request=request,encoding='utf-8')
        return response


class XueqiuTokenDownloaderMiddleware(object):
    def process_request(self, request, spider):
        if spider.name =='ChinaXueqiuFinance' :
            request.cookies=spider.cookies


class ProxyMiddleware(object):
    def __init__(self):
        # 隧道服务器
        self.tunnel_host = ""
        self.tunnel_port = ""
        # 隧道id和密码
        self.tid = ""
        self.password = ""

    def process_request(self, request, spider):
        if 'need_proxy' in request.meta :
            proxy_url = 'http://%s:%s@%s:%s' % (self.tid,self.password,self.tunnel_host,self.tunnel_port)
            request.meta['proxy'] = proxy_url  # 设置代理
            auth = "Basic %s" % (base64.b64encode(('%s:%s' % (self.tid,self.password)).encode('utf-8'))).decode('utf-8')
            request.headers['Proxy-Authorization'] = auth

    def process_response(self, request, response, spider):
        if spider.name=='ChinaReportApi' or spider.name == 'ChinaXueqiuFinance':
            if response.status != 200 :
                logging.warning('雪球网触发了代理！！！:%s'%request.url)
                request.meta['need_proxy'] = True
                return request
        if 'Sina' in spider.name:
            if 400 <= response.status < 500 :
                logging.warning('新浪网触发了代理！！！:%s' % request.url)
                request.meta['need_proxy'] = True
                return request
        return response


class UserAgentDownloaderMiddleware(object):
    def process_request(self,request,spider):
        USER_AGENTS = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A,'
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0',
            'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/44.0.2403.155 Safari/537.36',
        ]
        user_agent = random.choice(USER_AGENTS)
        request.headers['User-Agent'] = user_agent


class ContentFilterMiddleware(object):
    def process_response(self, request, response, spider):
        if 'Sina' in spider.name:
            if '公告内容详见附件' in response.text :
                raise IgnoreRequest
            if '无法查看当前文章' in response.text:
                raise IgnoreRequest
            if '秒钟之后将会带您进入新浪首页' in response.text:
                raise IgnoreRequest
        return response


