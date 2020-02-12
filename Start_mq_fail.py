# -*- coding: utf-8 -*-
import requests
import json
import logging
from Astock.settings import xredis,blsconfig,NOWBLSCONFIG,mqconfig,NOWMQCONFIG
from Astock.tools import strtotimestamp
import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


for i in range(xredis.llen('mqfail_item')):
    item = xredis.lpop('mqfail_item')
    item = json.loads(item)
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
        "website": item['webside'],
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
    try:
        resp = requests.post(url=url, data=json.dumps(data), headers=headers)
        print(resp.text)
        if resp.json()["code"] != "0":
            logging.warning('mq消息推送失败!错误参数:%s！' % resp.text)
            xredis.rpush("mqfail_item", json.dumps(dict(item)))
    except Exception as e:
        logging.warning('mq接口调用失败！%s' % e)
        xredis.rpush("mqfail_item", json.dumps(dict(item)))

