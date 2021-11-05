'''
使用說明:
1. 僅供以 pandas.df 對專題用的 MySQL db 進行資料的輸出,輸入 (不得修改SQL內容)
2. 匯入class --> from connect_MySQL import MysqlDataFrame
3. 需要匯入packages --> pymysql, pandas
4. 建立 MysqlDataFrame 物件 --> df = MysqlDataFrame('user', 'pwd', 'db')
5. df.show_info() --> 顯示現有的 databases, tables 等資訊
6. df.get_pandas_df("table名稱") --> 得到 pandas.df
7. df.use_sql_query("自己輸入的SQL語法") --> 得到 pandas.df
8. insert_pandas_df(df, "table名稱") --> 將 pandas.df 填入 MySQL
'''

import pymysql
import pandas as pd
import logging

class MysqlDataFrame:
    def __init__(self, user, pwd, db='test'):
        self.user = user
        self.pwd = pwd
        self.db = db
        self.__conn_ip = '10.2.16.174'
        self.__stopWords = [
            'alter', 'update', 'delete', 'drop', 'insert',
            'table', 'database'
            ]

    def __repr__(self):
        return '''
        1. Call "show_info()" to get the db & table list
        2. Call "get_pandas_df()" to get a pd.DataFrame from MySQL table
        3. Call "use_sql_query()" to get a pd.DataFrame with customized SQL 
        4. Call "insert_pandas_df()" to insert pd.DataFrame to MySQL 
        '''

    def create_conn(self):
        try:
            conn = pymysql.connect(
                host=self.__conn_ip, port=3306,
                user=self.user, passwd=self.pwd,
                db=self.db
                )
            return conn
        except Exception as err:
            print(logging.error(str(err)))

    def show_info(self):
        conn = self.create_conn()
        cursor = conn.cursor()

        # Get db list
        sql_db = 'SHOW databases;'
        cursor.execute(sql_db)
        db = [i[0] for j, i in enumerate(cursor.fetchall()) if (j > 4) & (j == 5)]
        # Get table list
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
        for word in self.__stopWords:
            if word in input_sql:
                return print("Please don't alter the data")
        df = pd.read_sql_query(input_sql, conn)
        conn.close()
        return df

    def insert_pandas_df(self, df, table):
        conn = self.create_conn()
        try:
            df.to_sql(table, conn, if_exist='append', index=0)
        except Exception as err:
            print(logging.error(str(err)))

