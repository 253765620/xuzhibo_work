# -*- coding: utf-8 -*-
'''
- CAN关键字
- 封装了关于发送和接收CAN数据的关键字
- 也是因为CAN应答数据太快，所以在接收CAN数据的时候会新建一个线程去提前接收
'''
import sys
if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')
    
import os
import can
import time
import threading
    
from robot.api import logger
from robot.utils import asserts    

#global parameter 这些全局参数可以考虑放进类里，放在外面有点丑
SHOULD_RECV_CAN_OBJECT = []                                        # 接收到的数据数组
CAN_MONITOR_CTRL = True                                            # 退出接收线程的标志位
BUS_CAN1 = can.interface.Bus(channel='can1', bustype='socketcan')  # can1的实例对象
BUS_CAN2 = can.interface.Bus(channel='can0', bustype='socketcan')  # can2的实例对象
BUS_CAN = BUS_CAN1                                                 # 当前使用的can对象

class CAN(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def CAN_send_and_rec(self, send_id, send_data, recv_id, recv_data, is_false=False, NRC=None, timeout=20):
        '''
        功能:
        - 发送并接收CAN数据
        - 通过条件 : 接收到对应的can id和data
        
        参数:
        - send_id : 发送的ID
        - send_data : 发送的数据
        - recv_id : 接收的ID
        - recv_data : 接收的数据
        - is_false : 是否为否定响应(填写'True'为是否定响应)
        - NRC : 填写的是第三个字节的否定响应码,不填写就不判断
        - timeout : 超时时间(ms)
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | CAN_send_and_rec | 720 | 02 10 03 | 728 | 06 50 01 00 32 01 F4 | is_false=False | NRC=None | timeout=20 |
        '''
        send_id = self._convert_can_id(send_id)               # 把发送的can id转化为python-can接口函数要求的格式
        recv_id = self._convert_can_id(recv_id)               # 把发送的can id转化为python-can接口函数要求的格
        send_data = self._convert_can_send_data(send_data)    # 同理转数据
        recv_data = self._convert_can_recv_data(recv_data)    # 同理转数据
        
        msg = can.Message(
            arbitration_id = send_id,
            data = send_data, 
            extended_id = False)                              # 组成发送的can数据包, extended_id选择是否是标准帧
        
        self._can_send_and_wait_rsp(recv_id, msg)             # 发送CAN数据并且等待应答, 应答的数据会保存在全局变量SHOULD_RECV_CAN_OBJECT中
        
        if SHOULD_RECV_CAN_OBJECT:                            # 判断到底有没有收到应答数据, python-can其实是有filter 过滤功能的（就是选择收哪个id的can的数据，还没弄，弄了可以加快很多效率）
            for bus_recv_msg in SHOULD_RECV_CAN_OBJECT:
                print('should recv',hex(recv_id),self._bytes_to_hex(recv_data))
                print('infact recv',hex(bus_recv_msg.arbitration_id),self._bytes_to_hex(bus_recv_msg.data))
                if bus_recv_msg.arbitration_id == recv_id:
                    if is_false == 'True':
                        if bus_recv_msg.data[0] != 127:       # 判断第一个字节是不是7F, 是不是否定响应
                            asserts.fail('不是否定响应')
                        if NRC and bus_recv_msg.data[2] != int(NRC,16):
                            asserts.fail('不是期待的否定响应码:'+NRC)
                    elif bus_recv_msg.data != recv_data:
                        asserts.fail('CAN数据应答异常')
                    logger.info('CAN数据应答正常')
                    break
        else:
            asserts.fail('未接收到CAN数据')
            
    def CAN_send_and_rec_and_return(self, send_id, send_data, recv_id):
        '''
        功能:
        - 发送并接收CAN数据,并且返回CAN数据
        - 通过条件 : 接收到对应的can id的数据
        
        参数:
        - send_id : 发送的ID
        - send_data : 发送的数据
        - recv_id : 接收的ID
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | CAN_send_and_rec_and_return | 720 | 02 10 03 | 728 |
        '''
        send_id = self._convert_can_id(send_id)
        recv_id = self._convert_can_id(recv_id)
        send_data = self._convert_can_send_data(send_data)
        msg = can.Message(
            arbitration_id = send_id,
            data = send_data, 
            extended_id = False)
        self._can_send_and_wait_rsp(recv_id, msg)
        if SHOULD_RECV_CAN_OBJECT:
            for bus_recv_msg in SHOULD_RECV_CAN_OBJECT:
                return self._bytes_to_hex(bus_recv_msg.data)
        else:
            asserts.fail('未接收到CAN数据')
        
            
    def CAN_send_and_rec_nrc(self, send_id, send_data, recv_id, NRC, timeout=20):
        '''
        功能:
        - 发送并接收CAN数据,判断NRC
        - 通过条件 : 只要收到的否定响应码与指定的NRC相同
        
        参数:
        - send_id : 发送的ID
        - send_data : 发送的数据
        - recv_id : 接收的ID
        - NRC : 填写的是第三个字节的否定响应码
        - timeout : 超时时间(ms)
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | CAN_send_and_rec_nrc | 720 | 02 10 03 | 728 | 12 | timeout=20 |
        '''
        #global SHOULD_RECV_CAN_OBJECT
        send_id = self._convert_can_id(send_id)
        recv_id = self._convert_can_id(recv_id)
        send_data = self._convert_can_send_data(send_data)
        recv_data = self._convert_can_recv_data(recv_data)
        msg = can.Message(
            arbitration_id = send_id,
            data = send_data, 
            extended_id = False)
        self._can_send_and_wait_rsp(recv_id, msg)
        if SHOULD_RECV_CAN_OBJECT:
            for bus_recv_msg in SHOULD_RECV_CAN_OBJECT:
                print('expect nrc:', NRC)
                print('infact recv',hex(bus_recv_msg.arbitration_id),self._bytes_to_hex(bus_recv_msg.data))
                if bus_recv_msg.arbitration_id == recv_id:
                    if bus_recv_msg.data[1] != 127:
                        asserts.fail('不是否定响应')
                    if NRC and bus_recv_msg.data[3] != int(NRC,16):
                        asserts.fail('不是期待的否定响应码:'+NRC)
                    logger.info('CAN数据应答正常')
                    break
        else:
            asserts.fail('未接收到CAN数据')
            
    def CAN_send_and_rec_neg(self, send_id, send_data, recv_id, timeout=20):
        '''
        功能:
        - 发送并接收CAN数据,判断否定响应
        - 通过条件 : 只要收到否定响应就通过
        
        参数:
        - send_id : 发送的ID
        - send_data : 发送的数据
        - recv_id : 接收的ID
        - timeout : 超时时间(ms)
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | CAN_send_and_rec_neg | 720 | 02 10 03 | 728 | timeout=20 |
        '''
        #global SHOULD_RECV_CAN_OBJECT
        send_id = self._convert_can_id(send_id)
        recv_id = self._convert_can_id(recv_id)
        send_data = self._convert_can_send_data(send_data)
        #recv_data = self._convert_can_recv_data(recv_data)
        msg = can.Message(
            arbitration_id = send_id,
            data = send_data, 
            extended_id = False)
        self._can_send_and_wait_rsp(recv_id, msg)
        if SHOULD_RECV_CAN_OBJECT:
            for bus_recv_msg in SHOULD_RECV_CAN_OBJECT:
                print('expect negtive response')
                print('infact recv',hex(bus_recv_msg.arbitration_id),self._bytes_to_hex(bus_recv_msg.data))
                if bus_recv_msg.arbitration_id == recv_id:
                    if bus_recv_msg.data[1] == 127:
                        logger.info('收到否定响应,测试通过')
                    else:
                        asserts.fail('不是否定响应')
                    break
        else:
            asserts.fail('未接收到CAN数据')
            
    def CAN_send_and_rec_pos(self, send_id, send_data, recv_id, timeout=20):
        '''
        功能:
        - 发送并接收CAN数据, 判断肯定响应
        - 通过条件 : 收到期待的肯定响应的can id和data
        
        参数:
        - send_id : 发送的ID
        - send_data : 发送的数据
        - recv_id : 接收的ID
        - timeout : 超时时间(ms)
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | CAN_send_and_rec_pos | 720 | 02 10 03 | 728 | timeout=20 |
        '''
        #global SHOULD_RECV_CAN_OBJECT
        send_id = self._convert_can_id(send_id)
        recv_id = self._convert_can_id(recv_id)
        send_data = self._convert_can_send_data(send_data)
        #recv_data = self._convert_can_recv_data(recv_data)
        msg = can.Message(
            arbitration_id = send_id,
            data = send_data, 
            extended_id = False)
        self._can_send_and_wait_rsp(recv_id, msg)
        if SHOULD_RECV_CAN_OBJECT:
            for bus_recv_msg in SHOULD_RECV_CAN_OBJECT:
                print('expect positive response')
                print('infact recv',hex(bus_recv_msg.arbitration_id),self._bytes_to_hex(bus_recv_msg.data))
                if bus_recv_msg.arbitration_id == recv_id:
                    if bus_recv_msg.data[0] < 16:
                        if bus_recv_msg.data[1] == send_data[1]+64:
                            logger.info('收到肯定响应')
                        else:
                            asserts.fail('没有收到期待的肯定响应')
                    else:
                        if bus_recv_msg.data[2] == send_data[1]+64:
                            logger.info('recv continue')
                            logger.info('收到肯定响应')
                        else:
                            asserts.fail('没有收到期待的肯定响应')
                break
        else:
            asserts.fail('未接收到CAN数据')

    def CAN_send_and_rec_except(self, send_id, send_data, recv_id, recv_data):
        '''
        功能:
        - 发送并接收CAN数据
        - 通过条件 : 收到数据，并且收到的数据与指定的数据不同
        
        参数:
        - send_id : 发送的ID
        - send_data : 发送的数据
        - recv_id : 接收的ID
        - recv_data : 接收的数据
        - timeout : 超时时间(ms)
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | CAN_send_and_rec_except | 720 | 02 10 03 | 728 | 50 03 |
        '''
        send_id = self._convert_can_id(send_id)
        recv_id = self._convert_can_id(recv_id)
        send_data = self._convert_can_send_data(send_data)
        recv_data = self._convert_can_recv_data(recv_data)
        msg = can.Message(
            arbitration_id = send_id,
            data = send_data, 
            extended_id = False)
        self._can_send_and_wait_rsp(recv_id, msg)
        if SHOULD_RECV_CAN_OBJECT:
            for bus_recv_msg in SHOULD_RECV_CAN_OBJECT:
                print('except recv', hex(recv_id),self._bytes_to_hex(recv_data))
                print('infact recv', hex(bus_recv_msg.arbitration_id),self._bytes_to_hex(bus_recv_msg.data))
                if bus_recv_msg.arbitration_id == recv_id and bus_recv_msg.data == recv_data:
                    asserts.fail('收到了不想要的否定响应码')
                    break
        else:
            asserts.fail('没有收到CAN数据')
        
    def CAN_send_and_no_rsp(self, send_id, send_data, recv_id):
        '''
        功能:
        - 发送并接收CAN数据
        - 通过条件 : 没收到期待的can id的数据
        
        参数:
        - send_id : 发送的ID
        - send_data : 发送的数据
        - recv_id : 接收的ID
        - timeout : 超时时间(ms)
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | CAN_send_and_no_rsp | 720 | 02 10 03 | 728 |
        '''
        send_id = self._convert_can_id(send_id)
        recv_id = self._convert_can_id(recv_id)
        send_data = self._convert_can_send_data(send_data)
        msg = can.Message(
            arbitration_id = send_id,
            data = send_data, 
            extended_id = False)
        self._can_send_and_wait_rsp(recv_id, msg)
        if SHOULD_RECV_CAN_OBJECT:
            for bus_recv_msg in SHOULD_RECV_CAN_OBJECT:
                print('infact recv', hex(bus_recv_msg.arbitration_id),self._bytes_to_hex(bus_recv_msg.data))
                if bus_recv_msg.arbitration_id == recv_id:
                    asserts.fail('收到响应,测试失败')
                    break
        else:
            logger.info('没有收到响应,测试成功')
            
    def CAN_send_and_rec_rsp(self, send_id, send_data, recv_id):
        '''
        功能:
        - 发送并接收CAN数据
        - 通过条件 : 收到期待的can id的数据
        
        参数:
        - send_id : 发送的ID
        - send_data : 发送的数据
        - recv_id : 接收的ID
        - timeout : 超时时间(ms)
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | CAN_send_and_rec_rsp | 720 | 02 10 03 | 728 |
        '''
        send_id = self._convert_can_id(send_id)
        recv_id = self._convert_can_id(recv_id)
        send_data = self._convert_can_send_data(send_data)
        msg = can.Message(
            arbitration_id = send_id,
            data = send_data, 
            extended_id = False)
        self._can_send_and_wait_rsp(recv_id, msg)
        if SHOULD_RECV_CAN_OBJECT:
            for bus_recv_msg in SHOULD_RECV_CAN_OBJECT:
                print('infact recv', hex(bus_recv_msg.arbitration_id),self._bytes_to_hex(bus_recv_msg.data))
                if bus_recv_msg.arbitration_id == recv_id:
                    logger.info('收到响应,测试成功')
                    break
        else:
            asserts.fail('没有收到响应,测试失败')
            
    def CAN_data_send(self, send_id, send_data):
        '''
        功能:
        - 发送CAN数据
        - 通过条件 : 输入数据格式无误
        
        参数:
        - send_id : 发送的ID
        - send_data : 发送的数据
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | CAN_send_data | 720 | 02 10 03 |
        '''
        send_id = self._convert_can_id(send_id)
        send_data = self._convert_can_send_data(send_data)
        msg = can.Message(
            arbitration_id = send_id,
            data = send_data, 
            extended_id = False)
        BUS_CAN.send(msg)
        time.sleep(0.15)
        
    def CAN_data_wait(self, recv_id, recv_data, wait_time, recv_times=999):
        '''
        功能:
        - 等待接收CAN数据
        - 通过条件 : 在wait_time时间内收到指定的数量的CAN数据,并且与指定数据相同
        
        参数:
        - recv_id : 应该收到的CAN id
        - recv_data : 应该收到的CAN数据
        - wait_time : 超时时间(ms)
        - recv_times : 应该收到几次CAN数据
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | CAN_wait_for_data | 720 | 02 10 03 | 1000 | 5 |
        '''
        bus_can = can.interface.Bus(channel='can1', bustype='socketcan')
        recv_times = int(recv_times)
        wait_time = float(wait_time)/1000
        recv_id = self._convert_can_id(recv_id)
        recv_data = self._convert_can_recv_data(recv_data)
        start_time = time.time()
        recv_msg_num = 0
        time_list = []
        
        for act_recv_data in bus_can:
            now_time = time.time()
            if now_time-start_time > wait_time:
                break
            if act_recv_data and act_recv_data.arbitration_id == recv_id:
                if recv_data == act_recv_data.data:
                    recv_msg_num = recv_msg_num + 1
                    time_list.append(now_time)
                if recv_msg_num == recv_times:
                    break
                time.sleep(0)
        if not len(time_list):
            asserts.fail('未接收到指定的CAN数据')
        logger.info(time_list)
        if len(time_list) != recv_times and recv_times != 999:
            asserts.fail('收到的数据数量不对')
        return time_list
        '''
        last_time = time_list[0]
        avg_time = 0
        for i in time_list[1:]:
            avg_time = avg_time + abs(i-last_time)
            last_time = i
        if abs(avg_time/(recv_times-1)-interval_time) > 0.03:
            avg_time/(recv_times-1)-interval_time
        '''
        
    def CAN_id_wait(self, recv_id, wait_time, recv_times):
        '''
        功能:
        - 等待接收CAN数据
        - 通过条件 : 在wait_time时间内收到指定的数量的CAN数据
        
        参数:
        - recv_id : 应该收到的CAN id
        - wait_time : 超时时间(ms)
        - recv_times : 应该收到几次CAN数据
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | CAN_wait_for_id | 720 | 1000 | 5 |
        '''
        recv_times = int(recv_times)
        wait_time = float(wait_time)/1000
        recv_id = self._convert_can_id(recv_id)
        start_time = time.time()
        recv_msg_num = 0
        data_list = []
        
        while 1:
            now_time = time.time()
            if now_time-start_time > wait_time:
                break
            act_recv_data = BUS_CAN.recv(0.02)
            if act_recv_data and act_recv_data.arbitration_id == recv_id:
                recv_msg_num = recv_msg_num + 1
                data_list.append(self._bytes_to_hex(act_recv_data.data))
                if recv_msg_num == recv_times:
                    break
                time.sleep(0)
        if not data_list:
            asserts.fail('没收到指定ID的数据')
        return data_list
        
    def CAN_baudrate_change(self, baudrate):
        '''
        功能:
        - 切换波特率
        - 通过条件 : 输入数据无误
        
        参数:
        - baudrate : 波特率
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | CAN_change_baudrate | 500000 |
        '''
        self.restart_can(baudrate)
        print('change baudrate to {}'.format(baudrate))
    
    def _convert_can_id(self, can_id):
        '''
        can id转码
        '''
        return int(can_id, 16)
        
    def _convert_can_send_data(self, can_data):
        '''
        can data转码
        '''
        ret_list = []
        for item in can_data.split(' '):
            ret_list.append(int(str(item),16))
        while len(ret_list) < 8:
            ret_list.append(0)
        return ret_list
    
    def _convert_can_recv_data(self, can_data):
        '''
        can data转码
        '''
        if len(can_data) < 23:
            can_data = can_data + ' 00'
        return bytearray.fromhex(can_data.replace(' ', ''))
    
    def _start_monitor(self, can_id):
        '''
        开启can数据监控线程
        '''
        t = threading.Thread(target=self._monitor_can, args=(can_id,))
        t.setDaemon(True)
        t.start()
        
    def _monitor_can(self, can_id):
        '''
        - can应答数据监控
        '''
        global SHOULD_RECV_CAN_OBJECT
        global CAN_MONITOR_CTRL
        global BUS_CAN
        SHOULD_RECV_CAN_OBJECT = []
        CAN_MONITOR_CTRL = True
        while CAN_MONITOR_CTRL:
            bus_recv_msg = BUS_CAN.recv(0.02)
            if bus_recv_msg:
                if bus_recv_msg.arbitration_id == can_id:
                    SHOULD_RECV_CAN_OBJECT.append(bus_recv_msg)
                    break

    def _bytes_to_hex(self, array):
        '''
        字节码转hex
        '''
        ret_str = ''
        for byte in array:
            tmp_str = str(hex(byte))
            tmp_str = tmp_str[2:]
            if len(tmp_str) == 1:
                tmp_str = '0' + tmp_str
            ret_str = ret_str + tmp_str + ' '
        return ret_str
    
    def restart_can(self, baudrate):
        '''
        功能:
        - 重启can
        - 通过条件 : 输入数据无误
        '''
        self._colse_can(baudrate)
        self._open_can(baudrate)
        
    def _colse_can(self, baudrate):
        os.system('sudo ip link set can0 down')
        os.system('sudo ip link set can1 down')
    
    def _open_can(self, baudrate):
        global BUS_CAN, BUS_CAN1, BUS_CAN2
        setup_can0_order = 'sudo ip link set can0 up type can bitrate {}'.format(baudrate)
        setup_can1_order = 'sudo ip link set can1 up type can bitrate {}'.format(baudrate)
        os.system(setup_can0_order)
        os.system(setup_can1_order)
        os.system(setup_can0_order)
        os.system(setup_can1_order)                                              # 其实就是执行了两次打开can，因为有时候一次会失败，原因待定
        time.sleep(1)
        BUS_CAN1 = can.interface.Bus(channel='can1', bustype='socketcan')
        BUS_CAN2 = can.interface.Bus(channel='can0', bustype='socketcan')
        BUS_CAN = BUS_CAN2                                                       # 当前的使用的can口默认设置为can0
        
    def CAN_channel_choice(self, channel):
        '''
        功能:
        - 更改CAN通道
        - 通过条件 : 输入数据无误
        '''
        global BUS_CAN, BUS_CAN1, BUS_CAN2
        if channel == 'can1':
            BUS_CAN = BUS_CAN1
        else:
            BUS_CAN = BUS_CAN2
    
    def _pick_up_msg(self, send_id, send_data):
        '''
        - 用来合成can msg的，但是还没用到
        '''
        ret_msg = can.Message(
            arbitration_id = send_id,
            data = send_data, 
            extended_id = False)
        return ret_msg
    
    def _can_send_and_wait_rsp(self, recv_id, msg):
        global BUS_CAN, CAN_MONITOR_CTRL
        self._start_monitor(recv_id)             # 开启接收can数据的线程
        time.sleep(0.1)
        BUS_CAN.send(msg)                        # 发送指定的can数据
        time.sleep(0.1)
        CAN_MONITOR_CTRL = False                 # can线程关闭标志位置0
