#!coding:utf-8
'''
功能:
- Script关键字库
- 启动脚本文件
- 播放CAN数据...
'''
import sys
if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')

import os
import time
import socket
import subprocess
import threading
import hlrfw.algorithm.metacomm.combinatorics.all_pairs2

from robot.utils import asserts
from robot.api import logger

#from hlrfw.keywords.Script.scrpit_decorator import decorator_nodesim
from hlrfw.configs.ip_config import IP_CAN
from hlrfw.scripts.can_script.can_file_transfer import CANFileTransfer
from hlrfw.configs.sys_config import SERIAL_LOG_AMA0,SERIAL_LOG_USB0,SERIAL_LOG_USB1,SERIAL_LOG_USB2,SERIAL_LOG_USB3


class Script(object):
    '''
    定义各种工具脚本
    '''
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.nodesim_view = '/home/pi/hlview/'
        self._nodesim_init()

#   def get_orthogonalit_array(self, param):
#       '''
#       功能：
#       - 获取正交矩阵
#
#        参数:
#       - 请输入参数如:
#        - param = [ [ 0, 1 ]
#        -      , [ 0, 1]
#        -      , [ 0, 1, 2 ]
#        -      , [ 0, 1, 2 ]
#        -      , [ 0, 1, 2 ]
#        -      ]
#        - 返回: 一个关于param正交排列的一个数列
#        '''
#        all_pairs = metacomm.combinatorics.all_pairs2.all_pairs2
#        try:
#            ret_list = []
#            pairwise = all_pairs(param)
#            for i, v in enumerate(pairwise):
#                ret_list.append(v)
#            return ret_list
#        except Exception as e:
#            asserts.fail(e)
        
    def CAN_replayer_start(self, replay_file, flt_id=None, channel='can1', isup=False):
        '''
        功能：
        - 回放CAN数据
        
        参数:
        - replay_file : 回放的文件位置
        - flt_id: 需要过滤的can id, 比如 0x123|0x124, 过滤多个使用 "|" 符号分割
        - channel : 回放的CAN通道，默认can1
        - isup: 是否更新回放文件，默认更新，填入True就不更新
        
        例子:
        | CAN_replayer | /home/pi/can_test.log | channel='can1' |
        '''
        self.CAN_replayer_stop()
        if not isup:
            if flt_id:
                flt_id = flt_id.strip('|').split('|')
            else:
                flt_id = []
            tanster = CANFileTransfer(replay_file, '/home/pi/hlview', flt_id)
            tanster.start_tranfer()
        csv_replay_file = replay_file[:replay_file.rfind('.log')] + '.csv'
        time.sleep(1)
        if channel == 'can2':
            channel = 'can0'
        cmd = "python3.7 /home/pi/hlrfw/scripts/can_script/can_replayer.py -c {} -i socketcan {}".format(channel, csv_replay_file)
        self._creat_thred(cmd)
        
    def CAN_replayer_stop(self):
        '''
        功能：
        - 停止回放CAN数据

        例子:
        | stop_CAN_replayer |
        '''
        self._kill_all_process('python3.7 /home/pi/hlrfw/scripts/can_script/can_replayer.py')
        
    def CAN_heartbeat_ctrl(self, status, can_id='720', can_data='02 3E 00 00 00 00 00 00', stmin=2000, channel='can1', single=False):
        '''
        功能：
        - 持续发送CAN心跳数据
        - 可以控制开关
        
        参数:
        - status: start代表开始发送，stop代表停止发送
        - can_id: 发送的can id
        - can_data: 发送的can数据
        - stmin: 发送的时间间隔
        - channel: 发送的can通道
        - single: 不填写,默认将之前的播放数据更改
        
        例子:
        | ctrl_CAN_heartbeat | start | can_id=720 | can_data='02 3E 00 00 00 00 00 00' | stmin=2000 | channel='can1' |
        '''
        if status == 'start':
            if not single:
                self._stop_CAN_heartbeat()
                time.sleep(2)
            cmd = "python3.7 /home/pi/hlrfw/scripts/can_script/can_heartbeat.py \'{}\' \'{}\' \'{}\' \'{}\'".format(can_id, can_data, channel, stmin)
            self._creat_thred(cmd)
        else:
            self._stop_CAN_heartbeat()
            
    def _stop_CAN_heartbeat(self):
        '''
        停止发送CAN心跳数据
        '''
        self._kill_all_process("python3.7 /home/pi/hlrfw/scripts/can_script/can_heartbeat.py")
        
    def _nodesim_init(self):
        '''
        - 初始化节点仿真, 关闭以前的节点仿真程序
        '''
        logger.info('节点仿真初始化')
        self._kill_all_process(self.nodesim_view)
        if not os.path.exists(self.nodesim_view):
            logger.info('没有节点仿真文件')

    def _exe_os_cmd(self, cmd):
        os.system(cmd)
        
    def _creat_thred(self, cmd):
        t_ = threading.Thread(target=self._exe_os_cmd, args=(cmd,))
        t_.setDaemon(True)
        t_.start()

    def node_simulate_start(self, test_mode, node_file, node_file_dir=None):
        '''
        功能：
        - 开启节点仿真
        
        参数:
        - test_mode : 节点仿真的测试模式, 就是外层的文件名字比如common
        - node_file: 需要开启的节点方针类型, 比如nodesim_bcm, nodesim_vcm
        - node_file_dir: 节点仿真文件具体位置, 可以不填
        
        例子:
        | node_simulate_start | common | nodesim_bcm |
        '''
        self.node_simulate_stop(test_mode, node_file)
        node_file_dir = '/home/pi/hlview/{}/{}'.format(str(test_mode), str(node_file))
        os.system('sudo chmod +x '+node_file_dir)
        self._creat_thred(node_file_dir)
        logger.info('start nodesim ...')
        
    def node_simulate_stop(self, test_mode, node_file, node_file_dir=None):
        '''
        功能：
        - 关闭节点仿真
        
        参数:
        - test_mode : 节点仿真的测试模式, 就是外层的文件名字比如common
        - node_file: 需要开启的节点方针类型, 比如bcm, vcm
        - node_file_dir: 节点仿真文件具体位置, 可以不填
        
        例子:
        | node_simulate_stop | common | bcm |
        '''
        node_file_dir = '/home/pi/hlview/{}/{}'.format(str(test_mode), str(node_file))
        self._kill_all_process(node_file_dir)

    def adj_colt_pow_freq(self, freq):
        '''
        功能:
        - 切换电流采集频率
        - 测试用例失败的时候记得把采集频率置回5s
        - 通过条件：参数填写无误
        
        参数:
        - freq: 采集频率ms
        '''
        if not freq.isdigit():
            asserts.fail('参数应该为数字')
            
        self._kill_all_process('python3.7 /home/pi/hlrfw/scripts/collect_current_data.py')
        time.sleep(1)
        os.system('python3.7 /home/pi/hlrfw/scripts/collect_current_data.py {}'.format(freq))
        
    def CAN_player_add(self, can_id, can_data, interval, channel):
        '''
        功能:
        - 添加一条can 数据播放
        
        参数:
        - can_id: --
        - can_data: --
        - channel: can通道 (选填can1, can2)
        - interval: 发送间隔(ms)
        '''
        if channel == 'can2':
            channel = 'can0'
        if channel not in ['can0', 'can1']:
            asserts.fail('无效can通道')
        sock_msg = '(\'{}\',\'{}\',\'{}\',\'{}\',\'{}\')'.format('add', can_id, can_data, channel, interval)
        self._change_can_player_sock(sock_msg)
    
    def CAN_player_delete(self, can_id):
        '''
        功能:
        - 删除一条can 数据播放
        
        参数:
        - can_id: --
        '''
        sock_msg = '(\'{}\',\'{}\',\'{}\',\'{}\',\'{}\')'.format('delete', can_id, '', '', '')
        self._change_can_player_sock(sock_msg)
        
    def CAN_player_all_delete(self):
        '''
        功能:
        - 删除所有can 数据播放
        '''
        sock_msg = '(\'{}\',\'{}\',\'{}\',\'{}\',\'{}\')'.format('delete all', '', '', '', '')
        self._change_can_player_sock(sock_msg)
        
    def device_creat(self,device):
        list = []
        deviced = os.popen('bash ' + '/home/pi/hlrfw/scripts/devicecreat.sh %s'%(device))
        list.append(deviced.read())
        for i in list:
            if i.find('Access Token') != -1:
                token = i[i.find(':')+2:]
            else:
                raise Exception ('Device with such name already exists')
        return(token)
        #return(deviced)
        #with open('/home/pi/hlrfw/scripts/deviceinfo.txt', 'r') as f:
        #   lines = f.readlines()
        #   if lines[-1] == '\n':
        #      last_line = lines[-2]
        #   else:
        #       last_line = lines[-1]
        #   if last_line.find('Access Token') != -1:
        #       token = last_line[last_line.find(':')+2:]
        #       return (token)
        #   else:
        #       raise Exception ('Device with such name already exists')
  
    def script_serial_ama0(self,status):
        '''
        功能:
        开启关闭AMA0串口
        参数：
        - starus:状态是open 还是close
        例子:
        script_serial_ama0 | open
        
        '''
        if status == 'open':
            self._kill_all_process('python /home/pi/hlrfw/scripts/serial_handle.py /dev/ttyAMA0')
            os.system('rm -rf /home/pi/nohup.out')
            time.sleep(1)
            #os.system('nohup python /home/pi/hlrfw/scripts/serial_handle.py /dev/ttyAMA0 &')
            os.system('nohup python /home/pi/hlrfw/scripts/serial_handle.py /dev/ttyAMA0 &')
            time.sleep(1)
        else:
            self._kill_all_process('python /home/pi/hlrfw/scripts/serial_handle.py /dev/ttyAMA0')
            os.system('rm -rf /home/pi/nohup.out')
    
    def script_serial_usb(self,usb,status='open'):
        '''
        功能:
        开启关闭USB串口
        参数：
        - usb:开启的是那个USB,0,1,2,3
        - starus:状态是open 还是close
        例子:
        script_serial_usb | 1 |open
        
        '''
        usb_list = os.system("find /dev/USB{}".format(usb))
        if   usb_list == 256:
            raise Exception('no found USB{}'.format(usb))
        if status == 'open':
            self._kill_all_process('python /home/pi/hlrfw/scripts/serial_handle.py /dev/USB{}'.format(usb))
            os.system('rm -rf /home/pi/nohup.out')
            time.sleep(1)
            os.system('nohup python /home/pi/hlrfw/scripts/serial_handle.py /dev/USB{} &'.format(usb))
            time.sleep(1)
        else:
            self._kill_all_process('python /home/pi/hlrfw/scripts/serial_handle.py /dev/USB{}'.format(usb))
            os.system('rm -rf /home/pi/nohup.out')

                    
    def _change_can_player_sock(self, sock_msg):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(IP_CAN)
        sock.send(sock_msg.encode())
        sock.close()
        
    def _get_process_pid(self, name):
        '''
        功能: 获取执行进程的pid
        - name: 开启进程的shell命令（一部分就可以）
        
        - 返回值: 一个pid为整型的列表
        '''
        pid_list = []
        pid_list_obj = subprocess.Popen(['pgrep', '-f', name], stdout=subprocess.PIPE, shell=False)
        pid_list_bytes = pid_list_obj.communicate()[0].split()
        
        for index,pid in enumerate(pid_list_bytes):
            int_pid = int(pid)
            print('要查询的进程PID为: ',int_pid)
            pid_list.append(int_pid)
            
        return pid_list

    def _kill_all_process(self, name):
        '''
        - 终止带有对应名字的进程
        '''
        pid_list = self._get_process_pid(name)

        if not pid_list:
            print('没有找到对应进程')

        for pid in pid_list:
            print('终止进程: ', pid)
            os.system("sudo kill -9 {}".format(pid))
   
   