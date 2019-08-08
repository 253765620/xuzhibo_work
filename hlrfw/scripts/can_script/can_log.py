#!coding:utf-8
'''
- 记录收到的CAN数据, 一般在测试的时候使用
'''
import can
import time
import sys
sys.path.append('/home/pi')
from hlrfw.configs.ip_config import myip

bus = can.interface.Bus(channel='can1',
                      bustype='socketcan')
f = open('/home/pi/Desktop/TTT/can_log{}'.format(myip), 'a')

a = time.time()
b = time.localtime(a)
c = time.strftime('%Y%m%d%H%M%S',b)

while 1:
    rec = str(bus.recv(1))
    if rec != 'None':
        f.write(rec + c + '\n')
    time.sleep(0)
    
