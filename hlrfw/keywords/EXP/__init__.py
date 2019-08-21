#!coding:utf-8
import sys
if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')
import serial
from multiprocessing import Process
import re
import os
import time
import random
from socket import *
from ftplib import FTP
from decimal import Decimal
from time import sleep
from hlrfw.configs.ip_config import myip as LOCALIP
try:
    import pymysql as mdb
    from hlrfw.database.MyDatabase import MyDatabase
except:
    print('do not have pymysql')
    
class EXP(object):
    def exp_hextime_to_timestamp(self, hex_time):
        '''
        将120101010101类似的hex时间转化为对应的时间戳
        
        例子:
        | ${i} | hextime2timestamp | 120101010101 |#返回的就是20180101010101
        '''
        int_time = '20'
        for i in range(int(len(hex_time)/2)):
            str_time = str(int(hex_time[i*2:i*2+2],16))
            if len(str_time) == 1:
                str_time = '0' + str_time
            int_time = int_time + str_time
            
        timeArray = time.strptime(int_time, '%Y%m%d%H%M%S')
        mytimestamp = int(time.mktime(timeArray))
        return mytimestamp
    
    def exp_abs(self, data):
        '''
        取算式的绝对值并且返回
        
        例子:
        | ${i} | abs | 2+2-5 |#返回的就是5
        '''
        return abs(data)
    
 #   def exp_loc_ip_req(self):
 #       '''
 #       获取本地IP,并且返回
 #
 #       例子:
 #       | ${i} | req_loc_ip |#返回的是IP后三位数字
  #      '''
  #      return LOCALIP
        
    def exp_vin_random(self):
        '''
        生成随机VIN码
        '''
        vin_1 = 'VINSTR'
        vin_2 = random.randint(10000, 99999)
        vin_2 = str(vin_2)
        vin_3 = random.randint(100000, 999999)
        vin_3 = str(vin_3)
        vin = vin_1 + vin_2 + vin_3
        return vin

    def exp_str_spilt(self, mystr, symbol):
        '''
        字符串切片，返回数列
        '''
        return mystr.split(symbol)
    
    def exp_serial_str_spilt(self, str_, num1, num2=None):
        '''
        功能：
        - 解析串口字符串
        
        参数:
        - str_: 需要分析的字符串
        - num1: 需要返回的字符串的开始位置
        - num2: 需要返回的字符串的结束位置
        
        例子:
        | get_param_str | abc,def;gh:qq | 1 | 3 | #就会返回第1到第3个字符 |
        | get_param_str | abc,def;gh:qq | 1 | #就会返回第1个字符 |
        '''
        num1 = int(num1)
        if not num2:
            num2 = num1
        else:
            num2 = int(num2)
        print(re.split('[;:|, ]+', str_))
        return re.split('[;:|, ]+', str_)[num1-1:num2]
    
#    def get_str_1(self, str_, num1, num2=None):
#        '''
#        功能：
#        - 解析串口字符串
#
#        参数:
#        - str_: 需要分析的字符串
#        - num1: 需要返回的字符串的开始位置
#        - num2: 需要返回的字符串的结束位置
#
#        例子:
#        | get_param_str | abc,def;gh:qq | 1 | 3 | #就会返回第1和第3个字符 |
#        '''
#        num1 = int(num1)
#        if not num2:
#            num2 = num1
#        else:
#            num2 = int(num2)
#        print(re.split('[ ;:,]+', str_)[:-1])
#        a = re.split('[ ;:,]+', str_)[:-1][num1-1:num2]
#        return a[0]

#    def get_str_2(self, str_, num1):
#        '''
#        功能：
#        - 解析串口字符串
#
#        参数:
#        - str_: 需要分析的字符串
#        - num1: 需要返回的字符串的开始位置
#        - num2: 需要返回的字符串的结束位置
#
#        例子:
#        | get_param_str | abc,def;gh:qq | 1 | #就会返回第1和第3个字符 |
#        '''
#        num1 = int(num1)
#        a = re.split('[ ;:,]+', str_)
#        return a[num1]

    def exp_flag_one_query(self,str1,str2,num):
        '''
        - param str1: 串口返回的内容
        - param str2: 需要查询的字符串
        - param num: 对应的第几位
        - return: 第几位的值
        '''
        list_1 = re.split(r'[ |,:;]',str1)
        list_2 = []
        if str2 in list_1:
            n =list_1.index(str2)
            m =list_1[n+1]
            for i in m:
                list_2.append(i)
            print(list_2)
            l = len(list_2)
            num = int(num)
            if num<l :
                return list_2[l-num]
            else:
                return ('输入的数字超过搜索范围')
        else:
            return ('没有这项字符串')
        
    def exp_flag_more_query(self,str1,str2,num1,num2=None):
        '''
        :param str1: 串口返回的内容
        :param str2: 需要查询的字符串
        :return: 需要查询的字符串对应冒号后面内容(必须为数字)
        '''
        num1 = int(num1)
        if not num2:
            num2 = num1
        else:
            num2 = int(num2)
        list_1 = re.split(r'[ |,:;]',str1)
        print(list_1)       
        if str2 in list_1:
            n =list_1.index(str2)
            m =list_1[n+num1:n+num2+1]
            k = ','.join(m)
            return  k
        else:
            print('没找到{}字段'.format(str2))
            return -1
        
    def exp_int_change(self,num1):
        '''把列表的某一项转成整型'''
        return int(num1)
    
    def exp_str_find(self,str_):
        print(str_)
        return str_.find('成功')
    
    def exp_flag_judge(self,str1,*args):
        '''
        :param str1:被解析的字符串
        :param args:需要查询的唤醒方式
        :return:能查询到返回1 否正返回-1
        '''
        FLAG = {
            1: 'ACC唤醒',
            32: 'CAN1唤醒',
            31: 'CAN2唤醒',
            30: 'CAN3唤醒',
            29: 'CAN4唤醒',
            28: 'CAN5唤醒',
            3: '报警唤醒',
            4: '电源电压状态变化唤醒',
            5: '网络唤醒',
            6: '电话唤醒',
            7: '短信唤醒',
            8: '电池唤醒',
            9: '电池供电状态下，外电接入时唤醒',
            10: '蓝牙连接唤醒',
            11: '解析CAN报文的指定字段匹配时唤醒',
            12: ' BCALL唤醒',
            13: 'ECALL唤醒',
            14: 'ICALL唤醒',
            15: '动态开启模块',
            16: 'LIN远程唤醒',
            17: '动态开启CAN，进行CAN报文过滤',
            18: 'ON唤醒',
            19: '振动唤醒',
        }
        a = self.exp_flag_more_query(str1,'FLAG',1)
        count = 0
        list_1 = []
        list_2 = []
        list_3 = []
        for j in args:
            list_3.append(j)
        for i  in a :
            count+=1
            if i =='1':
                list_1.append(count)
        for key,val in FLAG.items():
            for b in list_1:
                if b == key:
                    list_2.append(val)
        if list_3==list_2:
            return 1
        else:
            return -1
        
#    def p_string(self,str1,num):
#        num = int(num)
#        list_ = re.split(r'[,]',str1)
#        return list_[num-1]
    
    def exp_belong(self,str1,str2):
        '''
        功能:判断字符串1是否在字符串2里面(成功返回1否则返回0)
        参数:str1:查询的字符串  str2:被查询的字符串
        实例:belong|cunzai|shifoucunzai
        '''
        if str1.find(str2)!= -1:
            return 1
        else:
            return 0
    def bestr(self,res):
        return str(res)


    def exp_local_time_query(self):
        the_time = time.time()
        return str(the_time)

    def get_local_time(self):
        the_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        return the_time
    
    def exp_sub(self,sz1,sz2):
        '''
        功能:做差(保留2位小数，针对小数点后面数字很多的)
        参数:sz1,sz2都为数值
        实例:round_int|2.3056|2.3641
        '''
        sz1 = float(sz1)
        sz2 = float(sz2)
        sz = sz2-sz1
        return Decimal(sz).quantize(Decimal('0.00'))


#    def box_cid_set(self,clientid,judge):
#       '''
#        功能:TBOX或ABOX设置信息写入配置文件
#        参数:设置的clientid，t或者a(代表tbox的还是abox的)
#        实例:box_did_set|GID_T3_Group@@@010101181200000001|t
#        '''
#        clientid = int(clientid[-4:])
#        print(clientid)
#        clientid += 1
#        if judge == 't':
#            with open('/home/pi/production/ID_param.py','a') as f:
#                f.write('tbox_cid_start = '+'\''+'GID_T3_Group@@@01010118120000'+ str(clientid)+'\''+'\n')
#        else:
#            with open('/home/pi/production/ID_param.py','a') as f:
#                f.write('abox_cid_start = '+'\''+'GID_T3_Group@@@01020118120000'+ str(clientid)+'\''+'\n')

    def exp_id_judge(self,start,end):
        '''
        功能:对设置的id做判断,通过返回0否则返回1
        参数:start：开始的序列号，end结束的序列号
        实例:id_judge|6850001|6851000
        '''
        start = int(start[-4:])
        print(start)
        end = int(end[-4:])
        print(end)
        if start<=end:
            return 0
        else:
            return 1
            
    def exp_timestamp(self):
        #获取当前时间戳
        return int(time.time())
    
    def exp_length(self,str_):
        return len(str(str_))
    
#    def lanya(self,str_):
#        a = re.split('[ ;:,]+', str_)
#        return a[-1]

    def use_ama0_recv(self,baud=115200):
        ser = serial.Serial("/dev/ttyAMA0",baudrate=baud,timeout=5)
        count = 0
        while 1:
            s = ser.read()
            try:
                s = s.decode('utf-8','ignore')
            except:
                print('a error in recv msg')
            print(s)
            if s != '':
                return s
            count +=1
            if count > 5:
                return '0'
    
    def return_int(self,str_):
        return int(str_)

    def close_jdq(self):
        os.system('sudo python3.7 /home/pi/hlrfw/drives/drives_test/antenna_control.py')
        
    def exp_generate_pid(self,str_):
        a = str_[2]
        b = int(a,16)
        b = str(b)
        if len(b)<2:
            b = '0'+str(b)
        c = str_[0:2]
        d = str_[3:]
        f = c+b+d
        return f
    
    def exp_generate_id(self,m,n,date,pid):
        tbox_d = '010102'
        tbox_c = 'GID_T3_Group@@@010102'
        abox_d = '010202'
        abox_c = 'GID_T3_Group@@@010202'
        date = date[2:6]
        if m == 't':
            if n == 'd':
                id = tbox_d+date+self.exp_generate_pid(pid)
            else:
                id = tbox_c+date+self.exp_generate_pid(pid)
        if m == 'a':
            if n == 'd':
                id = abox_d+date+self.exp_generate_pid(pid)
            else:
                id = abox_c+date+self.exp_generate_pid(pid)
        return id
    
    def exp_ping(self,url,timeout):
        these_time = time.time()
        cmd = "ping -c 1 \"%s\" " % (url)
        for i in range(int(timeout)):
            result = os.system(cmd)
            result >>= 8
            #print(result)
            if result:
                #print('ping fail')
                last_time = time.time()
                time_difference = int(last_time - these_time)
                #print('sub:{}'.format(time_difference))
                if time_difference >= int(timeout):
                    #print('sub')
                    print('ping fail')
                    result_time  = '{}'.format(time_difference) + 's'
                    break
            else:
                print('ping success')
                last_time = time.time()
                time_difference = int(last_time - these_time)
                #print(time_difference)
                result_time = '{}'.format(time_difference) + 's'
                break
        return (result,result_time ) 
    
        
if __name__  ==  "__main__":
    a = EXP()
    b = a.exp_generate_id('c','d','2018','6850001')
    print(b)