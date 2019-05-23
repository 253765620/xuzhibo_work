#！coding:utf-8
import os
import sys
import time
import xlwt
from socket import *
import threading
from ftplib import FTP
if '/home/pi' not in sys.path:
	sys.path.append('/home/pi')

from time import sleep
from hlrfw.keywords.NetTest.__init__ import NetTest
from hlrfw.keywords.SerialLibrary.__init__ import SerialLibrary
from hlrfw.keywords.Utils.__init__ import Utils


# global param
REPORT_PATH = '/home/pi/production/report/'
STOP_T = True

class CombinationReport(object):
    def __init__(self):
        self.project_path = '/home/pi/production/'
        self.report_dir = REPORT_PATH
        self.report_list = []
        self.xml_file_list = []
        self.Utils = Utils
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
    led_test_flag = False

    def __init__(self, infor=None, rfcase_dir='/home/pi/production/nettest.txt'):
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
        self.rfvariable_dir = '/home/pi/production/param_test.py'
        self.report_dir = ''
        self.dev_id = ''
        self.pybot_cmd  = ''
        self.project_path = '/home/pi/production/'
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
            return 1
        self.build_report_path()
        self.build_report_dir()
        self.build_pybot_cmd()

        return self.exec_pybot()

    def get_key_status(self, key_num):
        for i in range(50):
            serial_res = self.serial.serial_send('(CESHI)DEV-1', '(CESHI)DEV-1')
            location = serial_res.find('GPI')
            key_status_act = serial_res[location+8:location+12]
            if key_status_act[4-key_num] == '1':
                return 1
            sleep(0.1)
        return 0

    def start_led_test(self):
        self.get_curr_time()
        self.get_dev_id()
        if self.dev_id == 'no dev id' or self.dev_id == -1:
            return 1
        TestControl.led_test_flag = False
        try:
            self.serial.serial_send('(CESHI)OLED 1-99','(CESHI)OLED DONE')
            self.serial.serial_send('(CESHI)OLED 2-99','(CESHI)OLED DONE')
            self.serial.serial_send('(CESHI)OLED 3-99','(CESHI)OLED DONE')
            self.serial.serial_send('(CESHI)OLED 4-99','(CESHI)OLED DONE')
        except Exception as e:
            self.infor.emit(str(e)+':串口异常')
        for i in range(40):
            sleep(0.3)
            if TestControl.led_test_flag:
                try:
                    self.serial.serial_send('(CESHI)OLED 1-0','(CESHI)OLED DONE')
                    self.serial.serial_send('(CESHI)OLED 2-0','(CESHI)OLED DONE')
                    self.serial.serial_send('(CESHI)OLED 3-0','(CESHI)OLED DONE')
                    self.serial.serial_send('(CESHI)OLED 4-0','(CESHI)OLED DONE')
                except Exception as e:
                    self.infor.emit(str(e)+':串口异常')
                self.infor.emit('LED测试通过')
                self.add_test_record(0,'LED测试')
                return 0
        if not TestControl.led_test_flag:
            self.serial.serial_send('(CESHI)OLED 1-0','(CESHI)OLED DONE')
            self.serial.serial_send('(CESHI)OLED 2-0','(CESHI)OLED DONE')
            self.serial.serial_send('(CESHI)OLED 3-0','(CESHI)OLED DONE')
            self.serial.serial_send('(CESHI)OLED 4-0','(CESHI)OLED DONE')
            self.infor.emit('LED测试失败')
            self.add_test_record(1,'LED测试')
            return 1

    def start_key_test(self):
        self.get_curr_time()
        self.get_dev_id()
        if self.dev_id == 'no dev id' or self.dev_id == -1:
            return 1

        #按下按键1，2s
        for item in [1, 2, 3, 4]:
            try:
                key_status = self.get_key_status(item)
            except Exception as e:
                key_status = 0
                self.infor.emit(str(e))
            if key_status:
                self.infor.emit('按键{}测试通过'.format(item))
                self.add_test_record(0, '按键{}'.format(item))
            else:
                self.infor.emit('按键{}测试失败'.format(item))
                self.add_test_record(1, '按键{}'.format(item))
                return 1
        return 0
        
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
        global STOP_T
        T = threading.Thread(target=self.process_display)
        T.setDaemon(True)
        T.start()
        test_res = self.exec_cmd(self.pybot_cmd)
        sleep(3)
        STOP_T = False
        self.reflash_txt()
        self.infor.emit('报告位置：'+self.report_dir)

        if self.rfcase_dir == '/home/pi/production/case/board_case.txt':
            test_name = '主板功能测试'
        elif self.rfcase_dir == '/home/pi/production/case/ethernet_test.txt':
            test_name = '以太网'
        elif self.rfcase_dir == '/home/pi/production/case/production_case.txt':
            test_name = '整机功能测试'
        elif self.rfcase_dir =='/home/pi/production/case/quality_test.txt':
            test_name = '质检测试'
        elif self.rfcase_dir == '/home/pi/production/case/setid_case.txt':
            test_name = '参数设置'
        else:
            test_name = 'AI-box自检测试-序列号设置'
            self.infor.emit(self.get_last_line())

        self.add_test_record(test_res, '{}测试'.format(test_name))

        if test_res == 0:
            self.infor.emit('{}测试通过\n'.format(test_name))
            return 0
        else:
            self.infor.emit('错误码：'+str(test_res))
            self.infor.emit('{}测试失败\n'.format(test_name))
            return 1


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
            return self.dev_id

    def get_curr_time(self):
        self.test_time = time.strftime('%Y_%m_%d_%H_%M_%S',time.localtime(time.time()))
        self.infor.emit('测试时间：' + self.test_time)

    def build_report_dir(self):
        self.report_dir = '{reportpath}{dev_id}_{time}'.format(reportpath=self.report_path, time=self.test_time, dev_id=self.dev_id)
        self.mkdir(self.report_dir)

    def build_report_path(self):
        if not os.path.exists(self.report_path):
            self.mkdir(self.report_path)

    def build_pybot_cmd(self):
        self.pybot_cmd = 'pybot --listener Listener_production  -P /home/pi/hlrfw/keywords -d {reportdir} --variablefile {rfvariable} --variablefile /home/pi/production/ID_param.py {rfcasedir}'.format(reportdir=self.report_dir,rfvariable=self.rfvariable_dir ,rfcasedir=self.rfcase_dir)
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

        #item_list = ['终端序列号', 'USB ECM测试', '以太网测试', 'AIBOX自检测试', '按键1测试', '按键2测试', '按键3测试', '按键4测试', 'LED灯测试']
        self.write_data_to_excel(test_res_dict)

    def set_style(self, width):
        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.width = width
        style.font = font
        return style

    def write_data_to_excel(self, test_res_dict):
        os.system('mkdir /home/pi/production/excel_report/')
        # write T3 report
        write_list = []
        font_list = [256*22, 256*14, 256*14,256*16, 256*8, 256*8, 256*8, 256*8, 256*14]
        item_list = ['终端序列号', 'ECM测试', '以太网测试', 'AI-box自检测试', '按键1', '按键2', '按键3', '按键4', 'LED测试']
        write_list.append(item_list)
        for serial in test_res_dict:
            list_ = [serial, ]
            for i in [1,2,3,4,5,6,7,8]:
                res_list = test_res_dict[serial].get(item_list[i])
                if res_list:
                    list_.append(res_list[0])
                else:
                    list_.append('None')
            write_list.append(list_)
        excel_report_dir = '/home/pi/production/excel_report/生产测试报告_{}'.format(self.test_time)
        workbook = xlwt.Workbook(encoding='utf-8')
        data_sheet = workbook.add_sheet('T3生产测试结果')
        for i in range(9):
            data_sheet.col(i).width = font_list[i]
        for index,item in enumerate(write_list):
            for i in range(9):
                data_sheet.write(index, i, item[i])
        
        if os.path.exists(self.project_path+'ai_test_record.txt'):
            # write AIBOX report
            write_list = []
            font_list = [256*22, 256*8, 256*8,256*8, 256*8, 256*8, 256*8, 256*8, 256*8, 256*8, 256*8]
            #item_list = ['AIBOX序列号', 'Sdcard1', 'Sdcard2', 'Emmc', 'Dvr', 'Eth', 'Uart', 'Gpio', 'Adas', 'Dsm']
            item_list = ['AIBOX序列号', 'Dsm', 'Adas', 'Gpio', 'Uart', 'Eth', 'Dvr', 'Emmc', 'Sdcard2', 'Sdcard1']

            write_list.append(item_list)
            added_dict = {}
            
            with open(self.project_path+'ai_test_record.txt', 'r') as file:
                while 1:
                    line = file.readline()
                    if not line:
                        break
                    one_record = line.strip().split('|')
                    if one_record[0] not in added_dict:
                        write_list.append(one_record)
                        added_dict[one_record[0]] = len(write_list) - 1
                    else:
                        write_list[added_dict[one_record[0]]] = one_record

            data_sheet_ai = workbook.add_sheet('AIBOX生产测试结果')

            for i in range(10):
                data_sheet_ai.col(i).width = font_list[i]

            for index,item in enumerate(write_list):
                for i in range(10):
                    data_sheet_ai.write(index, i, item[i])

        workbook.save(excel_report_dir+'.xls')
        self.infor.emit('报告位置：{}'.format(excel_report_dir))

    def get_last_line(self, file='/home/pi/production/ai_test_record.txt'):
        blocksize = 1024
        maxseekpoint = 1
        if os.path.exists(file):
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
        else:
            last_line = '没有测试记录文件'
        return last_line

    def write_res_file(self,ICCID,state):
        with open('/home/pi/production/signal_test.py','a') as f:
            f.write('\''+ICCID+'\''+'='+'\''+state+'\''+'\n')

    def judge_num(self,num):
        if num>=0:
            return 0
        else:return 1

    def process_display(self):
        global STOP_T
        STOP_T=True
        while (STOP_T):
            with open('/home/pi/production/process_display.txt', 'r') as f:
                m = f.read()
                if m !=None and m.strip()!='':
                    self.infor.emit(m)
                    os.system('sudo rm -rf /home/pi/production/process_display.txt')
                    os.system('touch /home/pi/production/process_display.txt')
                sleep(3)

    def reflash_txt(self):
        os.system('sudo rm -rf /home/pi/production/process_display.txt')
        os.system('touch /home/pi/production/process_display.txt')

    def ftp_upload(self,filename1 = '/home/pi/production/res_hardsoft/hard_soft.txt',filename2 = 'hard_soft.txt' ):
        ftp = FTP(timeout=10)
        try:
            print(11)
            ftp.connect('192.168.3.85', 2018)
            ftp.login('scjc', 'scjc')
            ftp.set_pasv(False)
            bufsize = 1024
            fp = open(filename1, 'rb')
            ftp.storbinary('STOR '+filename2,fp,bufsize)
            ftp.close()
        except BaseException:
            print('ftp连接错误')

    def ftp_downloadfile(self,filename1 = '/home/pi/production/res_hardsoft/hard_soft.txt' ,filename2 = 'hard_soft.txt'  ):
        f = FTP(timeout=10)
        f.connect('192.168.3.85', 2018)
        f.login('scjc', 'scjc')
        bufsize = 1024  # 设置缓冲器大小
        fp = open(filename1, 'wb')
        f.retrbinary('RETR %s' % filename2, fp.write, bufsize)
        fp.close()

    def id_judge(self,start,end,clientid=False):
        if clientid==False:
            start = int(start)
            end = int(end)
            if start<=end:
                return 0
            else:
                return 1
        else:
            start = int(start[-17:])
            end = int(end[-17:])
            if start<=end:
                return 0
            else:
                return 1

    def pid_down_(slef,str_):
        pid_1 = str_[:3]
        pid_2 = int(str_[-4:])
        pid_2 -= 1
        pid_2 = str(pid_2)
        while len(pid_2)<4:
            pid_2 = '0'+pid_2
        pid = pid_1+pid_2
        return str(pid)
       



