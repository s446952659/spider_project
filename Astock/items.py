# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import json
import requests
from Astock.settings import ct4config,NOWCT4CONFIG,blsconfig,NOWBLSCONFIG,mqconfig,NOWMQCONFIG
from Astock.tools import strtotimestamp


#A股基本信息
class BasicDataItem(scrapy.Item):
    stock_code = scrapy.Field()
    stock_market = scrapy.Field()
    stock_name = scrapy.Field()
    tchange = scrapy.Field()  # 换手
    tvalue = scrapy.Field()  # 总市值
    tvaluep = scrapy.Field()  # 市净率
    trange = scrapy.Field()  # 振幅
    flowvalue = scrapy.Field() # 流通市值
    fvaluep = scrapy.Field()  # 市赢率（动）
    crawl_time = scrapy.Field()
    need_api = False

    def save(self, cursor, item):
        #sql = "replace into china_basic_data(stock_code,stock_name,stock_market,trange,tchange,tvalue,tvaluep,flowvalue,fvaluep,crawl_time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        sql = "insert into china_basic_data(stock_code,stock_name,stock_market,trange,tchange,tvalue,tvaluep,flowvalue,fvaluep,crawl_time)" \
              " values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update stock_name=%s,stock_market=%s,trange=%s,tchange=%s,tvalue=%s,tvaluep=%s,flowvalue=%s,fvaluep=%s,crawl_time=%s"
        params = [item['stock_code'], item['stock_name'], item['stock_market'],item['trange'], item['tchange'], item['tvalue'],item['tvaluep'],item['flowvalue'],item['fvaluep'],item['crawl_time']
                  , item['stock_name'], item['stock_market'],item['trange'], item['tchange'], item['tvalue'],item['tvaluep'],item['flowvalue'],item['fvaluep'],item['crawl_time']]
        cursor.execute(sql, params)


#A股公司简介
class CompanyProfileItem(scrapy.Item):
    stock_code = scrapy.Field()
    stock_market = scrapy.Field()
    stock_name = scrapy.Field()
    area = scrapy.Field() # 地区
    concept = scrapy.Field()  # 涉及概念
    main_business = scrapy.Field() # 主营业务
    launch_date = scrapy.Field()  # 上市日期
    per_share = scrapy.Field()  # 每股净资产
    per_earning = scrapy.Field()  # 每股收益
    profit = scrapy.Field() # 净利润
    profit_growth = scrapy.Field()  # 净利润增长率
    income = scrapy.Field()  # 营业收入
    cash_flow = scrapy.Field()  # 现金流
    fund = scrapy.Field()  # 公积金
    undistributed_profit = scrapy.Field()  # 每股未分配利润
    total_equity = scrapy.Field()  # 总股本
    shares_outstanding = scrapy.Field() #流通股
    crawl_time = scrapy.Field()
    need_api = False

    def save(self, cursor, item):
        #sql = "replace into china_company_profile(stock_code,stock_name,stock_market,area,concept,main_business,launch_date,per_share,per_earning,profit,profit_growth,income,cash_flow,fund,undistributed_profit,total_equity,shares_outstanding,crawl_time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        sql = "insert into china_company_profile(stock_code,stock_name,stock_market,area,concept,main_business,launch_date,per_share,per_earning,profit,profit_growth,income,cash_flow,fund,undistributed_profit,total_equity,shares_outstanding,crawl_time) " \
              "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update " \
              "stock_name=%s,stock_market=%s,area=%s,concept=%s,main_business=%s,launch_date=%s,per_share=%s,per_earning=%s,profit=%s,profit_growth=%s,income=%s,cash_flow=%s,fund=%s,undistributed_profit=%s,total_equity=%s,shares_outstanding=%s,crawl_time=%s"
        params = [item['stock_code'],item['stock_name'],item['stock_market'],item['area'], item['concept'], item['main_business'],item['launch_date'],
                  item['per_share'],item['per_earning'],item['profit'],item['profit_growth'],item['income'],item['cash_flow'],
                  item['fund'],item['undistributed_profit'],item['total_equity'],item['shares_outstanding'],item['crawl_time'],
                  item['stock_name'], item['stock_market'], item['area'], item['concept'], item['main_business'],item['launch_date'],
                  item['per_share'], item['per_earning'], item['profit'], item['profit_growth'], item['income'],item['cash_flow'],
                  item['fund'], item['undistributed_profit'], item['total_equity'], item['shares_outstanding'],item['crawl_time']
                  ]
        cursor.execute(sql, params)


#A股公司公告
class CompanyNoticeItem(scrapy.Item):
    stock_code = scrapy.Field()
    stock_market = scrapy.Field()
    stock_name = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    link_url = scrapy.Field()
    link_url_md5 = scrapy.Field()
    pub_time = scrapy.Field()
    crawl_time = scrapy.Field()
    website = scrapy.Field()
    source = scrapy.Field()
    need_api = False

    def save(self, cursor, item):
        sql = "insert into china_notice(stock_code,stock_name,stock_market,title,content,link_url,link_url_md5,pub_time,website,source,crawl_time) " \
              "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update stock_code=%s,stock_name=%s,stock_market=%s,title=%s,content=%s," \
              "link_url=%s,pub_time=%s,website=%s,source=%s,crawl_time=%s"
        params = [item['stock_code'], item['stock_name'], item['stock_market'],item['title'], item['content'],item['link_url'],item['link_url_md5'],item['pub_time'],item['website'],item['source'],item['crawl_time'],
                  item['stock_code'], item['stock_name'], item['stock_market'], item['title'], item['content'],item['link_url'], item['pub_time'],item['website'],item['source'], item['crawl_time']]
        cursor.execute(sql, params)


#A股新闻(BLS&CT4_API)
class CompanyNewsItem(scrapy.Item):
    stock_code = scrapy.Field()
    stock_market = scrapy.Field()
    stock_name = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    content = scrapy.Field()
    link_url = scrapy.Field()
    link_url_md5 = scrapy.Field()
    pub_time = scrapy.Field()
    website = scrapy.Field()
    source = scrapy.Field()
    crawl_time = scrapy.Field()
    need_api = False

    def save(self, cursor, item):
        sql = "insert into china_news(stock_code,stock_name,stock_market,title,description,link_url,link_url_md5,pub_time,content," \
              "website,source,crawl_time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) " \
              "on duplicate key update stock_code=%s,stock_name=%s,stock_market=%s,title=%s,description=%s,link_url=%s,pub_time=%s,content=%s,website=%s,source=%s,crawl_time=%s"
        params = [item['stock_code'],item['stock_name'],item['stock_market'],item['title'],item['description'],
                  item['link_url'],item['link_url_md5'],item['pub_time'],item['content'],item['website'],item['source'],item['crawl_time'],
                  item['stock_code'], item['stock_name'], item['stock_market'], item['title'], item['description'],
                  item['link_url'], item['pub_time'], item['content'], item['website'],
                  item['source'], item['crawl_time']
                  ]
        cursor.execute(sql, params)

    def blsmqapi(self,item):
        url = mqconfig[NOWMQCONFIG]
        requestBody = {
            "brief": item['description'],
            "content": item['content'],
            "link": item['link_url'],
            "md5": item['link_url_md5'],
            "pubTime": item['pub_time'],
            "source": item['source'],
            "stockId": item['stock_market'] + '_' + item['stock_code'],
            "title": item['title'],
            "website": item['website'],
            "pubTimeLong":strtotimestamp(item['pub_time'])
        }
        data = {
            "delaySeconds": 0,
            "discardErrorMessage": False,
            "ip": "192.168.5.3",
            "queryParam": None,
            "requestBody": json.dumps(requestBody),
            "requestMethod": 2,
            "siteType": 14,
            "url": blsconfig[NOWBLSCONFIG]
        }
        headers = {'Content-Type': 'application/json'}
        return requests.post(url=url, data=json.dumps(data), headers=headers)


#A股公司研报
class ResearchReportItem(scrapy.Item):
    stock_code = scrapy.Field()
    stock_market = scrapy.Field()
    stock_name = scrapy.Field()
    title = scrapy.Field()
    status = scrapy.Field()
    description = scrapy.Field()
    link_url = scrapy.Field()
    article_id = scrapy.Field()
    pub_time = scrapy.Field()
    content = scrapy.Field()
    website = scrapy.Field()
    source = scrapy.Field()
    crawl_time = scrapy.Field()
    need_api = False

    def save(self, cursor, item):
        sql = "insert into china_report(stock_code,stock_name,stock_market,title,status,description,link_url,article_id,pub_time,content,website,source,crawl_time) " \
              "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update stock_code=%s,stock_name=%s,stock_market=%s,title=%s,status=%s,description=%s,link_url=%s,pub_time=%s,content=%s,website=%s,source=%s,crawl_time=%s"
        params = [item['stock_code'],item['stock_name'],item['stock_market'],item['title'],item['status'],
                  item['description'],item['link_url'],item['article_id'],item['pub_time'],item['content'],item['website'],item['source'],
                  item['crawl_time'],item['stock_code'],item['stock_name'],item['stock_market'],item['title'],
                  item['status'],item['description'],item['link_url'],item['pub_time'],item['content'],item['website'],item['source'],
                  item['crawl_time']]
        cursor.execute(sql, params)


##A股公司详细情况
class CompanyDetailItem(scrapy.Item):
    stock_code = scrapy.Field()
    stock_market = scrapy.Field()
    stock_name = scrapy.Field()
    c_name = scrapy.Field()#中文名
    area = scrapy.Field()#地区
    e_name = scrapy.Field()#英文名
    industry = scrapy.Field()#行业
    used_name = scrapy.Field()#曾用名
    web_site = scrapy.Field()#网址
    main_business = scrapy.Field()#主营业务
    product_name = scrapy.Field()#产品名称
    shareholder = scrapy.Field()#股东
    actual_controller = scrapy.Field()#实际控制人
    ultimate_controller = scrapy.Field()#最终控制人
    chairman = scrapy.Field()#董事长
    chairman_secretary = scrapy.Field()#董事长秘书
    legal_persion = scrapy.Field()#法人代表
    general_manager = scrapy.Field()#总经理
    registered_capital = scrapy.Field()#注册资金
    number = scrapy.Field()#员工人数
    telephone = scrapy.Field()#电话
    fax = scrapy.Field()#传真
    zip_code = scrapy.Field()#邮编
    address = scrapy.Field()#办公地址
    intro = scrapy.Field()#公司简介
    crawl_time = scrapy.Field()
    need_api = False

    def save(self, cursor, item):
        sql = '''replace into china_company_detail(stock_code,stock_name,stock_market,c_name,
               area,e_name,industry,used_name,web_site,main_business,product_name,shareholder,actual_controller,ultimate_controller,
               chairman,chairman_secretary,legal_persion,general_manager,registered_capital,number,telephone,fax,zip_code,
               address,intro,crawl_time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        params = [item['stock_code'],item['stock_name'],item['stock_market'],item['c_name'],
                  item['area'],item['e_name'],item['industry'],item['used_name'],
                  item['web_site'],item['main_business'],item['product_name'],item['shareholder'],
                  item['actual_controller'],item['ultimate_controller'],item['chairman'],item['chairman_secretary'],
                  item['legal_persion'],item['general_manager'],item['registered_capital'],item['number'],
                  item['telephone'],item['fax'],item['zip_code'],item['address'],
                  item['intro'],item['crawl_time']]
        cursor.execute(sql, params)


#A股公司持股变动
class ChangeOwnershipItem(scrapy.Item):
    stock_code = scrapy.Field()
    stock_market = scrapy.Field()
    stock_name = scrapy.Field()
    detaileds_hold =scrapy.Field()
    crawl_time = scrapy.Field()
    need_api = False

    def save(self, cursor, item):
        sql = "insert into china_change_ownership(stock_code,stock_name,stock_market,detaileds_hold,crawl_time)" \
              " values (%s,%s,%s,%s,%s) on duplicate key update stock_name=%s,stock_market=%s,detaileds_hold=%s,crawl_time=%s"
        params = [item['stock_code'], item['stock_name'], item['stock_market'],item['detaileds_hold'],item['crawl_time'],
                  item['stock_name'], item['stock_market'], item['detaileds_hold'], item['crawl_time']
                  ]
        cursor.execute(sql, params)


#A股公司持股机构
class InstitutionalHoldItem(scrapy.Item):
    stock_code = scrapy.Field()
    stock_market = scrapy.Field()
    stock_name = scrapy.Field()
    detail_hold =scrapy.Field()
    summary_hold = scrapy.Field()
    crawl_time = scrapy.Field()
    need_api = False

    def save(self, cursor, item):
        sql = "insert into china_institution_hold(stock_code,stock_name,stock_market,summary_hold,detail_hold,crawl_time)" \
              " values (%s,%s,%s,%s,%s,%s) on duplicate key update stock_name=%s,stock_market=%s,summary_hold=%s,detail_hold=%s,crawl_time=%s"
        params = [item['stock_code'],item['stock_name'],item['stock_market'],item['summary_hold'],item['detail_hold'],item['crawl_time'],
                  item['stock_name'], item['stock_market'], item['summary_hold'], item['detail_hold'],item['crawl_time']
                  ]
        cursor.execute(sql, params)


#A股公司业绩预测
class ForecastsItem(scrapy.Item):
    stock_code = scrapy.Field()
    stock_market = scrapy.Field()
    stock_name = scrapy.Field()
    eper_share = scrapy.Field()
    profit = scrapy.Field()
    crawl_time = scrapy.Field()
    need_api = False

    def save(self, cursor, item):
        sql = "insert into china_forecasts(stock_code,stock_name,stock_market,eper_share,profit,crawl_time)" \
              " values (%s,%s,%s,%s,%s,%s) on duplicate key update stock_name=%s,stock_market=%s,eper_share=%s,profit=%s,crawl_time=%s"
        params = [item['stock_code'],item['stock_name'],item['stock_market'],item['eper_share'],item['profit'],item['crawl_time'],
                  item['stock_name'], item['stock_market'], item['eper_share'], item['profit'], item['crawl_time']
                  ]
        cursor.execute(sql, params)


#A股公司历史资金数据
class FundItem(scrapy.Item):
    stock_code = scrapy.Field()
    stock_market = scrapy.Field()
    stock_name = scrapy.Field()
    fund_data = scrapy.Field()
    crawl_time = scrapy.Field()
    need_api = False

    def save(self, cursor, item):
        sql = "insert into china_fund_data(stock_code,stock_name,stock_market,fund_data,crawl_time)" \
              " values (%s,%s,%s,%s,%s) on duplicate key update stock_name=%s,stock_market=%s,fund_data=%s,crawl_time=%s"
        params = [item['stock_code'],item['stock_name'],item['stock_market'],item['fund_data'],item['crawl_time'],
                  item['stock_name'], item['stock_market'], item['fund_data'], item['crawl_time']
                  ]
        cursor.execute(sql, params)


#A股财务指标负债表(雪球网)
class XueqiuFinanceDebtItem(scrapy.Item):
    stock_code = scrapy.Field()
    stock_market = scrapy.Field()
    stock_name = scrapy.Field()
    debt_report = scrapy.Field()
    debt_year = scrapy.Field()
    debt_quarter = scrapy.Field()
    crawl_time = scrapy.Field()
    need_api = False

    def save(self,cursor,item):
        sql = "insert into china_finance_debt(stock_code,stock_name,stock_market,debt_report,debt_year,debt_quarter,crawl_time) " \
              "values (%s,%s,%s,%s,%s,%s,%s) on duplicate key update stock_name=%s,stock_market=%s,debt_report=%s," \
              "debt_year=%s,debt_quarter=%s,crawl_time=%s"
        params = [item['stock_code'], item['stock_name'], item['stock_market'],
                  item['debt_report'],item['debt_year'],item['debt_quarter'],
                  item['crawl_time'], item['stock_name'], item['stock_market'],
                  item['debt_report'],item['debt_year'],item['debt_quarter'],
                  item['crawl_time'],]
        cursor.execute(sql, params)


#A股财务指标利润表(雪球网)
class XueqiuFinanceBenifitItem(scrapy.Item):
    stock_code = scrapy.Field()
    stock_market = scrapy.Field()
    stock_name = scrapy.Field()
    benifit_report = scrapy.Field()
    benifit_year = scrapy.Field()
    benifit_quarter = scrapy.Field()
    crawl_time = scrapy.Field()
    need_api = False

    def save(self,cursor,item):
        sql = "insert into china_finance_benifit(stock_code,stock_name,stock_market," \
              "benifit_report,benifit_year,benifit_quarter,crawl_time) " \
              "values (%s,%s,%s,%s,%s,%s,%s) on duplicate key update stock_name=%s,stock_market=%s," \
              "benifit_report=%s,benifit_year=%s,benifit_quarter=%s,crawl_time=%s"
        params = [item['stock_code'], item['stock_name'], item['stock_market'],
                  item['benifit_report'], item['benifit_year'], item['benifit_quarter'],
                  item['crawl_time'], item['stock_name'], item['stock_market'],
                  item['benifit_report'], item['benifit_year'], item['benifit_quarter'],
                  item['crawl_time'],]
        cursor.execute(sql, params)


#A股财务指标现金流(雪球网)
class XueqiuFinanceCashItem(scrapy.Item):
    stock_code = scrapy.Field()
    stock_market = scrapy.Field()
    stock_name = scrapy.Field()
    cash_report = scrapy.Field()
    cash_year = scrapy.Field()
    cash_quarter = scrapy.Field()
    crawl_time = scrapy.Field()
    need_api = False

    def save(self,cursor,item):
        sql = "insert into china_finance_cash(stock_code,stock_name,stock_market,cash_report,cash_year,cash_quarter,crawl_time) " \
              "values (%s,%s,%s,%s,%s,%s,%s) on duplicate key update stock_name=%s,stock_market=%s,"  \
              "cash_report=%s,cash_year=%s,cash_quarter=%s,crawl_time=%s"
        params = [item['stock_code'], item['stock_name'], item['stock_market'],
                  item['cash_report'], item['cash_year'], item['cash_quarter'],
                  item['crawl_time'], item['stock_name'], item['stock_market'],
                  item['cash_report'], item['cash_year'], item['cash_quarter'],
                  item['crawl_time'],]
        cursor.execute(sql, params)


#港股基本信息
class HKBasicDataItem(scrapy.Item):
    stock_code = scrapy.Field()
    stock_market = scrapy.Field()
    stock_name = scrapy.Field()
    tchange = scrapy.Field()  # 换手
    trange = scrapy.Field()  # 振幅
    tvalue = scrapy.Field()  # 总市值
    tvaluep = scrapy.Field()  # 市净率
    flowvalue = scrapy.Field()  # 流通市值
    fvaluep = scrapy.Field()  # 市赢率（动）
    total_equity = scrapy.Field()  #总股本
    earnper_share = scrapy.Field() #每股收益
    crawl_time = scrapy.Field()
    need_api = False

    def save(self,cursor,item):
        sql = "insert into hk_basic_data(stock_code,stock_name,stock_market,tchange,trange,tvalue,tvaluep,flowvalue,fvaluep,total_equity,earnper_share,crawl_time) " \
              "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)  on duplicate key update " \
              "stock_name=%s,stock_market=%s,tchange=%s,trange=%s,tvalue=%s,tvaluep=%s,flowvalue=%s,fvaluep=%s,total_equity=%s" \
              ",earnper_share=%s,crawl_time=%s"
        params = [item['stock_code'],item['stock_name'],item['stock_market'],item['tchange'],item['trange'],
                  item['tvalue'],item['tvaluep'], item['flowvalue'], item['fvaluep'],item['total_equity'], item['earnper_share'],item['crawl_time'],
                  item['stock_name'], item['stock_market'], item['tchange'], item['trange'],
                 item['tvalue'], item['tvaluep'], item['flowvalue'], item['fvaluep'], item['total_equity'], item['earnper_share'], item['crawl_time']]
        cursor.execute(sql,params)


#港股持股变动
class HKChangeOwnershipItem(scrapy.Item):
    stock_code = scrapy.Field()
    stock_market = scrapy.Field()
    stock_name = scrapy.Field()
    detaileds_hold = scrapy.Field()
    crawl_time = scrapy.Field()
    need_api = False

    def save(self,cursor,item):
        sql = "insert into hk_change_ownership(stock_code,stock_name,stock_market,detaileds_hold,crawl_time)" \
              " values (%s,%s,%s,%s,%s) on duplicate key update stock_name=%s,stock_market=%s,detaileds_hold=%s,crawl_time=%s"
        params = [item['stock_code'],item['stock_name'],item['stock_market'],item['detaileds_hold'],item['crawl_time'],
                  item['stock_name'], item['stock_market'], item['detaileds_hold'], item['crawl_time']
                  ]
        #参数化查询防止依赖注入
        cursor.execute(sql,params)


#港股公司基本信息
class HKCompanyProfileItem(scrapy.Item):
    stock_code = scrapy.Field()
    stock_market = scrapy.Field()
    stock_name = scrapy.Field()
    launch_date = scrapy.Field()
    c_name = scrapy.Field()
    address = scrapy.Field()
    telephone = scrapy.Field()
    website = scrapy.Field()
    profile = scrapy.Field()
    crawl_time = scrapy.Field()
    need_api = False

    def save(self, cursor, item):
        sql = "insert into hk_company_profile(stock_code,stock_name,stock_market,launch_date,c_name,address,telephone,website,profile,crawl_time)" \
              " values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update stock_name=%s,stock_market=%s,launch_date=%s," \
              "c_name=%s,address=%s,telephone=%s,website=%s,profile=%s,crawl_time=%s"
        params = [item['stock_code'],item['stock_name'],item['stock_market'],item['launch_date'],item['c_name'],item['address'],
                 item['telephone'],item['website'],item['profile'],item['crawl_time'],item['stock_name'],item['stock_market'],item['launch_date'],item['c_name'],item['address'],
                 item['telephone'],item['website'],item['profile'],item['crawl_time']]
        cursor.execute(sql, params)


#港股公司新闻(BLS&CT4_API)
class HKCompanyNewsItem(scrapy.Item):
    stock_code = scrapy.Field()
    stock_market = scrapy.Field()
    stock_name = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    content = scrapy.Field()
    link_url = scrapy.Field()
    link_url_md5 = scrapy.Field()
    pub_time = scrapy.Field()
    website = scrapy.Field()
    source = scrapy.Field()
    crawl_time = scrapy.Field()
    need_api = False

    def save(self, cursor, item):
        sql = "replace into hk_news(stock_code,stock_name,stock_market,title,description,link_url,link_url_md5,pub_time,content," \
              "website,source,crawl_time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        params = [item['stock_code'], item['stock_name'], item['stock_market'], item['title'], item['description'],
                  item['link_url'], item['link_url_md5'], item['pub_time'], item['content'], item['website'],
                  item['source'], item['crawl_time']]
        cursor.execute(sql, params)

    def blsmqapi(self, item):
        url = mqconfig[NOWMQCONFIG]
        requestBody = {
            "brief": item['description'],
            "content": item['content'],
            "link": item['link_url'],
            "md5": item['link_url_md5'],
            "pubTime": item['pub_time'],
            "source": item['source'],
            "stockId":  item['stock_market'] + '_' + item['stock_code'],
            "title": item['title'],
            "website": item['website'],
            "pubTimeLong": strtotimestamp(item['pub_time'])
        }
        data = {
            "delaySeconds": 0,
            "discardErrorMessage": False,
            "ip": "192.168.5.3",
            "queryParam": None,
            "requestBody": json.dumps(requestBody),
            "requestMethod": 2,
            "siteType": 14,
            "url": blsconfig[NOWBLSCONFIG]
        }
        headers = {'Content-Type': 'application/json'}
        return requests.post(url=url, data=json.dumps(data), headers=headers)


#港股公司公告
class HKCompanyNoticeItem(scrapy.Item):
    stock_code = scrapy.Field()
    stock_market = scrapy.Field()
    stock_name = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    link_url = scrapy.Field()
    link_url_md5 = scrapy.Field()
    pub_time = scrapy.Field()
    crawl_time = scrapy.Field()
    website = scrapy.Field()
    source = scrapy.Field()
    need_api = False

    def save(self, cursor, item):
        sql = "replace into hk_notice(stock_code,stock_name,stock_market,title,content,link_url,link_url_md5,pub_time,website,source,crawl_time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        params = [item['stock_code'], item['stock_name'], item['stock_market'], item['title'], item['content'],
                  item['link_url'], item['link_url_md5'], item['pub_time'],item['website'], item['source'], item['crawl_time']]
        cursor.execute(sql, params)


#热点资讯（API）
class FlashNewsItem(scrapy.Item):
    title = scrapy.Field()
    pub_time = scrapy.Field()
    description = scrapy.Field()
    content = scrapy.Field()
    link_url = scrapy.Field()
    source = scrapy.Field()
    classify = scrapy.Field()
    crawl_time = scrapy.Field()
    website = scrapy.Field()
    need_api = True

    def save(self, cursor, item):
        sql = "insert into flashnews(title,pub_time,description,content,link_url,source,classify,website,crawl_time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        params = [item['title'], item['pub_time'], item['description'], item['content'],item['link_url'], item['source'],
                  item['classify'],item['website'],item['crawl_time']]
        cursor.execute(sql, params)

    def sapi(self,item):
        url = ct4config[NOWCT4CONFIG]
        data = {
            'title': item['title'],
            'pub_time': item['pub_time'],
            'description': item['description'],
            'content':item['content'],
            'source':item['source'],
            'classify':item['classify'],
            'link_url': item['link_url'],
            'website':item['website'],
            'crawl_time': item['crawl_time']
        }
        return requests.post(url=url,data=json.dumps(data))


#港股财经
class HKFinanceItem(scrapy.Item):
    stock_code = scrapy.Field()
    stock_market = scrapy.Field()
    stock_name = scrapy.Field()
    debt_year = scrapy.Field()
    benefit_year = scrapy.Field()
    cash_year = scrapy.Field()
    crawl_time = scrapy.Field()
    need_api = False

    def save(self, cursor, item):
        sql = "insert into hk_finance(stock_code,stock_market,stock_name,debt_year,benefit_year,cash_year,crawl_time)" \
              " values (%s,%s,%s,%s,%s,%s,%s) on duplicate key update stock_market=%s,stock_name=%s,debt_year=%s,benefit_year=%s," \
              "cash_year=%s,crawl_time=%s"
        params = [item['stock_code'], item['stock_market'], item['stock_name'], item['debt_year'],
                  item['benefit_year'],item['cash_year'], item['crawl_time'], item['stock_market'],
                  item['stock_name'], item['debt_year'],
                  item['benefit_year'],item['cash_year'], item['crawl_time']]
        cursor.execute(sql, params)