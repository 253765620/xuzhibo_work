#!coding:utf-8
'''
- 平台接收终端链接入口
'''
import sys
sys.path.append("/home/pi/hlrfw")
sys.path.append("/home/pi/hlrfw/server/32960")
import asyncore
import socket
import signal
import Queue
import threading
import time

from core.dispatch import Dispatch
from visual.visual_decorator import info
from process_signal.payload import hello
from configs.ip_config import IP_SERVER_32960,PORT_32960,IP

#global parameter
mysock = []
mysock_flag = True
IS_NEED_RSP = True
IS_RECV_FLAG = True

#server thread
def server_to_ter_msg(q):
    '''
    - 控制平台发送数据给终端
    '''
    global mysock
    global IS_NEED_RSP
    global IS_RECV_FLAG
    mysock2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    mysock2.bind(IP_SERVER_32960)
    mysock2.listen(5)
    while 1:
        connection, address = mysock2.accept()
        if connection:
            while 1:
                mydata = connection.recv(1024).decode()
                if not mydata:
                    continue
                connection.close()
                if mydata == 'close connection':
                    for item in mysock:
                        try:
                            item.shutdown(2)
                        except:
                            print '32960 threading error'
                    mysock = []
                elif mydata == 'do not give rsp':
                    IS_NEED_RSP = False
                elif mydata == 'give rsp':
                    IS_NEED_RSP = True
                elif mydata == 'do not recv connection':
                    IS_RECV_FLAG = False
                elif mydata == 'recv connection':
                    IS_RECV_FLAG = True
                else:
                    active_sock = []
                    for item in mysock:
                        try:
                            item.sendall(mydata.decode('hex'))
                            active_sock.append(item)
                            print 'send data:{} '.format(mydata)
                        except:
                            print '32960 threading error'
                    mysock = active_sock
                break
        time.sleep(0.1)

class Adapt:
    """
    - Just for make it's adapt suck_block_mode.py & conn.sendall()
    - 增加了一个sendall方法
    """

    def __init__(self, send_desc):
        self.sendall = send_desc  # For Adapt socket sendall() method

class EchoHandler(asyncore.dispatcher_with_send):
    global IS_NEED_RSP
    data_len = 0
    def handle_read(self):
        data = self.recv(8192)           # 接收发送的数据
        self.data_len = len(data)        # 统计数据长度
        if data and IS_NEED_RSP:         # 判断现在是否允许发送数据
            try:
                conn = Adapt(self.send)  # Now your conn have method sendall()
                #data_judge = data
                Dispatch(data, conn)     # 开始解析接收到的数据
            except Exception,e:
                print e


class EchoServer(asyncore.dispatcher):
    '''
    - 开启socket, 等待链接
    '''
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self.total_recv = 0
        self.current = 0
        self.counter = 0

    def handle_accept(self):
        global IS_RECV_FLAG
        if IS_RECV_FLAG:
            pair = self.accept()     # 接受链接
            if pair is not None:
                sock, addr= pair
                info_tips = 'Incoming connection from ' + repr(addr)
                
                #server send msg to terminal
                global mysock
                global mysock_flag
                mysock.append(sock)   # 把链接加入到已有链接中
                if mysock_flag:       # 建立平台给终端发送数据的socket
                    q = Queue.Queue()
                    t = threading.Thread(target=server_to_ter_msg, args=(q,))
                    t.result_queue = q
                    t.setDaemon(True)
                    t.start()
                    mysock_flag = False
                    
                info(info_tips)
                handler = EchoHandler(sock)
                self.current = handler.data_len
                self.total_recv += self.current
                self.counter += 1

if __name__ == '__main__':
    server = EchoServer(IP, PORT_32960)   # 主程序
    signal.signal(signal.SIGTSTP, hello)  # 获取signal
    asyncore.loop()                       # 异步循环执行