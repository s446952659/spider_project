# -*- coding: utf-8 -*-

# Scrapy settings for Astock project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'Astock'

SPIDER_MODULES = ['Astock.spiders']
NEWSPIDER_MODULE = 'Astock.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Astock (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 100
# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1

# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'Astock.middlewares.AstockSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'Astock.middlewares.XueqiuTokenDownloaderMiddleware': 300,
   #'Astock.middlewares.ProxyMiddleware': 400,
   'Astock.middlewares.UserAgentDownloaderMiddleware': 200,
   'Astock.middlewares.ContentFilterMiddleware':500
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'Astock.pipelines.MixDbPieline': 300,
   'Astock.pipelines.ApiPieline': 200,
   'Astock.pipelines.BlsMqPieline': 201,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'



# Scrapy-Redis相关配置
# 设置连接redis信息
REDIS_HOST = ''
REDIS_PORT = '6379'
REDIS_PARAMS = {
    'password': '',
}
# 确保所有爬虫共享相同的去重指纹
# DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# 在redis中保持scrapy-redis用到的队列，不会清理redis中的队列，从而可以实现暂停和恢复的功能。
SCHEDULER_PERSIST = True
#Bloom Filter
SCHEDULER = "scrapy_redis_bloomfilter.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis_bloomfilter.dupefilter.RFPDupeFilter"
BLOOMFILTER_HASH_NUMBER = 6
BLOOMFILTER_BIT = 30

#文件路径配置
ASTOCKFILEFATH = 'ct4data/Astocks.xlsx'
HKSTOCKFILEPATH = 'ct4data/HKstocks.xlsx'

# 日志配置
import datetime
now_time = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
LOG_LEVEL = "WARNING"
LOG_FILE = "Astock/log/scarpy_%s.log"%now_time

#redis连接配置
RedisTestConfig = {
    'host':'',
    'password': '',
    'db':1,
    'port':6379,
    'decode_responses':'True'
}
redisparams = RedisTestConfig
import redis
pool = redis.ConnectionPool(**redisparams)
xredis = redis.Redis(connection_pool=pool)

#mysql连接配置
from pymysql import cursors
#普通链接参数
DBConfig = {
    'host': '',
    'port': 3306,
    'user': 'analyst',
    'password': '',
    'database': 'infodb',
    'charset': 'utf8mb4',
    'cursorclass': cursors.DictCursor
}
#异步连接参数
AsynDBConfig = {
    'host': '',
    'port': 3306,
    'user': 'analyst',
    'password': '',
    'database': 'infodb',
    'charset': 'utf8mb4',
    'cp_reconnect':True,
    'cursorclass': cursors.DictCursor
}

#图片路径配置
IMGSAVEPATH = '/newsimg/'

#拜伦社服务器接口地址配置
blsconfig = {
    'development':'',
    'testing':'',
    'production':''
}
NOWBLSCONFIG = 'testing'

#MQ消息队列服务接口地址
mqconfig = {
    'development':'',
    'testing':'',
    'production':''
}
NOWMQCONFIG = 'testing'

#图片文件上传地址
imgfileconfig = {
    'testing':'',
    'production':''
}
NOWFILECONFIG = 'testing'

#CT4服务器接口地址配置
ct4config = {
    'development':'',
    'testing':'',
    'production':'',
}
NOWCT4CONFIG = 'testing'