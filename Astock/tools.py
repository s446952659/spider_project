# -*- coding: utf-8 -*-
import datetime
import time
import hashlib
import re
import html
import requests
import json
import pymysql
from urllib import request
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from Astock.settings import imgfileconfig,NOWFILECONFIG,IMGSAVEPATH
from Astock.settings import xredis
from Astock.settings import DBConfig


def get_md5(old_str):
    hl = hashlib.md5()
    hl.update(old_str.encode("utf-8"))
    return hl.hexdigest()


def filt_htmlstr(htmlstr):
    res = re.sub('<[^<]+?>', '', htmlstr).replace('网页链接','')
    res_htmlstr = html.unescape(res)
    return res_htmlstr


def timestamptostr(timestamp):
    timeStamp = float(timestamp / 1000)
    timeArray = time.localtime(timeStamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", timeArray)


def strtotimestamp(timestr):
    if len(timestr) == 16:
        timestr = timestr + ":00"
    timeArray = time.strptime(timestr, "%Y-%m-%d %H:%M:%S")
    timeStamp = int(time.mktime(timeArray))
    return timeStamp


def list_to_str(plist):
    p_list = list(map(lambda x:re.sub('\s|\n|\t','',x),plist))
    p_str = ''.join(p_list)
    return p_str


def get_cookies():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://xueqiu.com/snowman/S/SZ000001/detail#/GSLRB')
    time.sleep(0.5)
    if 'captcha' in driver.current_url:
        proxy = "tps168.kdlapi.com:15818"
        chrome_options.add_argument("--proxy-server=%s" % proxy)
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://xueqiu.com/snowman/S/SZ000001/detail#/GSLRB')
        cookie = driver.get_cookies()
        return cookie
    cookie = driver.get_cookies()
    driver.quit()
    return cookie


#处理新浪新闻列表页时间
def timelist_conversion(t_list):
    title1 = list(map(lambda x: x.strip().replace(u'\xa0', u' '), t_list))
    title2 = [i for i in title1 if i != '']
    return title2


#解析图片尺寸
def parse_img(img_url):
    #img_name_=re.sub(r'[,。？?!！\.\\\/:：\*\|\<\>"\' “”、《》]', '', img_name)
    #img_name_ = img_name_ + img_url[-4:]
    img_name = get_md5(img_url)
    img_suffix = img_url[-4:]
    if img_suffix == 'ream':
        img_suffix = '.png'
    if 'http' not in img_url:
        img_url_ = 'http:' + img_url
    else:
        img_url_ = img_url
    try:
        request.urlretrieve(img_url_, IMGSAVEPATH + img_name + img_suffix)
        img = Image.open(IMGSAVEPATH + img_name + img_suffix)
        width, height = img.size
        return img_url_,width,height
    except:
        return (img_url_,0,0)


#处理文章简介
def parse_descr(descr_list):
    des = ''.join([i.strip().replace(u'\xa0', u'').replace(' ','') for i in descr_list])
    if len(des) > 128:
        descrption = des[:128] + '...'
        return descrption
    else:
        return des


#处理图片url,阿里oss，传入图片链接
def parse_img_url(img_url,article_url):
    if 'http' not in img_url:
        img_url_ = 'http:' + img_url
    else:
        img_url_ = img_url
    url = imgfileconfig[NOWFILECONFIG]
    data = {
        'Directory': 'stock/news/',
        'Url': img_url_,
        'GetInfo': True
    }
    headers = {'Content-Type': 'application/json'}
    try:
        resp = requests.post(url=url, data=json.dumps(data), headers=headers)
        resp_json = resp.json()
        if resp_json['code'] == '0':
            bodyMessage = json.loads(resp_json['bodyMessage'])
            bl_img_url = bodyMessage["url"]
            width = bodyMessage["width"]
            height = bodyMessage["height"]
            return bl_img_url,width,height
        else:
            xredis.rpush("imgfail", "IMG_URL:%s,ARTICLE_URL:%s,REASON:%s"%(img_url_,article_url,resp.text))
            return img_url_
    except Exception as e:
        xredis.rpush("imgfail", "IMG_URL:%s,ARTICLE_URL:%s,REASON:%s"%(img_url_,article_url,e))
        return img_url_


#过滤标签特殊的标签
def filter_divkey(tagtext):
    filter_divkeys = ['ct_hqimg','finance_app_zqtg','suda_1028_guba',
                      'artical-player-wrap','xb_new_finance_app','iframe','查看更多董秘问答']
    for key in filter_divkeys:
        if key in tagtext:
            return True
    return False


#过滤特殊的url链接
def filter_urlkey(url):
    filter_keys = ['7x24', 'live.finance.sina.com.cn', '8haolou', 'finance.sina.com.cn/jinrong',
                   'tech.sina.cn', 'finance.sina.cn']
    for key in filter_keys:
        if key in url:
            return True
    return False


#解析域名为finance，cj 的文章内容（新浪）
def parse_content(tags,link_url):
    content_list = []
    for tag in tags:
        text = tag.xpath(".").get()
        if filter_divkey(text):
            continue
        text = re.sub('<a.+?>','<a>',text)#去除a标签的链接
        if '<!--' in text and '<img' in text:  # 去除已经注释的图片内容
            continue
        if '<img' in text:  # 处理图片标签
            if 'data-original' in text:
                img_url = re.search('data-original="(.*?)"', text).group(1)
            else:
                img_url = re.search('src="(.*?)"', text).group(1)
            info_img = parse_img_url(img_url,link_url) #将图片转化成自己的链接
            if isinstance(info_img, tuple):
                bl_img_url, width, height = info_img
                img_text = '<img src="%s" data-width="%s" data-height="%s">' % (bl_img_url, width, height)
                text = re.sub('<img.+?>', img_text, text)
            else:
                origin_img_url, width, height = parse_img(img_url)
                img_text = '<img src="%s" data-width="%s" data-height="%s">' % (origin_img_url, width, height)
                text = re.sub('<img.+?>', img_text, text)
            content_list.append(text)
            continue
        content_list.append(text)
    return  ''.join(content_list)


#通过redis的集合，过滤去重文章链接
def filter_url(setname,link_url_md5):
    if xredis.exists(setname) == 1:
        if xredis.sismember(setname, link_url_md5):
            return True
        xredis.sadd(setname, link_url_md5)
    else:
        xredis.sadd(setname, link_url_md5)
        xredis.expire(setname, 2592000)
    return False


#解析daliyfx的新闻文章内容
def parse_daliyfx_content(text):
    pattern = re.compile('src="(.*?)"')
    imgurls = pattern.findall(text)
    if len(imgurls) != 0:
        for imgurl in imgurls:
            text = text.replace(imgurl, '自己的链接')
        return text
    return text


#总市值，流通市值
def calculate_yi(number_str,i):
    try:
        t = round(float(number_str)/100000000,i)
        t = str(t)+'亿'
        return t
    except:
        return '--亿'


#振幅，换手
def calculate_z(number_str,i):
    try:
        t = round(float(number_str),i)
        t = str(t)+'%'
        return t
    except:
        return '--'

#市盈率，市净率
def calculate_s(number_str,i):
    if number_str == '亏损':
        return number_str
    try:
        t = round(float(number_str),i)
        t = str(t)
        return t
    except:
        return '--'

#获取股票信息
def get_stock(type):
    conn = pymysql.connect(**DBConfig)
    cursor = conn.cursor()
    sql = 'SELECT * FROM %s '%type
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

#解析快讯文章发布时间
def parse_pub_time(old_time):
    _time = old_time.strip()
    year = re.search('(.*)年', _time).group(1)
    mon = re.search('年(.*)月', _time).group(1)
    day = re.search('月(.*)日', _time).group(1)
    time = re.search('日(.*)', _time).group(1)
    if len(mon) == 1:
        mon = '0' + mon
    if len(day) == 1:
        day = '0' + day
    new_time = year + '-' + mon + '-' + day + time + ':00'
    return new_time