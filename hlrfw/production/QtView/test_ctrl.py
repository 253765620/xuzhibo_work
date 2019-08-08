#！coding:utf-8
import os
import sys
import time
import xlwt
from socket import *

if '/home/pi' not in sys.path:
	sys.path.append('/home/pi')

from time import sleep
from hlrfw.keywords.NetTest.__init__ import NetTest
from hlrfw.keywords.SerialLibrary.__init__ import SerialLibrary
from hlrfw.keywords.Utils.__init__ import Utils

# global param
REPORT_PATH = '/home/pi/ProductionTool/report/'


class CombinationReport(object):
    def __init__(self):
        self.project_path = '/home/pi/ProductionTool/'
        self.report_dir = REPORT_PATH
        self.report_list = []
        self.xml_file_list = []

    def start_combination(self, infor):
        self.infor = infor
        if not os.path.exists(self.report_dir):
                self.infor.emit('报告位置：'+self.report_dir+'不存在')
        self.get_report_list()
        self.build_xml_file_list()
        self.get_combination_xml_cmd()

    def get_report_list(self):
        self.report_list = os.listdir(self.report_dir)
        if not self.report_list:
            self.infor.emit('未获取到测试报告文件')

    def build_xml_file_list(self):
        for report_dir in self.report_list:
            if report_dir.find('.') != -1:
                continue
            xml_dir = self.report_dir + report_dir + '/output.xml'
            if not os.path.exists(xml_dir):
                self.infor.emit(xml_dir+'文件不存在')
            self.xml_file_list.append(xml_dir)

    def get_combination_xml_cmd(self):
        rebot_dir = self.get_rebot_dir()
        xml_cmd = rebot_dir + '/bin/rebot -d ../ '
        for i in self.xml_file_list:
            xml_cmd += i + ' '
        self.exec_cmd(xml_cmd)

    def exec_cmd(self, cmd):
        print(cmd)
        return os.system(cmd)

    def get_rebot_dir(self):
        rebot_dir_str = os.popen('whereis python-3.7.0').read()
        rebot_dir = rebot_dir_str[rebot_dir_str.find('/'):-1]
        return rebot_dir


class TestControl(object):
    key_status_dict = {
            1: '0001',
            2: '0010',
            3: '0100',
            4: '1000',
        }
    key_test_flag = False

    def __init__(self, infor=None, rfcase_dir='/home/pi/ProductionTool/nettest.txt'):
        '''
        - rfcase_dir: 测试用例的路径
        - report_path: 存放所有测试报告的根目录
        - report_dir： 存放每个报告的目录
        - self.dev_id: 设备序列号
        '''
        self.infor = infor
        self.rfcase_dir = rfcase_dir
        self.report_path = REPORT_PATH
        self.robot_log_file = 'robot.log'
        self.report_dir = ''
        self.dev_id = ''
        self.pybot_cmd  = ''
        self.project_path = '/home/pi/ProductionTool/'
        self.nettest = NetTest()
        self.serial = SerialLibrary()
        self.utils = Utils()

    def set_rfcase_dir(self, rfcase_dir):
        self.rfcase_dir = rfcase_dir

    def start_usb_test(self):
        self.get_curr_time()
        self.build_report_log()
        self.get_dev_id()
        if self.dev_id == 'no dev id' or self.dev_id == -1:
            return -1
        self.build_report_path()
        self.build_report_dir()
        self.build_pybot_cmd()
        self.exec_pybot()

    def start_key_test(self):
        self.get_curr_time()
        self.get_dev_id()
        if self.dev_id == 'no dev id' or self.dev_id == -1:
            return -1
        #先确认一遍当前的按键状态
        # test_res1 = self.confirm_key_status(self.key_status_dict[item], '0000')
        # if test_res1 != 1:
        # 	self.infor.emit('key测试失败')

        #按下按键1，2s
        #for item in [1, 2, 3, 4]:
        #	while not TestControl.key_test_flag:
        #		sleep(0.1)
        #	self.confirm_key_status(item, self.key_status_dict[item])
                # self.infor.emit('按下按键{}，实际按键状态位：{}'.format(item, '1111'))
                # self.infor.emit('按键{}测试通过'.format(item))
        #	TestControl.key_test_flag = False
        key_1 = False
        key_2 = False
        key_3 = False
        key_4 = False
        for item in range(50):
            try:
                serial_res = self.serial.serial_send('(CESHI)DEV-1', '(CESHI)DEV-1')
                location = serial_res.find('GPI')
                key_status_act = serial_res[location+8:location+12]
            except:
                continue
            if not key_1 and key_status_act[3] == '1':
                self.infor.emit('按键1测试通过')
                self.add_test_record(0, '按键1')
                key_1 = True
            if not key_2 and key_status_act[2] == '1':
                self.infor.emit('按键2测试通过')
                self.add_test_record(0, '按键2')
                key_2 = True
            if not key_3 and key_status_act[1] == '1':
                self.infor.emit('按键3测试通过')
                self.add_test_record(0, '按键3')
                key_3 = True
            if not key_4 and key_status_act[0] == '1':
                self.infor.emit('按键4测试通过')
                self.add_test_record(0, '按键4')
                key_4 = True
            if key_1 and key_2 and key_3 and key_4:
                break
            sleep(0.5)
        if not key_1:
            self.infor.emit('按键1测试失败')
            self.add_test_record(1, '按键1')
        if not key_2:
            self.infor.emit('按键2测试失败')
            self.add_test_record(1, '按键2')
        if not key_3:
            self.infor.emit('按键3测试失败')
            self.add_test_record(1, '按键3')
        if not key_4:
            self.infor.emit('按键4测试失败')
            self.add_test_record(1, '按键3')
        if not key_1 or not key_2 or not key_3 or not key_4:
            self.add_test_record(1, '按键4')
            self.infor.emit('按键测试结束,失败')
        else:
            self.infor.emit('按键测试结束,通过')
       
    def confirm_key_status(self, key_num, key_status):
        '''
        功能：
        - 确定按键状态是否都为0
        - 返回-1，代表串口应答超时
        - 返回0，代表应答的状态不匹配
        - 返回1，代表应答的状态匹配
        '''
        try:
            try:
                serial_res = self.serial.serial_send('(CESHI)DEV-1', '(CESHI)DEV-1')
            except:
                self.add_test_record(1, '按键{}'.format(key_num))
                self.infor.emit('接收串口数据失败')
                self.infor.emit('按键{}测试失败 {}'.format(key_num, serial_res))
            # if isinstance(serial_res, int):
            #	self.add_test_record(1, '按键{}'.format(key_num))
            #	self.infor.emit('按键{}测试失败 {}'.format(key_num, serial_res))
            #	return serial_res
            location = serial_res.find('GPI')
            key_status_act = serial_res[location+8:location+12]
            self.infor.emit('按下按键{}，实际按键状态位：{}'.format(key_num, key_status_act))
            if key_status_act == key_status:
                self.add_test_record(0, '按键{}'.format(key_num))
                self.infor.emit('按键{}测试通过'.format(key_num))
            else:
                self.add_test_record(1, '按键{}'.format(key_num))
                self.infor.emit('按键{}测试失败'.format(key_num))
        except Exception as e:
            self.infor.emit(str(e))
            return -1

    def get_tcp_key_status(self, data, should_data):
        i = 1
        k = self.nettest.get_usbecm_ip('usb0')
        if isinstance(k, int):
            return k
        a = k.split('.')
        a[3] = '1'
        judge = 'right'
        host = '.'.join(a)
        port = 20000
        addr = (host, port)
        tctimeClient = socket(AF_INET, SOCK_STREAM)
        try:
            tctimeClient.connect(addr)
        except ConnectionRefusedError:
            self.infor.emit('TCP connect error')
            return -1
        tctimeClient.send(data.encode())
        data_ = tctimeClient.recv(1024).decode()
        if should_data not in data_:
            tctimeClient.close()
            return -1
        tctimeClient.close()
        return data_

    def exec_pybot(self):
        test_res = self.exec_cmd(self.pybot_cmd)
        self.infor.emit('报告位置：'+self.report_dir)

        if self.rfcase_dir == '/home/pi/ProductionTool/nettest.txt':
            test_name = 'ECM'
        elif self.rfcase_dir == '/home/pi/ProductionTool/ethernet_test.txt':
            test_name = '以太网'
        else:
            test_name = 'AI-box自检'
            self.infor.emit(self.get_last_line())

        if test_res == 0:
            self.infor.emit('{}测试通过\n'.format(test_name))
        else:
            self.infor.emit('错误码：'+str(test_res))
            self.infor.emit('{}测试失败\n'.format(test_name))

        self.add_test_record(test_res, '{}测试'.format(test_name))

    def build_report_log(self):
        self.robot_log_file_dir = self.project_path + self.robot_log_file

    def get_dev_id(self):
        try:
            self.dev_id = self.serial.serial_send('(CESHI)MODEM INFO', '(CESHI)MODEM')
        except Exception as e:
            print(e)
            self.dev_id = 'no dev id'
        if self.dev_id != 'no dev id':
            self.dev_id = self.nettest.Get_icc(self.dev_id, 'ICCID')
        if self.dev_id == 'no dev id' or self.dev_id == -1:
            self.infor.emit('获取dev_id失败')
        else:
            self.infor.emit('当前设备id：'+str(self.dev_id))

    def get_curr_time(self):
        self.test_time = time.strftime('%Y_%m_%d_%H_%M_%S',time.localtime(time.time()))

    def build_report_dir(self):
        self.report_dir = '{reportpath}{dev_id}_{time}'.format(reportpath=self.report_path, time=self.test_time, dev_id=self.dev_id)
        self.mkdir(self.report_dir)

    def build_report_path(self):
        if not os.path.exists(self.report_path):
            self.mkdir(self.report_path)

    def build_pybot_cmd(self):
        self.pybot_cmd = 'pybot -P /home/pi/hlrfw/keywords -d {reportdir} {rfcasedir}'.format(reportdir=self.report_dir, rfcasedir=self.rfcase_dir)
        self.infor.emit('执行命令：'+self.pybot_cmd)

    def mkdir(self, dir_):
        if not os.path.exists(dir_):
            self.exec_cmd('mkdir %s' % dir_)

    def exec_cmd(self, cmd):
        return os.system(cmd)

    def save_log_file(self, text):
        with open(self.robot_log_file_dir, 'a') as f:
            f.write(text+'\n')

    def add_test_record(self, test_code, test_type):
        with open(self.project_path+'testrecord.txt', 'a') as file:
            if test_code == 0:
                test_res = 'PASS'
            else:
                test_res = 'FAIL'
            test_record_line = self.dev_id + '|' + test_type + '|' + test_res + '|' + str(test_code) + '|' + str(self.test_time) + '\n'
            file.write(test_record_line)

    def output_xlwt(self):
        self.get_curr_time()
        test_res_dict = {}
        lines = ''

        if not os.path.exists(self.project_path+'testrecord.txt'):
            return '还没有测试记录'
        with open(self.project_path+'testrecord.txt', 'r') as file:
            while 1:
                line = file.readline()
                if not line:
                    break
                test_res_list = line.strip().split('|')
                if test_res_list[0] not in test_res_dict:
                    test_res_dict[test_res_list[0]] = {}
                test_res_dict[test_res_list[0]][test_res_list[1]] = test_res_list[2:]
        if not test_res_dict:
            return '没有测试记录'

        item_list = ['终端序列号', 'USB ECM测试', '以太网测试', 'AIBOX自检测试', '按键1测试', '按键2测试', '按键3测试', '按键4测试']
        self.write_data_to_excel(test_res_dict)

    def set_style(self, width):
        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.width = width
        style.font = font
        return style

    def write_data_to_excel(self, test_res_dict):
        if not os.path.exists('/home/pi/hlrfw/production/excel_report'):
            os.system('mkdir /home/pi/hlrfw/production/excel_report')
        if not os.path.exists('/home/pi/hlrfw/production/ai_test_record.txt'):
            ai_file = open('/home/pi/hlrfw/production/ai_test_record.txt', 'a')
            ai_file.close()

        # write T3 report
        write_list = []
        font_list = [256*22, 256*14, 256*14,256*16, 256*8, 256*8, 256*8, 256*8]
        item_list = ['终端序列号', 'ECM测试', '以太网测试', 'AI-box自检测试', '按键1', '按键2', '按键3', '按键4']
        write_list.append(item_list)
        for serial in test_res_dict:
            list_ = [serial, ]
            for i in [1,2,3,4,5,6,7]:
                res_list = test_res_dict[serial].get(item_list[i])
                if res_list:
                    list_.append(res_list[0])
                else:
                    list_.append('None')
            write_list.append(list_)
        excel_report_dir = '/home/pi/ProductionTool/excel_report/生产测试报告_{}'.format(self.test_time)
        workbook = xlwt.Workbook(encoding='utf-8')
        data_sheet = workbook.add_sheet('T3生产测试结果')
        for i in range(8):
            data_sheet.col(i).width = font_list[i]
        for index,item in enumerate(write_list):
            for i in range(8):
                data_sheet.write(index, i, item[i])

        # write AIBOX report
        write_list = []
        font_list = [256*22, 256*8, 256*8,256*8, 256*8, 256*8, 256*8, 256*8, 256*8, 256*8, 256*8]
        item_list = ['AIBOX序列号', 'Sdcard1', 'Sdcard2', 'Emmc', 'Dvr', 'Eth', 'Uart', 'Gpio', 'Adas', 'Dsm']
        write_list.append(item_list)
        added_list = []

        with open(self.project_path+'ai_test_record.txt', 'r') as file:
            while 1:
                line = file.readline()
                if not line:
                    break
                one_record = line.strip().split('|')
                if one_record[0] not in added_list:
                    write_list.append(one_record)
                    added_list.append(one_record[0])

        data_sheet_ai = workbook.add_sheet('AIBOX生产测试结果')

        for i in range(10):
            data_sheet_ai.col(i).width = font_list[i]

        for index,item in enumerate(write_list):
            for i in range(10):
                data_sheet_ai.write(index, i, item[i])


        workbook.save(excel_report_dir+'.xls')
        self.infor.emit('报告位置：{}'.format(excel_report_dir))

    def get_last_line(self, file='/home/pi/ProductionTool/ai_test_record.txt'):
        blocksize = 1024
        maxseekpoint = 1
        filesize = os.path.getsize(file)
        with open(file, 'r') as f:
            if (maxseekpoint-1)*blocksize < filesize:
                maxseekpoint = filesize // blocksize
                if maxseekpoint == 0:
                    f.seek(0, 0)
                else:
                    f.seek((maxseekpoint-1)*blocksize, 0)
            lines = f.readlines()
            last_line = lines[-1]
            return last_line
