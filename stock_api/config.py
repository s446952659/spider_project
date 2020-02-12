#文件路径配置
ASTOCKFILEFATH = '../ct4data/Astocks.xlsx'
HKSTOCKFILEPATH = '../ct4data/HKstocks.xlsx'

#数据库连接配置
DBDevelopmentConfig = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'infodb',
    'charset': 'utf8',
}

DBTestingConfig = {
    'host': '',
    'port': 3306,
    'user': 'analyst',
    'password': '',
    'database': 'infodb',
    'charset': 'utf8',
}

dbconfig ={
    'development': DBDevelopmentConfig,
    'testing': DBTestingConfig,
}

china_sql_list=[
               'UPDATE china_basic_data set stock_name=%s WHERE stock_code=%s',
               'UPDATE china_change_ownership set stock_name=%s WHERE stock_code=%s',
               'UPDATE china_company_detail set stock_name=%s WHERE stock_code=%s',
               'UPDATE china_company_profile set stock_name=%s WHERE stock_code=%s',
               'UPDATE china_finance set stock_name=%s WHERE stock_code=%s',
               'UPDATE china_forecasts set stock_name=%s WHERE stock_code=%s',
               'UPDATE china_fund_data set stock_name=%s WHERE stock_code=%s',
               'UPDATE china_institution_hold set stock_name=%s WHERE stock_code=%s',
               'UPDATE china_news set stock_name=%s WHERE stock_code=%s',
               'UPDATE china_notice set stock_name=%s WHERE stock_code=%s',
               'UPDATE china_report set stock_name=%s WHERE stock_code=%s',
               ]

hk_sql_list = [
              'UPDATE hk_basic_data set stock_name=%s WHERE stock_code=%s',
              'UPDATE hk_change_ownership set stock_name=%s WHERE stock_code=%s',
              'UPDATE hk_company_profile set stock_name=%s WHERE stock_code=%s',
              'UPDATE hk_news set stock_name=%s WHERE stock_code=%s',
              'UPDATE hk_notice set stock_name=%s WHERE stock_code=%s',
              'UPDATE hk_finance set stock_name=%s WHERE stock_code=%s'
              ]
