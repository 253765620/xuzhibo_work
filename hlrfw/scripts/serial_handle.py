#!coding: utf-8
'''
功能:
- 串口控制平台就是控制串口数据的收发校验
- 代码结构有点乱, 建议重构
'''
import sys
if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')

import socket
import time
import serial
import threading
from hlrfw.configs.ip_config import IP_SERIAL_USB0,IP_SERIAL_AMA0,IP_SERIAL_USB1,IP_SERIAL_USB2,IP_SERIAL_USB3
from hlrfw.configs.sys_config import SERIAL_LOG_USB0, SERIAL_EQUIP,SERIAL_LOG_AMA0,SERIAL_LOG_USB1,SERIAL_LOG_USB2,SERIAL_LOG_USB3

#global parameter,应该发送的数据与收到的数据(收到的数据不代表正确的数据)
SERIAL_SEND_DATA = ''
SERIAL_REC_DATA  = ''
SERIAL_REC_DATA_SHOULD_BE = ''
MYBAUDRATE = 115200
STOP_SIGN = True

def recv_serial_msg(ser, f):
    # 接收串口数据
    s = ser.readline()
    try:
        s = s.decode('utf-8','ignore')
    except:
        print('a error in recv msg')
    if s != '':
        print(s[:-1])
        f.write(s)
        #print(f)
        if s.find('(bsp)can recv callback')!=-1:
            with open('/home/pi/can_testlog.txt','w') as ff:
                ff.write(s)
        if s.find('good')!=-1:
            with open('/home/pi/ser2_send.txt','w') as ff:
                ff.write(s)
        if s.find('nice')!=-1:
            with open('/home/pi/ttl_send.txt','w') as ff:
                ff.write(s)
    return s

def wait_for_data(ser, f):
    # 监控回复数据
    global STOP_SIGN, SERIAL_REC_DATA_SHOULD_BE, SERIAL_REC_DATA
    while STOP_SIGN:
        s = recv_serial_msg(ser, f)
        if s != '':
            location = s.upper().find(SERIAL_REC_DATA_SHOULD_BE.upper())
            if location != -1:
                SERIAL_REC_DATA = s[location:]
                break

def serial_data(q,SERIAL_CHICE):
    global SERIAL_SEND_DATA, SERIAL_REC_DATA, MYBAUDRATE, SERIAL_REC_DATA_SHOULD_BE, STOP_SIGN
    cur_baudrate = MYBAUDRATE
    ser = serial.Serial(SERIAL_CHICE,baudrate=cur_baudrate,timeout=0.1)
    if SERIAL_CHICE == SERIAL_EQUIP:
        f = open(SERIAL_LOG_USB0, 'a')
    elif SERIAL_CHICE == '/dev/USB1':
        f = open(SERIAL_LOG_USB1, 'a')
    elif SERIAL_CHICE == '/dev/USB2':
        f = open(SERIAL_LOG_USB2, 'a')
    elif SERIAL_CHICE == '/dev/USB3':
        f = open(SERIAL_LOG_USB3, 'a')
    else:
        f = open(SERIAL_LOG_AMA0, 'a')
    ser.flush()
    
    while 1:
        s = recv_serial_msg(ser, f)
        #如果收到应该发送的串口数据，发送串口数据，并且监控回复数据
        if SERIAL_SEND_DATA:
            err_time = time.strftime("%Y%m%d %H:%M:%S")
            if cur_baudrate != MYBAUDRATE:                                            # 判断指定的串口波特率和当前波特率是否相同，不相同就更改波特率
                cur_baudrate = MYBAUDRATE
                ser = serial.Serial(SERIAL_CHICE, baudrate=cur_baudrate, timeout=0.1)
                
            if len(SERIAL_REC_DATA_SHOULD_BE) > 7:                                    # 应该接收的数据类型为IOT+, 而且长度超过7个字符, 就截取前七个字符去校验接收到的串口数据
                if SERIAL_REC_DATA_SHOULD_BE.find('IOT+') != -1:
                    SERIAL_REC_DATA_SHOULD_BE = SERIAL_REC_DATA_SHOULD_BE[:7]
                    
            if SERIAL_SEND_DATA != 'FF':                                              # 如果发送的数据是'FF', 代表不发送数据, 只修改波特率
                ser.write(SERIAL_SEND_DATA.encode()+'\r\n'.encode())                  # 发送串口数据. 需要encode
                f.write(SERIAL_SEND_DATA+' '+err_time+'\n')                           # 写入发送的串口数据，以及发送的时间
                SERIAL_SEND_DATA = ''
                if SERIAL_REC_DATA_SHOULD_BE == 'FF':
                    SERIAL_REC_DATA = 'FF'
                    SERIAL_SEND_DATA = ''
                    continue
                wait_for_data(ser, f)
            else:
                f.write('FF\n')
                if SERIAL_REC_DATA_SHOULD_BE == 'FF':
                    SERIAL_REC_DATA = 'FF'
                    SERIAL_SEND_DATA = ''
                    continue
                wait_for_data(ser, f)
                
            f.flush()         # 每次收到robot的发送串口数据请求，就会把缓冲区的内容，写入到串口日志文件中
        STOP_SIGN = True      # 停止等待串口数据的
        time.sleep(0)         # 等待 0 秒，主要是为了防止线程资源不释放
        
def serial_server_start(q):
    global SERIAL_SEND_DATA, SERIAL_REC_DATA, MYBAUDRATE, SERIAL_REC_DATA_SHOULD_BE, STOP_SIGN
    while 1:
        mydata = connection.recv(1024)    # 这么connection就是__main__函数中的
        if not mydata:
            continue
        SERIAL_SEND_DATA, SERIAL_REC_DATA_SHOULD_BE, baudrate, my_wait_time = eval(mydata) # 解析从socket收到的串口数据, 分别为，发送串口数据，接收串口数据，波特率，超时时间
        print(SERIAL_SEND_DATA,baudrate)
        baudrate = int(baudrate)
        if MYBAUDRATE != baudrate:
            MYBAUDRATE = baudrate
        #返回给客户端数据
        timer = 0
        SERIAL_REC_DATA = ''
        my_wait_time = int(my_wait_time)
        while SERIAL_REC_DATA == '':
            timer = timer + 0.2
            time.sleep(0.2)
            if timer > my_wait_time:       # 超时了就初始化参数，返回timeout
                STOP_SIGN = False
                SERIAL_REC_DATA = 'timeout'
                time.sleep(1)
                break
        connection.sendall(SERIAL_REC_DATA.encode())
        break
    

if __name__ == '__main__':
    try:
        #开启serial线程
        len_argv = len(sys.argv)
        if len_argv == 2:
            SERIAL_CHICE = sys.argv[1]
        else:
            SERIAL_CHICE = SERIAL_EQUIP
        print(SERIAL_CHICE)
        t_serial = threading.Thread(target=serial_data, args=(1,SERIAL_CHICE))
        t_serial.setDaemon(True)
        t_serial.start()

        #建立socket套接字
        if SERIAL_CHICE == SERIAL_EQUIP:
            IP_SERIAL_CHICE = IP_SERIAL_USB0
        elif SERIAL_CHICE == '/dev/USB1':
            IP_SERIAL_CHICE = IP_SERIAL_USB1
        elif SERIAL_CHICE == '/dev/USB2':
            IP_SERIAL_CHICE = IP_SERIAL_USB2
        elif SERIAL_CHICE == '/dev/USB3':
            IP_SERIAL_CHICE = IP_SERIAL_USB3
        else:
            IP_SERIAL_CHICE = IP_SERIAL_AMA0 
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.bind(IP_SERIAL_CHICE)
        sock.listen(5)

        #开启socket监听
        while 1:
            try:
                connection, address = sock.accept()
                #print(address)
                if connection:
                    t_sock = threading.Thread(target=serial_server_start, args=(1,))
                    t_sock.setDaemon(True)
                    t_sock.start()
                    t_sock.join()
            except:
                connection.close()
            time.sleep(0.1)
    except:
        connection.close()
        sock.shutdown()
        sock.close()
