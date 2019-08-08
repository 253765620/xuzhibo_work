import sys
sys.path.append("/home/pi/hlrfw")
sys.path.append("/home/pi/hlrfw/server/JTT808")
import asyncore
import socket
import signal
import Queue
import threading
import time

from core.dispatch import Dispatch
from visual.visual_decorator import info
from process_signal.payload import hello
from configs.ip_config import IP_SERVER_JTT808,PORT_JTT808,IP

#global parameter
mysock = []
mysock_flag = True
#f = open('/home/pi/Desktop/TTT/err_data_jtt808.txt', 'a')

#server thread
def server_to_ter_msg(q): 
    global mysock
    mysock2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    mysock2.bind(IP_SERVER_JTT808)
    mysock2.listen(5)
    while 1:
        try:
            connection, address = mysock2.accept()
            if connection:
                while 1:
                    mydata = connection.recv(1024)
                    if not mydata:
                        continue
                    print 'send to ter ',mydata
                    mysock.send(mydata.decode('hex'))
                    connection.close()
        except Exception, e:
            print e
        time.sleep(0.1)


class Adapt:
    """
    Just for make it's adapt suck_block_mode.py & conn.sendall()
    """

    def __init__(self, send_desc):
        self.sendall = send_desc  # For Adapt socket sendall() method


class EchoHandler(asyncore.dispatcher_with_send):
    data_len = 0
    def handle_read(self):
        data = self.recv(8192)
        self.data_len = len(data)
        if data:       
            try:
                conn = Adapt(self.send)  # Now your conn have method sendall()
                data_judge = data
                Dispatch(data, conn)
            except Exception, e:
                #global f
                #f.write('jtt808:'+str(time.time())+'\n'+str(e))
                print e

class EchoServer(asyncore.dispatcher):
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
        pair = self.accept()
        if pair is not None:
            sock, addr= pair
            info_tips = 'Incoming connection from ' + repr(addr)

            #server send msg to terminal
            global mysock
            global mysock_flag
            
            mysock = sock
            if mysock_flag:
                q = Queue.Queue()
                t = threading.Thread(target=server_to_ter_msg, args=(q,))
                t.result_queue = q
                t.setDaemon(True)
                t.start()
            else:
                pass
            mysock_flag = False
            
            info(info_tips)
            handler = EchoHandler(sock)
            self.current = handler.data_len
            self.total_recv += self.current
            self.counter += 1

if __name__ == '__main__':
    server = EchoServer(IP, PORT_JTT808)
    signal.signal(signal.SIGTSTP, hello)
    asyncore.loop()
