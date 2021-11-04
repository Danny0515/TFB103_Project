'''
使用說明:
1. 僅供把 MySQL table 取出並轉為 pandas.df (不得修改SQL內容)
2. 匯入class --> from connect_MySQL import MysqlDataFrame
3. 需要匯入packages --> pymysql, pandas
4. 建立 MysqlDataFrame 物件 --> df = MysqlDataFrame('user', 'pwd', 'db')
5. df.show_info() --> 顯示現有的 databases, tables 等資訊
6. df.get_pandas_df("table名稱") --> 得到 pandas.df
7. df.use_sql_query("自己輸入的SQL語法") --> 得到 pandas.df
'''

import pymysql
import pandas as pd

class MysqlDataFrame:
    def __init__(self, user, pwd, db='test'):
        self.user = user
        self.pwd = pwd
        self.ip = 'Connect to: 10.2.16.174'
        self.db = db

    def __repr__(self):
        return '''
        1. Call "show_info()" to get the db & table list
        2. Call "get_pandas_df()" to get a pd.DataFrame from MySQL table
        3. Call "use_sql_query()" to get a pd.DataFrame with customized SQL 
        '''

    def create_conn(self):
        conn = pymysql.connect(
            host='10.2.16.174', port=3306,
            user=self.user, passwd=self.pwd,
            db=self.db
            )
        return conn

    def show_info(self):
        conn = self.create_conn()
        cursor = conn.cursor()

        sql_db = 'SHOW databases;'
        cursor.execute(sql_db)
        db = [i[0] for j, i in enumerate(cursor.fetchall()) if (j > 4) & (j == 5)]

        sql_table = 'SHOW tables;'
        cursor.execute(sql_table)
        table = [i[0] for i in cursor.fetchall()]

        conn.commit()
        cursor.close()
        conn.close()
        information = f'Use db = {self.db}\nUser = {self.user}\nDB list = {db}\nTable list =  {table}'
        return print(information)

    def get_pandas_df(self, table='test'):
        conn = self.create_conn()
        sql = f'select * from {table};'
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df

    # Use user-defined SQL
    def use_sql_query(self, input_sql):
        conn = self.create_conn()
        df = pd.read_sql_query(input_sql, conn)
        conn.close()
        return df

