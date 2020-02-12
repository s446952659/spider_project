FROM registry-vpc.cn-shenzhen.aliyuncs.com/stl-test/scrapy_base:v2.0

ADD . /ct4spider

WORKDIR /ct4spider/stock_api/

COPY root /var/spool/cron/crontabs/root

COPY docker_crontab.sh ./docker_crontab.sh

RUN python3 -m pip install scrapy-redis-bloomfilter -i http://pypi.douban.com/simple --trusted-host pypi.douban.com

RUN chmod +x ./docker_crontab.sh

ENTRYPOINT ["./docker_crontab.sh"]

#CMD ./docker_crontab.sh

EXPOSE 9000