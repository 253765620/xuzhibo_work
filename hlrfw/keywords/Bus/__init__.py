#!coding:utf-8
'''
- 编写比较复杂的业务关键字
- 现在主要是为了, 使用多线程, 同时运行两个关键字
- 原因是事件触发型测试, CAN的应答速度过快, 导致接收不到应答数据
'''
import sys
if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')
    
import threading
from time import ctime
from time import sleep
from hlrfw.keywords.CAN import CAN
from hlrfw.keywords.SerialLibrary import SerialLibrary
from hlrfw.keywords.Server import Server

class MyThread(threading.Thread):
    '''
    - 重写threding.run 获取返回值
    '''
    def __init__(self,func,args=()):
        super(MyThread,self).__init__()
        self.func = func
        self.args = args
 
    def run(self):
        self.result = self.func(*self.args)
 
    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

class test(object):
    def printf(self, num):
        print('nice'+num)


class Bus(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    lib_key_dict = {
        'SerialLibrary': 'serial',
        'CAN': 'can',
        'Server': 'server',
        'test': 'test',
        }
    
    def __init__(self):
        self.can = CAN()
        self.serial = SerialLibrary()
        self.server = Server()
        self.test = test()
        
    def wait_can_and_serial_data(self, can_id, recv_times, serial_data, wait_time):
        '''
        功能:
        - 等待接收CAN数据和串口数据
        - 通过条件 : 在wait_time时间内收到指定的数量的CAN数据和串口数据
        
        参数:
        - recv_id : 应该收到的CAN id
        - wait_time : 超时时间(ms)
        - recv_times : 应该收到几次CAN数据
        '''
        wait_time = int(wait_time)
        t_can_recv = MyThread(self.can.CAN_id_wait, args=(can_id,wait_time,recv_times))
        t_serial_recv = MyThread(self.serialLibrary.serial_send, args=('FF',serial_data,None,115200,wait_time/1000))
        t_can_recv.setDaemon(True)
        t_serial_recv.setDaemon(True)
        t_can_recv.start()
        t_serial_recv.start()
        for i in range(int(wait_time/1000)):
            #print(t_can_recv.get_result(), t_serial_recv.get_result())
            if t_can_recv.get_result() and t_serial_recv.get_result():
                break
            sleep(1)
        return (t_can_recv.get_result(),t_serial_recv.get_result())

    def wait_can_and_send_plat(self, recv_id, recv_data, wait_time, send_msg, recv_times=999, platform='gbtele'):
        '''
        - 发送远程控制指令，同时等待终端应答
        '''
        t_can_recv = MyThread(self.can.CAN_data_wait, args=(recv_id, recv_data, wait_time))
        t_plt_send = MyThread(self.server.server_data_send_ter, args=(send_msg, platform))
        t_can_recv.setDaemon(True)
        t_plt_send.setDaemon(True)
        t_can_recv.start()
        sleep(1)
        t_plt_send.start()
        for i in range(5):
            if t_can_recv.get_result() and t_plt_send.get_result():
                break
            sleep(1)
        if t_can_recv.result == None:
            asserts.fail('没收到CAN数据')
        if t_plt_send.result == None:
            asserts.fail('发送平台数据失败')
        print('can_res', t_can_recv.result, 'platform res', t_plt_send.result)
        return (t_can_recv.get_result(),t_plt_send.get_result())

    def run_hl_keywords(self, keyword_1, interval, keyword_2):
        '''
        - 准备同时运行多个关键字, 未完成
        '''
        self._split_keyword(keyword_1)
        
    def _split_keyword(self, keyword_msg):
        '''
        - 分解字符串，解析出关键字
        '''
        keyword_list = keyword_msg.strip('|').split('|')
        if len(keyword_list) < 2:
            assets.fail('数据填写过短，请按照`lib库名|关键字名|参数方式填写`')
        if keyword_list[0] not in self.lib_key_dict:
            asserts.fail('请确认填写的库名是否正确')
        obj_obj = getattr(self, self.lib_key_dict[keyword_list[0]])
        obj_method = getattr(obj_obj, keyword_list[1])
        obj_method(keyword_list[2])
