#!coding:utf-8
'''
- 用于can数据播放, 控制持续播放指定的can数据（注意, 不用做验证数据应答）
- 类似于串口平台的控制模式
- 测试用例通过socket给这个平台发送数据，控制can播放器的播放
'''
import sys
if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')

import can
import socket
import inspect
import ctypes
import threading

from time import sleep
from hlrfw.configs.ip_config import IP_CAN

def _async_raise(tid, exctype):
    """
    功能: 
    - 关闭子线程
    
    - tid: 子线程id
    - exctype: 退出线程方法
    """
    try:
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")
    except Exception as e:
        print(e)

def _convert_can_send_data(can_data):
    '''
    can data转码
    '''
    ret_list = []
    for item in can_data.split(' '):
        ret_list.append(int(str(item),16))
    while len(ret_list) < 8:
        ret_list.append(0)
    return ret_list

def reload_param(can_id):
    '''
    - 重新加载CAN对象、数据的参数
    '''
    global CAN_DATA_DICT
    can_bus = can.interface.Bus(channel=CAN_DATA_DICT[can_id][2], bustype='socketcan')
    can_msg = can.Message(
            arbitration_id = int(can_id, 16),
            data = _convert_can_send_data(CAN_DATA_DICT[can_id][1]), 
            extended_id = False)
    t_min = float(CAN_DATA_DICT[can_id][3])/1000
    return can_bus, can_msg, t_min
    
def can_player_start(can_id, connection):
    '''
    - 持续播放CAN数据
    '''
    global CAN_DATA_DICT

    while 1:
        if CAN_DATA_DICT[can_id][4]:
            can_bus, can_msg, t_min = reload_param(can_id)
            CAN_DATA_DICT[can_id][4] = False
        can_bus.send(can_msg)
        sleep(t_min)
        

if __name__ == '__main__':
    #global param
    CAN_DATA_DICT = {}
    
    try:
        #建立socket套接字
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.bind(IP_CAN)
        sock.listen(5)

        #开启socket监听
        while 1:
            try:
                connection, address = sock.accept()
                if connection:
                    mydata = connection.recv(1024)
                    if not mydata:
                        continue
                    try:
                        action, can_id, can_data, channel, interval = eval(mydata)
                    except:
                        connection.close()
                        break
                    #判断动作
                    if action == 'add':
                        if can_id not in CAN_DATA_DICT:
                            t_can = threading.Thread(target=can_player_start, args=(can_id, connection))
                            t_can.setDaemon(True)
                            CAN_DATA_DICT[can_id] = [t_can, can_data, channel, interval, True]
                            t_can.start()
                        else:
                            CAN_DATA_DICT[can_id] = [CAN_DATA_DICT[can_id][0], can_data, channel, interval, True]
                    elif action == 'delete':
                        if can_id in CAN_DATA_DICT:
                            #关闭can id对应的子线程
                            _async_raise(CAN_DATA_DICT[can_id][0].ident, SystemExit)
                            CAN_DATA_DICT.pop(can_id)
                    elif action == 'delete all':
                        # 关闭所有CAN播放
                        for _can_id in CAN_DATA_DICT:
                            _async_raise(CAN_DATA_DICT[_can_id][0].ident, SystemExit)
                        CAN_DATA_DICT = {}
                    connection.close()
            except:
                connection.close()
            sleep(0.1)
    except:
        connection.close()
        sock.shutdown()
        sock.close()
