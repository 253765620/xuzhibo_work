#!coding: utf-8
'''
IP地址配置
指定各个平台使用的IP和端口
'''
import os

def get_local_ip():
    ip = os.popen("/sbin/ifconfig eth0 | grep inet | grep -v 127.0.0.1 | grep -v inet6 | awk '{print $2}' | tr -d 'addr:'").read()
    location = ip.rfind('.')
    try:
        ip = int(ip[location+1:])
    except:
        ip = 999
    return ip

#获取本地ip，如果返回的ip是999，代表ip无效
myip = get_local_ip()
DEVIATION = myip * 100

#组成实际的ip字符串
IP = '192.168.3.'+str(myip)

IP_SERIAL_USB0     = ('127.0.0.1', 2560) # 串口的端口
IP_SERIAL_USB1     = ('127.0.0.1', 2569)
IP_SERIAL_USB2     = ('127.0.0.1', 2570)
IP_SERIAL_USB3     = ('127.0.0.1', 2571)
IP_SERIAL_AMA0     = ('127.0.0.1', 2568)

IP_CAN             = (IP, 2561)          # 弃用，本来打算用做CAN端口
IP_SERVER_32960    = (IP, 2562)          # 国标端口
IP_SERVER_SIRUN    = (IP, 2563)          # 思润端口
IP_SERVER_SHARENGO = (IP, 2564)          # 小灵狗端口
IP_SERVER_JTT808   = (IP, 2565)          # 部标端口
IP_SERVER_ZDGBT2   = (IP, 2566)          # 知豆2端口
IP_SERVER_ZDMON    = (IP, 2567)          # 知豆端口

# 通上面的端口配置，区别是上面的配置是用作远程控制下发指令的端口，下面的是对外开放，给终端连接的端口
PORT_32960    = 0 + DEVIATION
PORT_JTT808   = 1 + DEVIATION
PORT_SIRUN    = 2 + DEVIATION
PORT_ZDMON    = 3 + DEVIATION
PORT_SHARENGO = 4 + DEVIATION
PORT_ZDGBT2   = 5 + DEVIATION

### server port dict
PORT_DICT = {
    'gbtele'   : PORT_32960,
    'jtt808'   : PORT_JTT808,
    'sirun'    : PORT_SIRUN,
    'zdmon'    : PORT_ZDMON,
    'sharengo' : PORT_SHARENGO,
    'zdgbt2'   : PORT_ZDGBT2,
    }

###获取IP
SERVER_TO_TER_IP = {
    'gbtele'   : IP_SERVER_32960,
    'jtt808'   : IP_SERVER_JTT808,
    'sirun'    : IP_SERVER_SIRUN,
    'zdmon'    : IP_SERVER_ZDMON,
    'sharengo' : IP_SERVER_SHARENGO,
    'zdgbt2'   : IP_SERVER_ZDGBT2,
    }
