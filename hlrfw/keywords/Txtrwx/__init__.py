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

LOG_PATH = '/home/pi/production/log/'

class Txtrwx(object):
    def __init__(self):
        self.log_path = LOG_PATH = '/home/pi/production/log/'
        
    def txtrwx_write_file(self, *str_, filepath=LOG_PATH+'主板检测日志.txt'):
        '''
        文件写入
        '''
        f1 = open(filepath, 'a')
        for i in str_:
            f1.writelines('<' + i + '>')
        f1.writelines('\n\n')
        f1.flush()
        f1.close()

    def txtrwx_setid_file_write(self,*str,filepath=LOG_PATH+'Tbox_参数.txt'):
        '''
        文件写入
        '''
        f = open(filepath,'a')
        for i in str:
            if i != '\n':
                f.writelines(i+'  ')
            else:
                f.writelines(i)
        f.flush()
        f.close()

    def txtrwx_pid_set(self,str_):
        '''
        功能:PID比较并写入配置文件
        参数:被设置的PID
        实例:pid_set|'6850001'
        '''
        pid_1 = str_[:3]
        pid_2 = int(str_[-4:])
        pid_2 += 1
        pid_2 = str(pid_2)
        while len(pid_2)<4:
            pid_2 = '0'+pid_2
        with open('/home/pi/production/ID_param.py','a') as f:
            f.write('\n'+'pid_start = '+ '\''+pid_1+pid_2+'\''+'\n')

    def txtrwx_box_did_set(self,deviceid,judge):
        '''
        功能:TBOX或ABOX设置信息写入配置文件
        参数:设置的deviceid，t或者a(代表tbox的还是abox的)
        实例:box_did_set|010101181200000001|t
        '''
        deviceid = int(deviceid)
        deviceid += 1
        if judge =='t':
            with open('/home/pi/production/ID_param.py','a') as f:
                f.write('\n'+'tbox_did_start = '+'\''+'0'+ str(deviceid)+'\''+'\n')
        else:
            with open('/home/pi/production/ID_param.py','a') as f:
                f.write('\n'+'abox_did_start = '+'\''+'0'+ str(deviceid)+'\''+'\n')
    
    def txtrwx_box_cid_set(self,clientid,judge):
        '''
        功能:TBOX或ABOX设置信息写入配置文件
        参数:设置的clientid，t或者a(代表tbox的还是abox的)
        实例:box_did_set|GID_T3_Group@@@010101181200000001|t
        '''
        clientid = int(clientid[-4:])
        print(clientid)
        clientid += 1
        if judge == 't':
            with open('/home/pi/production/ID_param.py','a') as f:
                f.write('tbox_cid_start = '+'\''+'GID_T3_Group@@@01010118120000'+ str(clientid)+'\''+'\n')
        else:
            with open('/home/pi/production/ID_param.py','a') as f:
                f.write('abox_cid_start = '+'\''+'GID_T3_Group@@@01020118120000'+ str(clientid)+'\''+'\n')

    def txtrwx_abox_file_write(self,*str_,filepath=LOG_PATH+'abox_log.txt'):
        '''
        文件写入
        '''
        f1 = open(filepath, 'a')
        for i in str_:
            f1.writelines('<' + i + '>')
        f1.writelines('\n\n')
        f1.flush()
        f1.close()
        
        
    def txtrwx_zhengji_file_write(self,*str_,filepath=LOG_PATH+'整机检测日志.txt'):
        '''
        文件写入
        '''
        f1 = open(filepath, 'a')
        for i in str_:
            f1.writelines('<' + i + '>')
        f1.writelines('\n\n')
        f1.flush()
        f1.close()

    def txtrwx_quality_file_write(self,*str,filepath='/home/pi/production/quality_log.txt'):
        '''
        文件写入
        '''
        f1 = open(filepath, 'a')
        for i in str_:
            f1.writelines('<' + i + '>')
        f1.writelines('\n\n')
        f1.flush()
        f1.close()

    def txtrwx_ser_test(self):
        count = 0
        ser = serial.Serial("/dev/ttyAMA0",baudrate=9600,timeout=5)
        
        f = open('/home/pi/ama0log.txt', 'a')
        s = ser.read(512)
        try:
            s = s.decode('utf-8','ignore')
        except:
            print('a error in recv msg')
        print(s,len(s))
        f.write(s)
        if s.find('$')==-1 or len(s)<64:
            return -1
            #f.write(s)
        else:
            return 0


    def txtrwx_mid_file_write(self,*str_,filepath='/home/pi/production/mid.txt'):
        f1 = open(filepath, 'a')
        for i in str_:
            f1.writelines('<' + i + '>')
        f1.writelines('\n\n')
        f1.flush()
        f1.close()

    def txtrwx_mid_file_rm(self):
        os.system('sudo rm -rf /home/pi/production/mid.txt')
        
        
    def txtrwx_read(self,file_name):
        txtrwx_value  = []
        if not os.path.exists(file_name):
            print('文件不存在')
        
        txtrwx_read = open(file_name,'r')
        txtrwx_value = txtrwx_read.read()
        #for i in txtrwx_read_value:
            #txtrwx_value.append(i) 
        #print(txtrwx_value)
        txtrwx_read.close()
        
        return txtrwx_value
        
    def txtrwx_delet(self,file_name):
        if os.path.exists(file_name):
            os.system('sudo rm -rf ' + file_name)
        else:
            print('文件不存在')
    
    def txtrwx_transfer(self,a,b):
        m = self.txtrwx_read(a)
        with open(b,'a') as f:
            f. write(m)
            f.flush()
        
            
        
           
    