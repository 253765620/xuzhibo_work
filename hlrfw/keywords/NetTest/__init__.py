# -*- coding: utf-8 -*-
import sys
if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')
    
import time
import os
import hashlib
import psutil
import re

from robot.api import logger
from robot.utils import asserts
from hlrfw.keywords.SerialLibrary.__init__ import SerialLibrary
from hlrfw.keywords.EXP.__init__ import *
from hlrfw.keywords.Txtrwx.__init__ import *


from socket import *
from ftplib import FTP

try:
    from robot.api import logger
except:
    print('import robot failed')


def decorator(func):
    def wrapper(*args, **kwargs):
        '''
        装饰器：计算方法之间的某网卡流量差
        '''
        key_info = psutil.net_io_counters(pernic=True).keys()  # 获取网卡名称
        recv_1 = {}
        recv_2 = {}
        for key in key_info:
            recv_1.setdefault(key,psutil.net_io_counters(pernic=True).get(key).bytes_recv)
        recv1 = recv_1['usb0']
        print(recv1)
        func(*args, **kwargs)
        print(args[1])
        for key in key_info:
            recv_2.setdefault(key,psutil.net_io_counters(pernic=True).get(key).bytes_recv)
        recv2 = recv_2['usb0']
        print(recv2)
        print(recv2-recv1)
        return(recv2-recv1)
    
    return wrapper


class NetTest(object):
    def get_usbecm_ip(self,devname):
        '''
        - 获取某个网卡的ip
        - devname 设备名
        - retutn 
        '''
        a = os.popen('ifconfig').read()
        list_1 = a.split(devname)
        try:
            b = list_1[1].find('inet')
            c = list_1[1].find('netmask')
        except IndexError:
            print('找不到usb0设备')
            return -1
        if b != -1 or c != -1:
            return (list_1[1][b+5:c])
        else:
            return 0
    
    def tcp_test(self, data, should_data,ip='192.168.100.1',port=20000):
        '''
        - data:发送的数据
        - should_data应收到的数据
        - 成功返回right 失败返回wrong
        '''
        os.system('sudo route del -net '+ip+' netmask 255.255.255.255 dev eth0')
        os.system('sudo route add -net '+ip+' netmask 255.255.255.255 dev usb0')
        i = 1
        k = self.get_usbecm_ip('usb0')
        if isinstance(k, int):
            return -1
        a = k.split('.')
        print(a)
        a[3] = '1'
        judge = 'right'
        host = '.'.join(a)
        addr = (host, port)
        tctimeClient = socket(AF_INET, SOCK_STREAM)
        try:
            tctimeClient.connect(addr)
        except ConnectionRefusedError:
            print('TCP连接失败')
            return -1
        while (i < 6):
            i += 1
            tctimeClient.send(data.encode())
            data_ = tctimeClient.recv(1024).decode()
            print(data_)
            if should_data not in data_:
                judge = 'wrong'
                break
        tctimeClient.close()
        return judge
    
    def ping_test(self):
        '''
        - ping
        '''
        os.system('sudo route add -net 14.215.177.39 netmask 255.255.255.255 dev usb0')
        for i in range(3):
            key_info = psutil.net_io_counters(pernic=True).keys()  # 获取网卡名称
            recv_1 = {}
            for key in key_info:
                recv_1.setdefault(key,psutil.net_io_counters(pernic=True).get(key).bytes_recv)
            recv1 = recv_1['usb0']
            m = os.popen('ping -c 5 14.215.177.39').read()
            n = m.find('ttl')
            #k = self.ping.ping('www.baidu.com')
            key_info = psutil.net_io_counters(pernic=True).keys()
            recv_2 = {}
            for key in key_info:
                recv_2.setdefault(key,psutil.net_io_counters(pernic=True).get(key).bytes_recv)
            recv2 = recv_2['usb0']
            res = recv2-recv1
            if res>80 and n!=-1:
                return 1
            else:
                print('ping第{}次失败'.format(i+1))
        return -1
        #if (res) > 0:
            #if k==-1:
                #k = self.ping.ping('www.baidu.com')
                #return k
            #else:
                #return k
        
    def ethernet_test_list(self,ping):
        '''
        - 以太网测试用例，成功返回1失败返回-1
        '''
        #os.system('sudo route del -net 192.168.100.1 netmask 255.255.255.255 dev usb0')
        #os.system('sudo route add -net 192.168.100.1 netmask 255.255.255.255 dev eth0')
        for i in range(3):
            key_info = psutil.net_io_counters(pernic=True).keys()  # 获取网卡名称
            recv_1 = {}
            for key in key_info:
                recv_1.setdefault(key,psutil.net_io_counters(pernic=True).get(key).bytes_recv)
            recv1 = recv_1['eth0']
            m = os.popen(ping).read()
            n = m.find('ttl')
            #k = self.ping.ping('www.baidu.com')
            key_info = psutil.net_io_counters(pernic=True).keys()
            recv_2 = {}
            for key in key_info:
                recv_2.setdefault(key,psutil.net_io_counters(pernic=True).get(key).bytes_recv)
            recv2 = recv_2['eth0']
            res = recv2 - recv1
            if res>80 and n!=-1:
                return 1
            else:
                print('ping第{}次失败'.format(i+1))
        return -1
    
    def ethernet_test_1(self):
        os.system('sudo route del -net 192.168.100.1 netmask 255.255.255.255 dev usb0')
        os.system('sudo route add -net 192.168.100.1 netmask 255.255.255.255 dev eth0')
        return self.ethernet_test_list('ping -c 5 192.168.100.1')
            
    def ethernet_test_2(self):
        os.system('sudo route del -net 14.215.177.39 netmask 255.255.255.255 dev usb0')
        os.system('sudo route add -net 14.215.177.39 netmask 255.255.255.255 dev eth0')
        return self.ethernet_test_list('ping -c 5 14.215.177.39')
    
    def ethernet_test(self):
        a = self.ethernet_test_1()
        b = self.ethernet_test_2()
        if a==1 and b==1:
            return 1
        else:
            return -1
        
    def ftp_test(self):
        judge = 'right'
        key_info = psutil.net_io_counters(pernic=True).keys()  # 获取网卡名称
        recv_1 = {}
        for key in key_info:
            recv_1.setdefault(key,psutil.net_io_counters(pernic=True).get(key).bytes_recv)
        recv1 = recv_1['usb0']
        os.system('sudo route add -net 115.29.3.59 netmask 255.255.255.255 dev usb0')
        ftp = FTP(timeout=10)
        ftp.connect('115.29.3.59',2014)
        ftp.login('yinjian','yinjian')
        bufsize = 1024
        fp = open("/home/pi/123.txt", 'wb')
        ftp.retrbinary('RETR ' + '123.txt', fp.write, bufsize)
        ftp.set_debuglevel(0)
        fp.close()
        fmd5 = self._md5sum('/home/pi/123.txt')
        if fmd5 != ('859c5f520600848d0225170adc213e44'):
            judge = 'wrong'
            print('文件校验出错')
        os.system('rm -f /home/pi/123.txt')
        key_info = psutil.net_io_counters(pernic=True).keys()
        recv_2 = {}
        for key in key_info:
            recv_2.setdefault(key,psutil.net_io_counters(pernic=True).get(key).bytes_recv)
        recv2 = recv_2['usb0']
        res = recv2-recv1
        if res < 3000:
            judge = 'wrong'+str(res)
            print('网卡流量不对')
        return judge
    
    def _downloadfile(self,ftp,remotepath,filename):
        bufsize = 1024
        file_handle=open(filename,"wb").write
        ftp.retrbinary('RETR ' + remotepath, file_handle, bufsize)
        ftp.set_debuglevel(0)
        fp.close()
        
    def _md5sum(self,filename):
        '''
        - md5文件校验
        '''
        with open(filename) as f:
            fcont = f.read()
            m = hashlib.md5()
            m.update(fcont.encode("utf8"))
        return m.hexdigest()
    
    def ver_equ(self):
        judge = 'right'
        m = os.popen('ifconfig').read()
        n = m.find('usb0')
        if n == -1:
            print('未检测到设备')
            judge = 'wrong'
        return judge
    
    def suc_fail_rates(self):
        '''
        - 测试用例成功率打印
        '''
        f = open(r'NetTest.txt','r+')
        a = f.read()
        b = a.count('成功')
        c = a.count('失败')
        f.close()
        count=len(open(r"NetTest.txt",'r+').readlines())
        suc = b/(count)*100
        fail = c/(count)*100
        print('当前测试次数:{}次 ,成功次数:{}次 ,失败次数:{}次'.format(count,b,c))
        print('成功率:{:.2f}% , 失败率:{:.2f}%'.format(suc,fail))
        
    def Get_ICCID(self):
        '''
        - 获取ICCID
        '''
        os.system('sudo route del -net 192.168.100.1 netmask 255.255.255.255 dev eth0')
        data ='(CESHI)MODEM INFO'
        k = self.get_usbecm_ip('usb0')
        if isinstance(k, int):
            return -1
        a = k.split('.')
        a[3] = '1'
        judge = 'right'
        host = '.'.join(a)
        port = 20000
        print(host)
        addr = (host, port)
        tctimeClient = socket(AF_INET, SOCK_STREAM)
        try:
            tctimeClient.connect(addr)
        except ConnectionRefusedError:
            print('TCP连接失败')
        tctimeClient.send(data.encode())
        data_ = tctimeClient.recv(1024).decode()
        if data_ != None:
            res = self.Get_icc(data_,'ICCID')
            return res
        else:
            print('未收到数据')
        
    def Get_icc(self,str1,str2):
        list_1 = re.split(r'[,:;]',str1)
        list_2 = []
        if str2 in list_1:
            n =list_1.index(str2)
            m =list_1[n+1]
            return m
        else:
            return ('没有这项字符串')

    def Tcp_Send(senddata):
        address = '127.0.0.1'  # 服务器的ip地址
        port = 12345  # 服务器的端口号
        buffsize = 1024  # 接收数据的缓存大小
        s = socket(AF_INET, SOCK_STREAM)
        try:
            s.connect((address, port))
        except ConnectionRefusedError:
            print('TCP连接失败')
            return -1
        s.send(senddata.encode())
        recvdata = s.recv(buffsize).decode('utf-8')
        s.close()
        return recvdata

    def Handle_res(res):
        list_ = []
        res_ = bin(int(res))
        k = (12 - len(res_)) * '0'
        m = str(k) + str(res_[2:])
        for i in m:
            list_.append(i)
        if '0' not in list_[1:]:
            print('测试全部通过')
        else:
            if list_[1] == '0':
                print('Dsm测试失败')
            if list_[2] == '0':
                print('Adas测试失败')
            if list_[3] == '0':
                print('Gpio测试失败')
            if list_[4] == '0':
                print('Uart测试失败')
            if list_[5] == '0':
                print('Eth测试失败')
            if list_[6] == '0':
                print('Dvr测试失败')
            if list_[7] == '0':
                print('Emmc测试失败')
            if list_[8] == '0':
                print('Sdcard2测试失败')
            if list_[9] == '0':
                print('Sdcard1测试失败')

    def get_net_state(self, devname):
        '''
        - 返回网卡工作状态:
        - -1: 没有网卡
        - 0: 网卡准备就绪
        - 1: 网卡正常工作
        '''
        a = os.popen('ifconfig').read()
        list = a.split(devname)
        if len(list) == 1:
            return -1
        else:
            b = list[1].find('inet')
            c = list[1].find('netmask')
            if b == -1 or c ==-1:
                return 0
            else:
                return 1
    def ai_test(self):
        '''
        - aibox自检的测试用例
        '''
        try:
            S = SerialLibrary()
            U = Txtrwx()
            S.serial_send('IOT-V1+ai.lev.switch=0','IOT-V1+AI.LEV.SWITCH=successful;')
            #S.serial_send('IOT+S1+ai.m.tb.st.sw=0','IOT+S1+AI.M.TB.ST.SW=0;')
            #S.serial_send('(CESHI)DSMCORE FACTORY-LOCK','(CESHI)')
            #S.serial_send('(CESHI)DSMCORE FACTORY-P0000000000000110','(CESHI)')
            list_ = ['1']
            for j in range(6):
                if j == 5:
                    asserts.fail('启动自检测试失败')
                a = S.serial_send('IOT-V1+ai.self.check=1','IOT')
                b = a.find('suc')
                if b != -1:
                    break
            o = 0
            while(o<150):
                c = S.serial_send('IOT-C1+ai.sf.ck.r=?','IOT')
                time.sleep(1)
                o +=1
                list_ = re.split(r'[,;]',c)
                del list_[7:9]
                if '255' not in list_:
                    break
            if o==150:
                asserts.fail('接收数据超时')
            
            sd2 = list_[-2]
            del list_[-2]
            print(list_)
            if '1' not in list_:
                    print('测试全部通过')
            else:
                if list_[0] == '1':
                    print('Dsm测试失败')
                if list_[1] == '1':
                    print('Adas测试失败')
                if list_[2] == '1':
                    print('Gpio测试失败')
                if list_[3] == '1':
                    print('Uart测试失败')
                if list_[4] == '1':
                    print('Eth测试失败')
                if list_[5] == '1':
                    print('Dvr测试失败')
                if list_[6] == '1':
                    print('Emmc测试失败')
                #if list_[7] == '1':
                    #print('Sdcard2测试失败')
                if list_[7] == '1':
                    print('Sdcard1测试失败')
                    
            #S.serial_send('(CESHI)DSMCORE FACTORY-P0000000000000111','(CESHI)')
            #S.serial_send('(CESHI)DSMCORE FACTORY-UNLOCK','(CESHI)')
            #e = S.serial_send('IOT+V1+ai.ser.no.g=','IOT')
            #time.sleep(1)
            #f = S.serial_send('IOT+C1+ai.m.f2.sn=?','IOT')
            #if f ==None:
                #asserts.fail('未检测到AI_BOX序列号')
            #else:
                #with open('/home/pi/ProductionTool/ai_test_record.txt','a') as file:
                    #res = '|'.join(list_)
                    #file.write(str(f)+'|'+res+'\n')
                    #print('写入成功')
                
        finally:
            r = '|'.join(list_)
            S.serial_send('IOT-V1+ai.lev.switch=1','IOT-V1+AI.LEV.SWITCH=successful;')
            #S.serial_send('IOT+S1+ai.m.tb.st.sw=1','IOT+S1+AI.M.TB.ST.SW=1;')
            if '1' in list_:
                U.txtrwx_abox_file_write('AIBOX测试','Fail',r)
                asserts.fail('AI_BOX测试失败')
            else:
                U.txtrwx_abox_file_write('AIBOX测试','Pass',r)


if __name__  ==  "__main__":
    a = NetTest()
    b = a.ai_test()
    #print(b)
