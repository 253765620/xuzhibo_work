#!coding: utf-8
import sys
sys.path.append('/home/pi/hlrfw/')
import socket
import time
import can
import Queue
import threading
import os
import CAN
import codecs
from Config.Setting import Ip_can
from serial.tools import hexlify_codec
#####
STOP_SIGN = True
SEND_CAN_MSG = ''
SH_REC_CAN_ID = ''
SH_REC_CAN_DATA = ''
REC_CAN_ID = ''
REC_CAN_DATA = ''
CHANNEL = 'can0'

# add hexlify to codecs
def hexlify_decode_plus(data, errors='strict'):
    udata, length = hexlify_codec.hex_decode(data, errors)
    return (udata.rstrip(), length)

hexlify_codec_plus = codecs.CodecInfo(
    name='hexlify',
    encode=hexlify_codec.hex_encode,
    decode=hexlify_decode_plus
    )

codecs.register(lambda c: hexlify_codec_plus if c == 'hexlify' else None)

class can_platform(object):
    def _encode(self, ustring, encoding=None, encoding_mode='strict'):
        return ustring.encode(encoding or self._encoding, encoding_mode)
    
    def socket_build(self):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.bind(Ip_can)
        self.sock.listen(5)
        self.socket_mon()

    def can_build(self):
        q = Queue.Queue()
        self.can_t = threading.Thread(target=self.can_bus, args=(q,))
        self.can_t.result_queue = q
        self.can_t.setDaemon(True)
        self.can_t.start()
        
    def can_msg(self, q):
        global CHANNEL, STOP_SIGN, SH_REC_CAN_ID, SH_REC_CAN_DATA, SEND_CAN_MSG, REC_CAN_ID, REC_CAN_DATA
        
        STOP_SIGN = True
        i = 0
        while True:
            rec_data = self.connection.recv(1024)
            send_can_id, send_can_data, SH_REC_CAN_ID, SH_REC_CAN_DATA, CHANNEL, wait_time = eval(rec_data.decode('hex'))
            wait_time = int(wait_time)
            send_can_id = int(send_can_id,16)
            send_can_data = self._encode(send_can_data, 'hexlify')
            if send_can_id == 255:
                SEND_CAN_MSG = 'FF'
            else:
                SEND_CAN_MSG = can.Message(arbitration_id=send_can_id, data=send_can_data, extended_id=False)
            while REC_CAN_ID == '':
                i = i + 0.1
                time.sleep(0.1)
                if i > wait_time:
                    STOP_SIGN = False
                    REC_CAN_ID = 'timeout'
                    REC_CAN_DATA = ''
            ret_sock_data = REC_CAN_ID + ' ' + REC_CAN_DATA
            q.sendall(ret_sock_data.encode('hex'))
            REC_CAN_DATA = ''
            REC_CAN_ID = ''
            SEND_CAN_MSG = ''
            break

    def socket_mon(self):
        while 1:
            self.connection, address = self.sock.accept()
            if self.connection:
                q = Queue.Queue()
                t = threading.Thread(target=self.can_msg, args=(self.connection,))
                t.result_queue = q
                t.setDaemon(True)
                t.start()
                t.join()
            time.sleep(0.1)
        self.connection.close()

    def can_creat(self):
        global CHANNEL
        if self.now_channel != CHANNEL:
            self.now_channel = CHANNEL
            self.bus = can.interface.Bus(channel=self.now_channel, bustype='socketcan')

    def file_write(self, data):
        if data :
            self.file.write(str(data)+'\n')
            print data

    def change_can_data(self, data):
        ret_data = ''
        if isinstance(data, long):
            ret_data = hex(data)
        else:
            for item in data:
                item = hex(item)[2:] + ' '
                if len(item) == 2:
                    item = '0' + item
                ret_data = ret_data + item
        return ret_data

    def data_compare(self, rec_data):
        global SH_REC_CAN_ID, SH_REC_CAN_DATA, REC_CAN_ID, REC_CAN_DATA
        my_id = self.change_can_data(rec_data.arbitration_id)
        my_data = self.change_can_data(rec_data.data)
        location_1 = my_id.find(SH_REC_CAN_ID)
        location_2 = my_data.find(SH_REC_CAN_DATA)
        if location_1 != -1 and location_2 != -1:
            REC_CAN_ID = my_id
            REC_CAN_DATA = my_data
            return True
        else:
            return False
        
    def rec_can_data(self):
        '''
        属性：id_type, is_extended_id, is_remote_frame, timestamp,
             data, dlc, arbitration_id, is_error_frame
        '''
        ret_data = self.bus.recv(1)
        return ret_data

    def can_write_data(self, msg):
        self.bus.send(msg)

    def can_bus(self, q):
        global STOP_SIGN, SEND_CAN_MSG
        self.file = open('/home/pi/Desktop/TTT/can_data.txt', 'a')
        self.now_channel = 'can0'
        self.bus = can.interface.Bus(channel=self.now_channel, bustype='socketcan')
        while 1:
            self.can_creat()
            rec_data = self.rec_can_data()
            self.file_write(rec_data)
            if SEND_CAN_MSG:
                if SEND_CAN_MSG != 'FF':
                    self.can_write_data(SEND_CAN_MSG)
                SEND_CAN_MSG = ''
                while STOP_SIGN:
                    rec_data = self.rec_can_data()
                    if rec_data:
                        self.file_write(rec_data)
                        if self.data_compare(rec_data):
                            break
                    time.sleep(0)
        STOP_SIGN = True
#####
for i in range(2):
    try:
        os.system('sudo sh /usr/local/lib/python2.7/site-packages/hlrfw/script/can-start.sh')
    except:
        pass
a = can_platform()
a.can_build()
a.socket_build()
