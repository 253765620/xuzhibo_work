#!coding:utf-8
'''
- 封装了CAN诊断传输层的关键字
- 诊断传输层需要在PI插入isotp的内核模块
- 所以必须使用python3.7
- 对linux的版本也有要求
'''
import sys
if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')

import isotp
from robot.api import logger
from robot.utils import asserts

class IsotpCAN(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def __init__(self):
        '''
        参数初始化
        '''
        self.rsp_data = None
        self.baudrate = 500000
        self.channel = 'can1'
        #self.timeout = 0.01
        self.shd_recv_data = ''
        self.isotp_txid = 0x720
        self.isotp_rxid = 0x728
        self.isotp_sock_can_bus = isotp.socket()
        self.isotp_sock_can_bus.set_fc_opts(stmin=5, bs=10)
        self.isotp_sock_can_bus.bind(self.channel, rxid=self.isotp_rxid, txid=self.isotp_txid)
        
    def isotpCAN_send_and_rec(self, send_data, recv_data, timeout=None):
        '''
        功能：
        - 发送并且接收isotp can数据
        - 收发的CAN ID 需要设置, 默认为0x720 0x728
        - 通过条件 : 接收到CAN数据, 并且与指定CAN数据相同
        
        参数：
        - send_data : 发送的CAN数据
        - recv_data : 接收的CAN数据
        - timeout : 超时时间设置单位(ms)(未生效)
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子(电咖VIN码设置与查询):
        | isotpCAN_send_and_rec | 10 01 | 50 01 00 32 01 F4 |
        | sleep | 10 | #等待10秒的原因是,开机10秒内无法进入安全访问等级 |
        | isotpCAN_send_and_rec | 10 03 | 50 03 00 32 01 F4 |
        | isotpCAN_send_and_rec | 27 01 | 67 01 2B 3A 7A 44 |
        | isotpCAN_send_and_rec | 27 02 BE 92 38 AE | 67 02 |
        | isotpCAN_send_and_rec | 2E F1 90 01 01 01 01 01 01 01 01 01 01 01 01 01 01 01 01 01 | 6E F1 90 |
        | isotpCAN_send_and_rec | 22 F1 90 | 62 F1 90 01 01 01 01 01 01 01 01 01 01 01 01 01 01 01 01 01 |
        '''
        self.shd_recv_data = recv_data
        self._isotp_nor_pro(send_data)
        if recv_data.lower() != self.rsp_data[:-1]:
            asserts.fail('接收错误数据')
        else:
            logger.info('数据校验成功')

    def isotpCAN_send(self, send_data):
        '''
        功能：
        - 发送并且接收isotp can数据
        - 收发的CAN ID 需要设置，默认为0x720 0x728
        - 通过条件 : CAN数据格式填写无误
        
        参数：
        - send_data : 发送的CAN数据
        - timeout : 超时时间设置单位(ms)(未生效)
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | isotpCAN_send | 10 01 | #进入默认会话模式 |
        
        '''
        self.isotp_send_data = self._isotp_convert_can_send(send_data)
        self._isotp_data_send()
        logger.info('发送数据成功')
        
    def isotpCAN_send_and_rec_except(self, send_data, recv_data):
        '''
        功能：
        - 发送并且接收isotp can数据
        - 收发的CAN ID 需要设置，默认为0x720 0x728
        - 通过条件 : 接收到CAN数据，并且接收到的CAN数据与指定的CAN数据不同
        
        参数：
        - send_data : 发送的CAN数据
        - recv_data : 接收的CAN数据
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | isotpCAN_send_and_rec_except | 10 01 | 7F 01 |
        
        '''
        self.shd_recv_data = recv_data
        self._isotp_nor_pro(send_data)
        if recv_data.lower() == self.rsp_data[:-1]:
            asserts.fail('收到了不想要的否定响应码')
            
    def isotpCAN_send_and_rec_nrc(self, send_data, NRC):
        '''
        功能:
        - 发送并接收CAN数据,判断NRC
        - 通过条件 : 接收到CAN数据,并收到期待的否定响应7F,以及指定的NRC
        
        参数:
        - send_data : 发送的数据
        - NRC : 填写的是第三个字节的否定响应码
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | isotpCAN_send_and_rec_nrc | 10 01 | 7F 01 |
        '''
        self._isotp_nor_pro(send_data)
        if self._isotp_get_recv_data_loc(self.rsp_data, 1) != '7f':
            asserts.fail('不是否定响应')
        if self._isotp_get_recv_data_loc(self.rsp_data, 3) != NRC.lower():
            asserts.fail('不是期待的否定响应码:'+NRC)
        logger.info('CAN数据应答正常')
    
    def isotpCAN_send_and_rec_neg(self, send_data):
        '''
        功能:
        - 发送并接收CAN数据
        - 通过条件 : 接收到CAN数据,并收到期待的否定响应7f
        
        参数:
        - send_data : 发送的数据
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | isotpCAN_send_and_rec_neg | 10 01 |
        '''
        self._isotp_nor_pro(send_data)
        if self._isotp_get_recv_data_loc(self.rsp_data, 1) != '7f':
            asserts.fail('不是否定响应')
        logger.info('收到否定响应,测试通过')
    
    def isotpCAN_send_and_rec_pos(self, send_data):
        '''
        功能:
        - 发送并接收CAN数据, 判断肯定响应
        - 通过条件 : 收到CAN数据, 并且为肯定响应
        
        参数:
        - send_data : 发送的数据
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | isotpCAN_send_and_rec_pos | 10 01 |
        '''
        self._isotp_nor_pro(send_data)
        if self._isotp_hex_add_4(self._isotp_get_recv_data_loc(send_data, 1)) == self._isotp_get_recv_data_loc(self.rsp_data, 1):
            logger.info('收到肯定响应')
        else:
            asserts.fail('没有收到期待的肯定响应')
    
    def isotpCAN_send_and_return(self, send_data):
        '''
        功能:
        - 发送并接收CAN数据,并且返回收到的CAN数据
        - 通过条件 : 收到CAN数据
        
        参数:
        - send_data : 发送的数据
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | ${value} | isotpCAN_send_and_rec_pos | 10 01 |
        '''
        self._isotp_nor_pro(send_data)
        return self.rsp_data[:-1].upper()
            
    def isotpCAN_send_and_no_rsp(self, send_data):
        '''
        功能:
        - 发送并接收CAN数据, 判断肯定响应
        - 通过条件 : 没收到当前指定的CAN ID的CAN数据
        
        参数:
        - send_data : 发送的数据
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | isotpCAN_send_and_no_rsp | 10 01 |
        '''
        self.isotp_send_data = self._isotp_convert_can_send(send_data)
        self._isotp_data_send_and_rec()
        if self.rsp_data:
            asserts.fail('不应该收到应答数据: '+self._isotp_bytes_to_hex(self.rsp_data))
            
    def isotpCAN_send_and_rec_rsp(self, send_data):
        '''
        功能:
        - 发送并接收CAN数据, 判断肯定响应
        - 通过条件 : 收到当前指定的CAN ID的CAN数据
        
        参数:
        - send_data : 发送的数据
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | isotpCAN_send_and_no_rsp | 10 01 |
        '''
        self._isotp_nor_pro(send_data)
        if not self.rsp_data:
            asserts.fail('没有收到任何当前指定的CAN ID的应答数据')      

    def isotpCAN_change_channel(self, channel):
        '''
        功能：
        - 修改CAN通道
        
        参数：
        - channel : CAN通道选择，可填``can1`` ``can2``, 默认为can1
        (注意没有默认值的参数是必填的,有默认值的参数不填写,就会按照默认的参数执行)
        
        例子:
        | isotpCAN_change_channel | can1 |
        
        '''
        if channel == 'can1' and channel != self.channel:
            self.channel = channel
        if channel == 'can2' and self.channel != 'can0':
            self.channel = 'can0'
        self._isotp_flush_obj()
    
    def isotpCAN_change_txid_and_rxid(self, txid, rxid):
        '''
        功能：
        - 修改CAN的发送ID和接收的ID
        
        参数：
        - txid : 需要设置的接收ID
        - rxid : 需要设置的发送ID
        
        例子:
        | isotpCAN_change_txid_and_rxid | 720 | 728 |
        
        '''
        self.isotp_txid = self._isotp_convert_can_id(txid)
        self.isotp_rxid = self._isotp_convert_can_id(rxid)
        self._isotp_flush_obj()

    def isotp_set_stmin_and_bs(self):
        pass
    
    def isotp_change_baudrate(self):
        pass#restart can

    def _isotp_data_convert(self, send_data, recv_data):
        '''
        转换将要发送和接收数据格式(停用)
        '''
        self.isotp_send_data = self._isotp_convert_can_send(send_data)
        self.isotp_shd_recv_data = self._isotp_convert_can_send(recv_data)
        
    def _isotp_flush_obj(self):
        '''
        刷新CAN对象，更新CAN对象参数
        '''
        self.isotp_sock_can_bus.close()
        self.isotp_sock_can_bus = isotp.socket()
        self.isotp_sock_can_bus.set_fc_opts(stmin=5, bs=10)
        self.isotp_sock_can_bus.bind(self.channel, rxid=self.isotp_rxid, txid=self.isotp_txid)
        
    def _isotp_data_send_and_rec(self):
        '''
        发送CAN数据，并且接收CAN数据
        '''
        self._isotp_data_send()
        self._isotp_data_rec()
        
    def _isotp_data_send(self):
        '''
        发送CAN数据
        '''
        self.isotp_sock_can_bus.send(self.isotp_send_data)
        
    def _isotp_data_rec(self):
        '''
        接收CAN数据
        '''
        self.rsp_data = self.isotp_sock_can_bus.recv()
        
    def _isotp_convert_can_id(self, can_id):
        '''
        转换CAN ID数据
        '''
        return int(can_id, 16)
    
    def _isotp_convert_can_send(self, can_data):
        '''
        转换发送和接收数据格式公式
        '''
        return bytearray.fromhex(can_data.replace(' ', ''))
    
    def _isotp_bytes_to_hex(self, array):
        '''
        接收到的数据转化为打印数据的格式
        '''
        ret_str = ''
        for byte in array:
            tmp_str = str(hex(byte))
            tmp_str = tmp_str[2:]
            if len(tmp_str) == 1:
                tmp_str = '0' + tmp_str
            ret_str = ret_str + tmp_str + ' '
        return ret_str
    
    def _isotp_is_recv_data(self):
        '''
        判断是否收到到CAN数据，如果收到就打印数据(如果应收数据不是 7e 00,就过滤心跳数据)
        '''
        if self.shd_recv_data.lower() != '7e 00':
            self._isotp_recv_data_ignore_heartbeat()
        if not self.rsp_data:
            self._isotp_rewait_rsp_data()
        self.rsp_data = self._isotp_bytes_to_hex(self.rsp_data)
        logger.info(self.rsp_data)
    
    def _isotp_recv_data_ignore_heartbeat(self):
        self.shd_recv_data = ''
        for i in range(20):
            if not self.rsp_data or i == 19:
                self._isotp_rewait_rsp_data()
            if self._isotp_bytes_to_hex(self.rsp_data)[:-1] == '7e 00':
                self._isotp_data_rec()
            else:
                break
        
    def _isotp_rewait_rsp_data(self):
        self._isotp_data_rec()
        if not self.rsp_data:
            asserts.fail('未接收到数据')
        
    def _isotp_get_recv_data_loc(self, str_data, location):
        '''
        获取对应字节位置的CAN数据
        '''
        return str_data[location*3-3:location*3-1]
    
    def _isotp_hex_add_4(self, data):
        return hex(int(data,16)+64)[2:]
        
    def _isotp_nor_pro(self, send_data):
        self.isotp_send_data = self._isotp_convert_can_send(send_data)
        self._isotp_data_send_and_rec()
        self._isotp_is_recv_data()
        