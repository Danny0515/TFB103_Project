'''
使用說明:
#  僅供以 pandas.df 對專題用的 MySQL db 進行資料的輸出,輸入 (不得修改SQL內容)
1. 匯入class --> from connect_MySQL import MysqlDataFrame
2. 需要匯入packages --> pymysql, pandas, sqlalchemy.create_engine, logging
3. 建立 MysqlDataFrame 物件 --> df = MysqlDataFrame('user', 'pwd', 'db')
4  print(df) --> 可印出使用說明
5. df.show_info() --> 顯示現有的 databases, tables 等資訊
6. df.get_pandas_df("table名稱") --> 得到 pandas.df
7. df.use_sql_query("自己輸入的SQL語法") --> 得到 pandas.df
8. insert_pandas_df(df, "table名稱") --> 將 pandas.df 填入 MySQL
'''

import pandas as pd
import logging
from sqlalchemy import create_engine


class MysqlDataFrame:
    def __init__(self, user, pwd, db='tfb1031_project', ip='10.2.16.174'):
        self.user = user
        self.pwd = pwd
        self.db = db
        self.__conn_ip = ip
        self.__stopWords = [
            'alter', 'update', 'delete', 'drop', 'insert',
            'table', 'database'
            ]
        self.__sysDatabase = [
            'information_schema', 'performance_schema', 'mysql',
            'sakila', 'sys', 'world'
            ]

    def __repr__(self):
        return '''
        1. Call "show_info()" to get the db & table list
        2. Call "get_pandas_df()" to get a pd.DataFrame from MySQL table
        3. Call "use_sql_query()" to get a pd.DataFrame with customized SQL 
        4. Call "insert_pandas_df()" to insert pd.DataFrame to MySQL 
        '''

    def __create_conn(self):
        try:
            engine = create_engine(
                f'mysql+pymysql://{self.user}:{self.pwd}@{self.__conn_ip}:3306/{self.db}'
                )
            return engine
        except Exception as err:
            print(logging.error(str(err)))

    def show_info(self):
        engine = self.__create_conn()

        # Get db list
        sql_db = 'SHOW databases;'
        query_db = engine.execute(sql_db).fetchall()
        db = [i[0] for j, i in enumerate(query_db) if i[0] not in self.__sysDatabase]
        # Get table list
        sql_table = 'SHOW tables;'
        query_table = engine.execute(sql_table).fetchall()
        table = [i[0] for i in query_table]

        information = f'Use db = {self.db}\nUser = {self.user}\nDatabase list = {db}\nTable list =  {table}'
        return print(information)

    def get_pandas_df(self, table='test'):
        engine = self.__create_conn()
        sql = f'select * from {table};'
        try:
            df = pd.read_sql_query(sql, engine)
            return df
        except Exception as err:
            print(logging.error(str(err)))

    # Use user-defined SQL
    def use_sql_query(self, input_sql):
        engine = self.__create_conn()
        for word in self.__stopWords:
            if word in input_sql:
                return print("Please don't alter the data")
        try:
            df = pd.read_sql_query(input_sql, engine)
            return df
        except Exception as err:
            print(logging.error(str(err)))

    def insert_pandas_df(self, df, table):
        engine = self.__create_conn()
        try:
            df.to_sql(table, engine, if_exists='append', index=0)
        except Exception as err:
            print(logging.error(str(err)))

    def convert_str_to_list(self, df, column):
        import ast
        return df[f'{column}'].apply(lambda x: ast.literal_eval(x))

