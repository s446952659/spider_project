#!/bin/bash
crontab /var/spool/cron/crontabs/root
env >> /etc/default/locale
/etc/init.d/cron start
cd /ct4spider/stock_api && python3 stock_restfulapi.py