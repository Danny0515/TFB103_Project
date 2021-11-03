'''
pip install sqlalchemy
pip install pymysql
'''


# 使用 pymysql 模組，建立資料庫連線
engine = create_engine('mysql+pymysql://<database_user>:<pwd>@<hostIP>:<port>/<db>')
# 把 MySQL 搜尋結果轉成 pd.DataFrame
pd.read_sql_query(sql, engine)
# 將 pd.DataFrame 儲存到 MySQL 的 table (不儲存index)
df.to_sql('mpg', engine, index=0)

# ===================== 下面直接複製就可以丟資料到 MySQL local server =====================
import pandas as pd
from sqlalchemy import create_engine


engine = create_engine('mysql+pymysql://tfb1031_test:qwe123456@10.2.16.174:3306/tfb1031_project')
sql = '''
select * from testTable;
'''
df = pd.read_sql_query(sql, engine)


# ===================== 上面直接複製就可以丟資料到 MySQL local server =====================