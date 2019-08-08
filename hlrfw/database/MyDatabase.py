#coding:utf-8
'''how to import this code
   import sys
   sys.path.append('/usr/local/lib/python2.7/site-packages/hlrfw')
'''

import pymysql

class MyDatabase(object):
    def modify_data(self, sql):
        '''
        - 执行sql语句
        '''
        conn = pymysql.connect(
            host = 'localhost',
            port = 3306,
            user = 'root',
            passwd = 'zhangroot',
            db = 'hlrfw_test',
            unix_socket='/var/run/mysqld/mysqld.sock',
            cursorclass = pymysql.cursors.DictCursor,
            )    
        cur = conn.cursor()
        try:
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            conn.rollback()
        finally:
            conn.close()
            cur.close()

    def select_last_data(self, sql):
        '''
        - 返回sql的最后一条数据
        '''
        conn = pymysql.connect(
            host = 'localhost',
            port = 3306,
            user = 'root',
            passwd = 'zhangroot',
            db = 'hlrfw_test',
            unix_socket='/var/run/mysqld/mysqld.sock',
            cursorclass = pymysql.cursors.DictCursor,
            )    
        cur = conn.cursor()   
        try:
            cur.execute(sql)
            select_data = cur.fetchone()
            return select_data
        except Exception as e:
            #print 'select data failed!'
            conn.rollback()
        finally:
            conn.close()
            cur.close()
            
    def select_all_data(slef, sql):
        '''
        - 返回所有符合sql语句的数据
        '''
        conn = pymysql.connect(
            host = 'localhost',
            port = 3306,
            user = 'root',
            passwd = 'zhangroot',
            db = 'hlrfw_test',
            unix_socket='/var/run/mysqld/mysqld.sock',
            cursorclass = pymysql.cursors.DictCursor,
            )    
        cur = conn.cursor()   
        try:
            cur.execute(sql)
            select_data = cur.fetchall()
            return select_data
        except Exception as e:
            #print 'select data failed!'
            conn.rollback()
        finally:
            conn.close()
            cur.close()
