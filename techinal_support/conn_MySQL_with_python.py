'''
先確認有以下 packages
pip install sqlalchemy
pip install pymysql
pip install pandas
'''


import pandas as pd
from sqlalchemy import create_engine

# 使用 pymysql 模組，建立資料庫連線
engine = create_engine('mysql+pymysql://<database_user>:<pwd>@<hostIP>:<port>/<db>')

# 把 MySQL 搜尋結果轉成 pd.DataFrame
sql = 'select * from test;'
df = pd.read_sql_query(sql, engine)

# 將 pd.DataFrame 儲存到 MySQL 的 table (不儲存index)
df.to_sql('mpg', engine, index=False)

# 使用 SQL 語法並接收結果 --> tuple
engine.execute('sql').fetchall()