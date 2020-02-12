# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
#testing，development
import logging
import json
from Astock.settings import AsynDBConfig,xredis
from twisted.enterprise import adbapi


#整合所有Pieline
class MixDbPieline(object):
    def __init__(self):
        dbparams = AsynDBConfig
        self.dbpool = adbapi.ConnectionPool('pymysql', **dbparams)

    def process_item(self, item, spider):
        defer = self.dbpool.runInteraction(item.save, item)
        defer.addErrback(self.handle_error)
        return item

    def handle_error(self, error):
        print(error)


#需要调用接口的item处理,实时推送CT4实时热点
class ApiPieline(object):
    def process_item(self,item,spider):
        if item.need_api:
            try:
                resp = item.sapi(item=item)
                if resp.json()['code'] != 0:
                    logging.warning('Return Error !Parameter:%s！'%resp.text)
            except BaseException as e:
                logging.warning('Call Failed！%s'%e)
        return item


#向拜伦社推送消息
class BlsMqPieline(object):
    def process_item(self,item,spider):
        if 'SinaNews' in spider.name :
            try:
                resp = item.blsmqapi(item=item)
                if resp.json()["code"] != "0":
                    logging.warning('MQ Return Error ! Parameter:%s！' % resp.text)
                    xredis.rpush("mqfail_item",json.dumps(dict(item)))
            except Exception as e:
                logging.warning('MQ Push Error！%s' % e)
                xredis.rpush("mqfail_item", json.dumps(dict(item)))
        return item
