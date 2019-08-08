#coding:utf-8
'''
功能:
- 启动这个脚本，会储持续采集电流大小，并且存储到数据库
- 插入的时候启动了一个线程, 是因为树梅派插入数据库的时候, 有时候有点卡, 时效性不好
'''
import sys
import time
import pymysql
import threading
from os import path
from sys import path as path2
path2.append(path.abspath(path.join(__file__,'../../..')))

from hlrfw.drives.pcf8591 import Pcf8591

# param 全局锁
LOCK =  threading.Lock()

class DataBase(object):
    def __init__(self):
        self.creat_conn_cur()
    
    def creat_conn_cur(self):
        '''
        - 创建数据库游标
        '''
        self.conn = pymysql.connect(
            host = 'localhost',
            port = 3306,
            user = 'root',
            passwd = 'zhangroot',
            db = 'hlrfw_test',
            unix_socket='/var/run/mysqld/mysqld.sock',
            cursorclass = pymysql.cursors.DictCursor,
            )
        self.cur = self.conn.cursor()
    
    def clean(self):
        '''
        - 关闭数据库游标
        '''
        self.conn.close()
        self.cur.close()
        

class CollectPower(DataBase):
    def __init__(self, freq_inter):
        self.curr_volt_obj = Pcf8591()
        self.now_curr = 0
        self.now_volt = 0
        self.timestamp = 0
        self.freq_inter = float(freq_inter)/1000
        super(CollectPower, self).__init__()

    def get_real_curr(self):
        '''
        - 获取实时电流大小
        '''
        sum1 = 0
        avg_curr = 0
        times = (self.freq_inter*1000)/10
        list = []
        #print(times)
        for i in range(int(times)):
            self.now_curr = round(self.curr_volt_obj.get_now_curr()*1000, 8)
            list.append(self.now_curr)
        max1 = max(list)
        min1 = min(list)
        list.remove(max1)
        list.remove(min1)
        #print(len(list))
        sum1 = sum(list)
            #sum = sum + self.now_curr
        self.now_curr = round((sum1)/(len(list)),1)
        #self.now_curr = round((sum)/(times),1)
        #self.now_curr = round(self.curr_volt_obj.get_now_curr()*1000, 1)
        return self.now_curr

    def get_real_volt(self):
        '''
        - 获取实时电压大小
        '''
        self.now_volt = round(self.curr_volt_obj.read_pin(1)*11, 2)
    
    def get_timestamp(self):
        '''
        - 获取欧当前时间戳
        '''
        self.timestamp = float('%.3f' % time.time())
    
    def save_data(self):
        '''
        - 存储数据到数据库
        '''
        try:
            db = DataBase()
            sql = 'insert into real_ter_power_data(time_pi, current, voltage) values({0}, {1}, {2});'.format(self.timestamp, self.now_curr, self.now_volt)
            db.cur.execute(sql)
            db.conn.commit()
            db.clean()
        except Exception as e:
            print(e)
            db.conn.rollback()

    def start_thread(self):
        '''
        - 开始存储数据线程
        '''
        t = threading.Thread(target=self.save_data)
        t.setDaemon(True)
        t.start()

    def main(self):
        '''
        - 执行入口
        '''
        while 1:
            self.get_real_curr()
            print(self.now_curr)
            self.get_real_volt()
            self.get_timestamp()
            self.start_thread()
            time.sleep(self.freq_inter)


if __name__ == "__main__":
    # freq_inter 参数是采集频率ms
    file_name, freq_inter = sys.argv
    col_pow = CollectPower(freq_inter)
    col_pow.main()
