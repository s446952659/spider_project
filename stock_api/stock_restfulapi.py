# coding: utf8
from flask import Flask
from flask_restful import Api,Resource,reqparse
from config import dbconfig,china_sql_list,hk_sql_list,ASTOCKFILEFATH,HKSTOCKFILEPATH
import pandas as pd
import pymysql


app = Flask(__name__)
api = Api(app)

# development testing
dbparams = dbconfig['testing']


def check_stock(table_name,code):
    conn = pymysql.connect(**dbparams)
    cursor = conn.cursor()
    sql = 'SELECT * FROM %s WHERE code=%s'%(table_name,code)
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def insert_stock(table_name,code,market,name):
    conn = pymysql.connect(**dbparams)
    cursor = conn.cursor()
    sql = 'INSERT INTO %s(code,market,name) values ("%s","%s","%s")' %(table_name,code,market,name)
    print(sql)
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()


def update_stock(table_name,code,market,name):
    conn = pymysql.connect(**dbparams)
    cursor = conn.cursor()
    sql = 'UPDATE %s SET market="%s",name="%s" WHERE code=%s' % (table_name,market,name,code)
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()


@app.route('/')
def hello_world():
    return 'Hello World!'


class AddStockApi(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('code',type=str,help='code填写错误！',required=True)
        parser.add_argument('market',type=str,help='market填写错误！',required=True)
        parser.add_argument('name',type=str,help='name填写错误！',required=True)
        #0,表示A股；1，表示港股；
        parser.add_argument('type',type=int,choices=[0,1,2,3,4],required=True)
        args = parser.parse_args()
        #添加A股信息
        if args['type'] == 0:
            if len(args['code']) == 6:
                result = check_stock('china_data_source',args['code'])
                if len(result) == 0 : # 等于 0 表示该数据库中没有该股票数据
                    insert_stock('china_data_source',args['code'],args['market'],args['name'])
                else:
                    return {"bodycode":"1","message":"股票代码已存在！"}
            else:
                return {"bodycode":"1","message":"A股code填写错误！"}
        #添加港股信息
        if args['type'] == 1:
            if len(args['code']) == 5:
                result = check_stock('hk_data_source', args['code'])
                if len(result) == 0 : # 等于 0 表示该数据库中没有该股票数据
                    insert_stock('hk_data_source', args['code'], args['market'], args['name'])
                else:
                    return {"bodycode":"1","message":"股票代码已存在！"}
            else:
                return {"bodycode":"1","message":"港股code填写错误！"}
        return {"bodycode":"0","message":"新增成功"}


class UpdateStockApi(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('code',type=str,help='code填写错误！',required=True)
        parser.add_argument('market',type=str,help='market填写错误！',required=True)
        parser.add_argument('name',type=str,help='name填写错误！',required=True)
        #0,表示A股；1，表示港股；
        parser.add_argument('type',type=int,choices=[0,1,2,3,4],required=True)
        args = parser.parse_args()
        #更新A股信息
        if args['type'] == 0:
            if len(args['code']) == 6:
                result = check_stock('china_data_source', args['code'])
                if len(result) != 0: # 不等于 0 表示该数据库中有
                    update_stock('china_data_source',args['code'],args['market'],args['name'])
                    #更改数据库信息
                    conn = pymysql.connect(**dbparams)
                    cursor = conn.cursor()
                    for sql in china_sql_list:
                        cursor.execute(sql,(args['name'],args['code']))
                        conn.commit()
                else:
                    return {"bodycode":"1","message":"更新的股票不在表中！"}
            else:
                return {"bodycode": "1", "message": "A股code填写错误！"}
        #更新港股信息
        if args['type'] == 1:
            if len(args['code']) == 5:
                result = check_stock('hk_data_source', args['code'])
                if len(result) != 0: # 不等于 0 表示该数据库中有
                    update_stock('hk_data_source',args['code'],args['market'],args['name'])
                    # 更改数据库信息
                    conn = pymysql.connect(**dbparams)
                    cursor = conn.cursor()
                    for sql in hk_sql_list:
                        cursor.execute(sql, (args['name'], args['code']))
                        conn.commit()
                else:
                    return {"bodycode": "1", "message": "更新的股票不在表中！"}
            else:
                return {"bodycode": "1", "message": "港股code填写错误！"}
        return {"bodycode":"0","message": "更新成功！"}


api.add_resource(AddStockApi,'/api/add/stock/')
api.add_resource(UpdateStockApi,'/api/update/stock/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)