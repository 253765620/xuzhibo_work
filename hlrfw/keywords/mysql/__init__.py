#!coding:utf-8
import sys
if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')

import re
import os
import time
import random
from socket import *
from ftplib import FTP
from decimal import Decimal
    
try:
    import pymysql as mdb
    from hlrfw.database.MyDatabase import MyDatabase
except:
    print('do not have pymysql')

class Mysql(object):
	def mysql_link_backdic(self, sql):
        '''
        执行sql语句,返回字典
        '''
        m_data = MyDatabase()
        return m_data.select_all_data(sql)

    def mysql_link_backtup(self, sql):
        '''
        执行sql语句,返回元组
        '''
        host_ = '192.168.3.' + str(LOCALIP)
        conn = mdb.connect(host=host_,port=3306,user='root',database='hlrfw_test',password='zhangroot')
        cursor = conn.cursor()
        cursor.execute(sql)
        datacur = cursor.fetchall()
        conn.close()
        cursor.close()
        return datacur
    