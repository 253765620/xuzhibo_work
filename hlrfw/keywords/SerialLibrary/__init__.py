# -*- coding: utf-8 -*-
'''
- 串口关键字
- 实际上是使用socket发送数据给串口平台
- 串口平台代码位置 hlrfw/scritp/serail_handle
'''
import sys
if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')
from multiprocessing import Process
import time
import datetime
import socket
import serial
from robot.api import logger
from robot.utils import asserts
from hlrfw.configs.ip_config import IP_SERIAL_USB0,IP_SERIAL_AMA0,IP_SERIAL_USB3,IP_SERIAL_USB2,IP_SERIAL_USB1
from hlrfw.configs.sys_config import SERIAL_LOG_USB0,SERIAL_LOG_USB1,SERIAL_LOG_USB2,SERIAL_LOG_USB3
from hlrfw.keywords.SerialLibrary.serial_func import split_msg
from time import sleep
import threading
import os
from hlrfw.keywords.Power import *

class SerialLibrary(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def serial_send(self, send_data, receive_data, return_time=None, baudrate=115200, wait_time=3, repeat=2, is_error=False,ser_ip='0'):
        '''
        功能:
        - 发送并接收串口数据
        - 通过条件 : 接收到期待的串口数据
        
        参数:
        - send_data : 发送的数据
        - receive_data : 接收的数据
        - return_time : 是否返回时间(True 是)
        - baudrate : 波特率
        - wait_time : 超时时间
        - repeat : 重发次数
        - is_error : 代表是否报错，如果填入如True,就算没有收到指定的数据也不会报错
        - ser_ip:

        返回:
        - 当 return_time 填写 True 时就会返回查询的系统时间

        例子:
        | serial_send | IOT+S3 | IOT | return_time=None | baudrate=115200 | wait_time=3 | repeat=2 | is_error=False | ser_ip=0|
        '''
        self.is_error = is_error
        self.send_data = send_data
        self.receive_data = receive_data
        self.return_time = return_time
        self.baudrate = baudrate
        if ser_ip == '0':
            self.ser_ip = IP_SERIAL_USB0
        elif ser_ip == 1:
            self.ser_ip = IP_SERIAL_USB1
        elif ser_ip == 2:
            self.ser_ip = IP_SERIAL_USB2
        elif ser_ip == 3:
            self.ser_ip = IP_SERIAL_USB3
        else:
            self.ser_ip = IP_SERIAL_AMA0
        #print("$$$")
        print(self.ser_ip)
        self.wait_time = int(wait_time)
        if self.wait_time > 5:
            repeat = 1
        self.repeat = int(repeat)
        self.send_res = False
        self._log_serial_info()
        return self._send_to_serial_platform(self.ser_ip)
    
    def serial_ter_log_search(self, search_time, search_cont):
        '''
        功能:
        - 查询终端串口日志
        
        参数:
        - search_time: 查询多久以前的参数(s)
        - search_cont: 查询的内容(比如模块重启信息poweroff)
        
        返回:
        - 未找到匹配数据, 返回-1
        - 找到匹配数据, 返回找到的那行数据
        '''
        search_res = serial_ter_log_search(search_time, search_cont)
        print('查找结果: ', search_res)
        if search_res == -1 or not search_res:
            return  -1
        else:
            return search_res
    #def serial_ama0_send(self,send_data, receive_data, return_time=None, baudrate=115200, wait_time=3, repeat=2, is_error=False,ser_ip='ama0'):
    #    self.ama0_is_error = is_error
    #    self.ama0_send_data = send_data
    #    self.ama0_receive_data = receive_data
    #    self.ama0_return_time = return_time
    #    self.ama0_baudrate = baudrate
    #    self.ama0_wait_time = int(wait_time)
    #    self.ama0_repeat = int(repeat)
    #    self.ama0_ser = ser_ip
        #print(self.usb_wait_time)
    #    usb_ser_value = self.serial_send(self.ama0_send_data,self.ama0_receive_data,baudrate=self.ama0_baudrate,
    #                                     wait_time=self.ama0_wait_time,repeat=self.ama0_repeat,ser_ip=self.ama0_ser) 
    #    
    #    value = self.serial_send(send_data, receive_data, return_time=None, baudrate=115200, wait_time=3, repeat=2, is_error=False,ser_ip='ama0')
    #    return (value)
    #def serial_send_to_ser(self):
    def serial_usb_send(self,send_data, receive_data, return_time=None, baudrate=115200, wait_time=3, repeat=2, is_error=False,ser_ip=1):
        self.usb_is_error = is_error
        self.usb_send_data = send_data
        self.usb_receive_data = receive_data
        self.usb_return_time = return_time
        self.usb_baudrate = baudrate
        self.usb_wait_time = int(wait_time)
        self.usb_repeat = int(repeat)
        self.usb_ser = ser_ip
        #print(self.usb_wait_time)
        usb_ser_value = self.serial_send(self.usb_send_data,self.usb_receive_data,baudrate=self.usb_baudrate,
                                         wait_time=self.usb_wait_time,repeat=self.usb_repeat,ser_ip=self.usb_ser)        
        #value = self.serial_send(send_data, receive_data, return_time=None, baudrate=115200, wait_time=3, repeat=2, is_error=False,ser_ip=1)
        #print()
        #print(ser_ip)
        return (usb_ser_value)        
    
        
        
    def _log_serial_info(self):
        '''
        - 打印发送以及接收的数据
        '''
        logger_msg = '发送串口数据: ' + self.send_data + '\n' + '应该收到串口数据: ' + self.receive_data
        print(logger_msg)
        self._get_send_data()

    def _get_cn_log(self, msg):
        '''
        - 转换编码
        '''
        return unicode(msg, encoding='utf-8')

    def _get_send_data(self):
        '''
        - 组成发送到串口服务器的数据包
        '''
        self.send_data = '(\'{0}\',\'{1}\',{2},{3})'.format(self.send_data, self.receive_data, self.baudrate, self.wait_time)

    def _send_to_serial_platform(self,ser_ip):
        '''
        - 发送数据到串口服务器, 控制重发次数
        '''
        for i in range(self.repeat):
            self._creatsock(ser_ip)
            self.split_msg_item = split_msg(self.receive_data)
            self._wait_data_from_ter()
            if self.send_res:
                if self.return_time:
                    return self._get_ter_time()
                else:
                    if self.rsp_data.find('IOT') != -1 and self.rsp_data[-3] == ';':
                        return self.rsp_data[self.rsp_data.find('=')+1:-3]
                    else:
                        return self.rsp_data[:-1]
            elif i < (self.repeat - 1):
                print('num {0}, time: {1}'.format(i, self._get_local_time()))
            elif i == (self.repeat - 1) and not self.is_error:
                self.sock.close()
                asserts.fail('接收到错误的串口数据: ' + self.rsp_data)
            self.sock.close()
            time.sleep(3)
            
    def _get_local_time(self):
        '''
        - 获取当前的时间
        '''
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int(time.time())))
            
    def _creatsock(self,ser_ip):
        '''
        - 创建socket套接字
        '''
        try:          
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #print(self.ser_ip)
            self.sock.connect(ser_ip)
            #print(self.ser_ip)
            self.sock.send(self.send_data.encode())
        except:
            print('send serial data failed')
    
    def _wait_data_from_ter(self):
        '''
        - 等待串口服务器应答
        '''
        while True:
            self.rsp_data = self.sock.recv(1024).decode()
            if self.rsp_data:
                rsp_res = True
                for item in self.split_msg_item:
                    try:
                        location = self.rsp_data.upper().find(item.upper())
                    except:
                        location = self.rsp_data.upper().decode().find(item.upper().encode())
                    if location == -1:
                        rsp_res = False
                        break
                if rsp_res:
                    if self.receive_data == 'FF':
                        print('更改波特率: ',self.baudrate)
                    else:
                        print('实际接收到的数据: ',self.rsp_data)
                    self.send_res = True
                break
                
    def _get_ter_time(self):
        '''
        解析返回终端的系统时间数据,如年月日时分秒2019010203040506.
        '''
        ret_data = str(datetime.datetime.now().year)
        location = self.rsp_data.find(ret_data) + 4
        time_data = self.rsp_data[location:]
        for i in range(len(time_data)):
            if len(ret_data) == 14:
                break
            if time_data[i].isdigit():
                ret_data = ret_data + time_data[i]
        return ret_data        

    def serial_confirm_ter_restart(self, wait_time,baudrate=115200):
        '''
        功能:
        - 确认终端是否重启
        - 通过条件 : 接收到终端串口应答的时间
        
        参数:
        - wait_time : 超时时间
        '''
        wait_time = int(wait_time)
        send_data = '(\'IOT+L1+nw.e01.r01.ic=?\',\'IOT+L1+nw.e01.r01.ic\',{0},1)'.format(baudrate)
        s_time = 0
        flag = False
        for i in range(int(wait_time/2)):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(IP_SERIAL_USB0)
            sock.send(send_data.encode())
            self.rsp_data = sock.recv(1024).decode()
            if self.rsp_data.find('IOT+L1+NW.E01.R01.IC=') != -1:
                flag = True
                break
            time.sleep(0.1)
            sock.close()
        if flag:
            print('terminal is working')
            print(self.rsp_data)
        else:
            asserts.fail('restart failed')      
        sock.close()
        ret_time = self._get_ter_time()
        return ret_time
    
    def serial_ama0_recv(self):
        ser = serial.Serial("/dev/USB2",baudrate=115200,timeout=5)

        while 1:
            s = ser.readline()
            count = 0
            try:
                s = s.decode('utf-8','ignore')
            except:
                print('a error in recv msg')
            if s!='':
                print(s)
                with open('/home/pi/ser2.txt','a') as f:
                    f.write(s)
                    #if count > 5:
                        #return '0'
                
    def start_ama0_recv(self):
        P = Process(target=self.serial_ama0_recv)
        P.daemon = True
        P.start()
        
    def serial_ama0_send(self,data,b=115200):
        ser = serial.Serial("/dev/USB2",baudrate=b,timeout=5)
        ser.write(data.encode())
        
    def start_ama0_send(self):
        P = Process(target=self.serial_ama0_send)
        P.daemon = True
        P.start()
        
    def serial_ttl_recv(self,usb="/dev/USB1"):
        ser = serial.Serial(usb,baudrate=115200,timeout=5)

        while 1:
            s = ser.readline()
            count = 0
            try:
                s = s.decode('utf-8','ignore')
            except:
                print('a error in recv msg')
            if s!='':
                print(s)
                with open('/home/pi/ttl.txt','a') as f:
                    f.write(s)
    
    def start_serial_ttl(self):
        P = Process(target=self.serial_ttl_recv)
        P.daemon = True
        P.start()
        
    def new_ser2_test(self):
        t_serial = threading.Thread(target=self.serial_ama0_recv)
        t_serial.setDaemon(True)
        t_serial.start()
        for i in range(5):
            self.serial_ama0_send('IOT+S1+NATIVE=?'+'\n\r')
            time.sleep(1)
            #os.system('sudo chmod 777 /home/pi/ser2.txt')
            try:
                with open('/home/pi/ser2.txt','r') as f:
                   z = f.read()
                #print(z+'1111')
                if z != '':
                    with open('/home/pi/production/log/mid.txt','a') as f:
                        f.write('<%s>'%('TS04_串口2')+'\n')
                        f.write('(%s)' % (str(z))+'\n')
                    os.system('sudo rm -rf /home/pi/ser2.txt')
                    print(0)
                    return 0
            except Exception as e:
                print(e)
                continue
        print(-1)
        return -1
    
    def new_ttl_test(self):
        t_serial = threading.Thread(target=self.serial_ttl_recv)
        t_serial.setDaemon(True)
        t_serial.start()
        for i in range(5):
            self.serial_ttl_send('IOT+S1+NATIVE=?'+'\n\r')
            time.sleep(1)
            #os.system('sudo chmod 777 /home/pi/ser2.txt')
            try:
                with open('/home/pi/ttl.txt','r') as f:
                   z = f.read()
                if z != '':
                    with open('/home/pi/production/log/mid.txt','a') as f:
                        f.write('<%s>'%('TS03_TTL')+'\n')
                        f.write('(%s)' % (str(z))+'\n')
                    os.system('sudo rm -rf /home/pi/ttl.txt')
                    print(0)
                    return 0
            except Exception as e:
                print(e)
                continue
        print(-1)
        return -1
        
    def serial_ttl_send(self,data,usb="/dev/USB1"):
        #sleep(3)
        ser = serial.Serial(usb,baudrate=115200,timeout=5)
        ser.write(data.encode())
        
    def abox_ping_test(self):
        self.serial_send('IOT-V1+bg.p.lev3.sw=1','IOT')
        con = False
        ser = serial.Serial("/dev/USB2",baudrate=115200,timeout=5)
        get_time_one = time.time()
        while 1:
            s = ser.readline()
            #time.sleep(1)
            try:
                s = s.decode('utf-8','ignore')
            except:
                print('a error in recv msg')
            with open('/home/pi/abox_ping.txt','a') as f:
                f.write(s)
            j = s.find('192.168.100.1 is connect')
            get_time_two = time.time()
            tt = get_time_two-get_time_one
            if j!=-1 or tt>120:
                con = True
                break
        if con==True and tt<=120:
            print('0')
            return 0
        else:
            print('-1')
            return -1
        
if __name__ == '__main__':
    a = SerialLibrary()
    a.new_ttl_test()
