#！coding:utf-8
import os
import sys
import glob
import time
from time import sleep

if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')
    
#from s19 import *
#from core import *
import PyQt5
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from production.ID_param import *

from test_ctrl import TestControl, CombinationReport
from hlrfw.keywords.NetTest.__init__ import NetTest

def pid_down(str_):
    pid_1 = str_[:3]
    pid_2 = int(str_[-4:])
    pid_2 -= 1
    pid_2 = str(pid_2)
    while len(pid_2)<4:
        pid_2 = '0'+pid_2
    pid = pid_1+pid_2
    return str(pid)
__all__ = ['UIFlashloader']
RUN_FLAG = True
# 状态位表示： 开始测试，按键测试，结束测试， 显示内容/样式， 显示内容/样式，显示的数字累加。None就是表示不做操作
key_status_dict = {
    '主板功能测试': {'开始测试': [False, False, False, '等待结果', 'background-color: rgb(255, 255, 0)', '繁忙', None, None],
            '测试通过': [True, False, True, '主板功能测试PASS', 'background-color: rgb(0, 255, 0)', '空闲', None, None],
            '测试失败': [True, False, True, '主板功能测试Fail', 'background-color: rgb(255, 0, 0)', '空闲', None, None],},
    '按键': {'开始测试': [False, True, False, '按下按钮1', 'background-color: rgb(255, 255, 0)', '查看信息提示结果', 'background-color: rgb(255, 255, 0)', None],
            '按键1测试通过': [False, True, True, '按键1PASS', 'background-color: rgb(0, 255, 0)', '请按下按键2', None, None],
            '按键1测试失败': [True, True, True, '按键1Fail', 'background-color: rgb(255, 0, 0)', '按键测试失败', None, None],
            '按键2测试通过': [False, True, True, '按键2PASS', 'background-color: rgb(0, 255, 0)', '请按下按键3', None, None],
            '按键2测试失败': [True, True, True, '按键2Fail', 'background-color: rgb(255, 0, 0)', '按键测试失败', None, None],
            '按键3测试通过': [False, True, True, '按键3PASS', 'background-color: rgb(0, 255, 0)', '请按下按键4', None, None],
            '按键3测试失败': [True, True, True, '按键3Fail', 'background-color: rgb(255, 0, 0)', '按键测试失败', None, None],
            '按键4测试通过': [True, False, True, 'PASS', 'background-color: rgb(0, 255, 0)', '测试结束', None, None],
            '按键4测试失败': [True, False, True, 'Fail', 'background-color: rgb(255, 0, 0)', '按键测试失败', None, None],
            '按键测试失败': [True, False, True, '按键测试Fail', 'background-color: rgb(255, 0, 0)', '按键测试结束', None, None],
            '按键测试通过': [True, False, True, '按键测试PASS', 'background-color: rgb(0, 255, 0)', '按键测试结束', None, None],
            },
    '继电器':{ '开始测试': [False, True, False, '开始测试继电器', 'background-color: rgb(255, 255, 0)', '查看信息提示结果', 'background-color: rgb(255, 255, 0)', None],
              '测试通过': [True, False, True, '继电器测试PASS', 'background-color: rgb(0, 255, 0)', '继电器测试结束', None, None],
              '测试失败': [True, False, True, '继电器测试Fail', 'background-color: rgb(255, 0, 0)', '继电器测试结束', None, None],
            },
    'LED': {'开始测试': [False, True, False, '开始测试LED', 'background-color: rgb(255, 255, 0)', '查看信息提示结果', 'background-color: rgb(255, 255, 0)', None],
            '测试通过': [True, False, True, 'LED测试PASS', 'background-color: rgb(0, 255, 0)', 'LED测试结束', None, None],
            '测试失败': [True, False, True, 'LED测试Fail', 'background-color: rgb(255, 0, 0)', 'LED测试结束', None, None],
            },
    'ACCE': {'开始夹具测试': [False, True, False, '开始测试ACCE', 'background-color: rgb(255, 255, 0)', '请放上夹具', 'background-color: rgb(255, 255, 0)', None],
            '开始方向测试': [False, True, False, '开始测试ACCE', 'background-color: rgb(255, 255, 0)', '摇晃终端', 'background-color: rgb(255, 255, 0)', None],
            '测试通过': [True, False, True, 'ACCE测试PASS', 'background-color: rgb(0, 255, 0)', 'LED测试结束', None, None],
            '测试失败': [True, False, True, 'ACCE测试Fail', 'background-color: rgb(255, 0, 0)', 'LED测试结束', None, None],
            },
    '质检测试': {'开始测试': [False, False, False, '等待结果', 'background-color: rgb(255, 255, 0)', '繁忙', None, None],
            '测试通过': [True, False, True, '质检测试PASS', 'background-color: rgb(0, 255, 0)', '空闲', None, None],
            '测试失败': [True, False, True, '质检测试Fail', 'background-color: rgb(255, 0, 0)', '空闲', None, None],},
    'AI-box自检测试-序列号设置': {'开始测试': [False, False, False, '等待结果', 'background-color: rgb(255, 255, 0)', '繁忙', None, None],
            '测试通过': [True, False, True, '检测通过PID为:'+pid_start, 'background-color: rgb(0, 255, 0)', '空闲', None, None],
            '测试失败': [True, False, True, 'AI-box自检测试-序列号设置Fail', 'background-color: rgb(255, 0, 0)', '空闲', None, None],},
    '整机功能测试': {'开始测试': [False, False, False, '等待结果', 'background-color: rgb(255, 255, 0)', '繁忙', None, None],
             '测试通过': [True, False, True, '整机功能测试PASS', 'background-color: rgb(0, 255, 0)', '空闲', None, None],
             '测试失败': [True, False, True, '整机功能测试Fail', 'background-color: rgb(255, 0, 0)', '空闲', None, None], },
    '获取dev id失败': {'测试失败': [True, False, True, '获取dev id失败', 'background-color: rgb(255, 0, 0)', '空闲', None, None],},
    '通过数量': {'测试通过': [True, False, True, '测试通过', 'background-color: rgb(255, 0, 0)', None, None, True],},

}
# 保存测试结果的字典
# test_dev_id_dict = {
#     'dev_id': ['ECM测试结果', '按键1测试结果', '按键2测试结果', '按键3测试结果', '按键4测试结果', '自检结果']
# }
test_dev_id_dict = {}


class AsFlashloader(QThread):
    infor = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        super(QThread, self).__init__(parent)
        self.app = None
        self.test_ctrl = TestControl(self.infor)
        self.nettest = NetTest()

    def setTarget(self, testType):
        self.testType = testType

    def run(self):
        test_type = self.testType
        flag = True
        if test_type == '主板：ECM&以太网&按键&LED':
            for i in range(1):
                self.infor.emit('开始测试ECM')
                for i in range(100):
                    dev_status = self.nettest.get_net_state('usb0')
                    if dev_status == 1:
                        break
                    if dev_status == 0 and flag:
                        self.infor.emit('检测到USB')
                        flag = False
                    sleep(0.2)
                if dev_status == 1:
                    self.test_ctrl.set_rfcase_dir('/home/pi/production/nettest.txt')
                    test_res = self.test_ctrl.start_usb_test()
                    if test_res == 1:
                        break
                else:
                    self.infor.emit('ECM测试失败, 未检测到USB')
                    break
                sleep(1)
                self.infor.emit('开始测试以太网')
                self.test_ctrl.set_rfcase_dir('/home/pi/production/ethernet_test.txt')
                test_res = self.test_ctrl.start_usb_test()
                if test_res == 1:
                    break
                sleep(1)
                self.infor.emit('开始测试LED灯')
                self.infor.emit('确认4个LED之后点击确认按钮')
                test_res = self.test_ctrl.start_led_test()
                if test_res == 1:
                    break
                sleep(1)
                self.infor.emit('开始测试按键')
                test_res = self.test_ctrl.start_key_test()
                if test_res != 1:
                    self.infor.emit('通过数量加1')
        elif test_type == '整机：ECM&AI-box自检测试&按键&LED':
            for i in range(1):
                self.infor.emit('开始测试ECM')
                for i in range(100):
                    dev_status = self.nettest.get_net_state('usb0')
                    if dev_status == 1:
                        break
                    if dev_status == 0 and flag:
                        self.infor.emit('检测到USB')
                        flag = False
                    sleep(0.2)
                if dev_status:
                    self.test_ctrl.set_rfcase_dir('/home/pi/production/nettest.txt')
                    test_res = self.test_ctrl.start_usb_test()
                    if test_res == 1:
                        break
                else:
                    self.infor.emit('ECM测试失败, 未检测到USB')
                    break
                sleep(1)
                self.infor.emit('开始测试AI-box自检测试')
                self.test_ctrl.set_rfcase_dir('/home/pi/production/ai_test.txt')
                test_res = self.test_ctrl.start_usb_test()
                if test_res == 1:
                    break
                sleep(1)
                self.infor.emit('开始测试LED灯')
                self.infor.emit('确认4个LED之后点击确认按钮')
                test_res = self.test_ctrl.start_led_test()
                if test_res == 1:
                    break
                sleep(1)
                self.infor.emit('开始测试按键')
                test_res = self.test_ctrl.start_key_test()
                if test_res != 1:
                    self.infor.emit('通过数量加1')
        elif test_type == '按键检测&LED':
            for i in range(1):
                self.infor.emit('开始测试LED灯')
                self.infor.emit('确认4个LED之后点击确认按钮')
                test_res = self.test_ctrl.start_led_test()
                if test_res == 1:
                    break
                sleep(1)
                self.infor.emit('开始测试按键')
                test_res = self.test_ctrl.start_key_test()
                if test_res != 1:
                    self.infor.emit('通过数量加1')
        elif test_type == '质检测试':
            os.system('sudo pybot -P /home/pi/hlrfw/keywords /home/pi/production/volt.txt')
            self.infor.emit('开始测试质检测试')
            self.test_ctrl.set_rfcase_dir('/home/pi/production/case/quality_test.txt')
            #self.test_ctrl.start_usb_test()
            m  = self.test_ctrl.start_usb_test()
            if m ==0:
                with open('/home/pi/production/mid.txt','r') as a1:
                    a1_ = a1.read()
                with open('/home/pi/production/quality.txt','a') as a2:
                    a2.write(a1_)
                os.system('sudo rm -rf /home/pi/production/mid.txt')
                self.infor.emit('通过数量加1')
            else:
                os.system('sudo rm -rf /home/pi/production/mid.txt')
        elif test_type == '主板功能测试':
            #os.system('sudo pybot -P /home/pi/hlrfw/keywords /home/pi/production/volt.txt')
            #led_t = self.test_ctrl.start_led_test()
            #if led_t==0:
                #relay = self.test_ctrl.start_relay_test()
                #if relay == 0:
                #self.infor.emit('开始测试按键')
                #btn_res = self.test_ctrl.start_key_test()
                #self.test_ctrl.restart()
                #if btn_res==0:
            n = self.test_ctrl.acce_test()
            if n == 0:
                self.infor.emit('开始主板功能测试')
                self.test_ctrl.set_rfcase_dir('/home/pi/production/case/board_case.txt')
                m  = self.test_ctrl.start_usb_test()
                if m ==0:
                    self.infor.emit('通过数量加1')
        elif test_type == 'AI-box自检测试-序列号设置':
            os.system('sudo pybot -P /home/pi/hlrfw/keywords /home/pi/production/volt.txt')
            iccid_forai = self.test_ctrl.get_dev_id()
            if iccid_forai!=None and len(iccid_forai)<20:
                self.infor.emit('AI-box自检测试-序列号设置测试失败未找到iccid:{}对应的设备'.format(iccid_forai))
            else:                 
                try:
                    #self.test_ctrl.ftp_downloadfile()
                    with open('/home/pi/production/res_hardsoft/hard_soft.txt','r')as ff:
                        lll = ff.readlines()
                        for line in lll:
                            if  iccid_forai != None and  iccid_forai in line  :
                                self.infor.emit('开始AI-box自检测试-序列号设置测试')
                                self.test_ctrl.set_rfcase_dir('/home/pi/production/case/ai_test.txt')
                                m  = self.test_ctrl.start_usb_test()
                                if m == 0:
                                    self.infor.emit('通过数量加1')
                                    self.infor.emit('测试通过设置的PID为'+pid_start)
                                # if m ==0:
                                #     self.test_ctrl.set_rfcase_dir('/home/pi/production/case/setid_case.txt')
                                #     n = self.test_ctrl.start_usb_test()
                                break
                    with open('/home/pi/production/res_hardsoft/hard_soft.txt','r')as fff:
                        file_all = fff.read()
                        #print(file_all)
                        if file_all.find(iccid_forai) == -1:
                            #print(1)
                            self.infor.emit('AI-box自检测试-序列号设置测试失败本机ICCID为{}1111'.format(iccid_forai))
                except FileNotFoundError:
                    self.infor.emit('AI-box自检测试-序列号设置测试失败未找到iccid:{}对应的设备'.format(iccid_forai))
        elif test_type == '整机功能测试':
            os.system('sudo pybot -P /home/pi/hlrfw/keywords /home/pi/production/volt.txt')
            iccid_forai = self.test_ctrl.get_dev_id()
            if iccid_forai != None and len(iccid_forai)<20 :
                self.infor.emit('整机功能测试失败,未找到iccid:{}对应的设备'.format(iccid_forai))
            #self.test_ctrl.ftp_downloadfile(filename1='/home/pi/production/res_hardsoft/hardware_res.txt',filename2='hardware_res.txt')
            else:
                try:
                    with open('/home/pi/production/res_hardsoft/hardware_res.txt','r')as ff:
                        lll = ff.readlines()
                        if len(str(lll))<4:
                            self.infor.emit('整机功能测试失败,未找到iccid:{}对应的设备'.format(iccid_forai))
                        else:
                            for line in lll:
                                if iccid_forai != None and iccid_forai in line :
                                    self.infor.emit('开始整机功能测试')
                                    self.test_ctrl.set_rfcase_dir('/home/pi/production/case/production_case.txt')
                                    m  = self.test_ctrl.start_usb_test()
                                    if m == 0:
                                        with open('/home/pi/production/mid.txt','r') as a1:
                                            a1_ = a1.read()
                                        with open('/home/pi/production/product_log.txt','a') as a2:
                                            a2.write(a1_)
                                        os.system('sudo rm -rf /home/pi/production/mid.txt')
                                        self.infor.emit('通过数量加1')
                                        #self.test_ctrl.ftp_downloadfile()
                                        with open('/home/pi/production/res_hardsoft/hard_soft.txt', 'a') as f:
                                            f.write('\n'+iccid_forai + '\n')
                                        os.system('sudo chmod 777 /home/pi/production/res_hardsoft/hard_soft.txt')
                                    else:
                                        os.system('sudo rm -rf /home/pi/production/mid.txt')
                                        #self.test_ctrl.ftp_upload()
                                    # if m ==0:
                                    #     self.test_ctrl.set_rfcase_dir('/home/pi/production/case/setid_case.txt')
                                    #     n = self.test_ctrl.start_usb_test()
                                    break
                        with open('/home/pi/production/res_hardsoft/hardware_res.txt','r')as fff:
                            file_all = fff.read()
                            #self.infor.emit(file_all)
                            if file_all.find(iccid_forai)==-1:
                                #self.infor.emit('1111')
                                self.infor.emit('整机功能测试失败本机ICCID为{}读取文件失败'.format(iccid_forai))
                                os.system('sudo rm -rf /home/pi/production/mid.txt')

                except :
                    #self.infor.emit('111')
                    self.infor.emit('整机功能测试失败,未找到iccid:{}对应的设备'.format(iccid_forai))
                    os.system('sudo rm -rf /home/pi/production/mid.txt')

class AsFlashloader2(AsFlashloader):
    infor = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        super(QThread, self).__init__(parent)
        self.app = None
        self.comb_rreport = CombinationReport()
        self.test_ctrl = TestControl(self.infor)

    def setTarget(self, testType):
        self.testType = testType

    def run(self):
        #global RUN_FLAG

        #RUN_FLAG = False
        TestControl.led_test_flag = True


class AsFlashloader3(AsFlashloader2):
    infor = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        super(QThread, self).__init__(parent)
        self.app = None
        self.comb_rreport = CombinationReport()
        self.test_ctrl = TestControl(self.infor)

    def setTarget(self, testType):
        self.testType = testType

    def run(self):
        self.infor.emit('生成报告')
        output = self.test_ctrl.output_xlwt()
        self.infor.emit(output)
class AsFlashloader4(AsFlashloader):
    infor = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        super(QThread, self).__init__(parent)
        self.app = None
        self.comb_rreport = CombinationReport()
        self.test_ctrl = TestControl(self.infor)

    def setTarget(self, testType):
        self.testType = testType

    def run(self):
        ceshires = self.test_ctrl.judge_num(self.pass_num)
        self.test_ctrl.hardware_signal(ceshires)

class AsStepEnable(QCheckBox):
    enableChanged=QtCore.pyqtSignal(str,bool)
    def __init__(self,text,parent=None):
        super(QCheckBox, self).__init__(text,parent)
        self.stateChanged.connect(self.on_stateChanged)
    def on_stateChanged(self,state):
        self.enableChanged.emit(self.text(),state)
        

class UIFlashloader(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)

        self.loader = AsFlashloader()
        self.loader.infor.connect(self.on_loader_infor)
        self.loader2 = AsFlashloader2()
        self.loader2.infor.connect(self.on_loader_infor)
        self.loader3 = AsFlashloader3()
        self.loader3.infor.connect(self.on_loader_infor)
        self.loader4 = AsFlashloader4()
        self.loader4.infor.connect(self.on_loader_infor)

        self.test_ctrl = TestControl()
        self.test_ctrl.build_report_log()  
        
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)

        # get grid to vbox
        grid = QGridLayout()
        #self.leApplication = QLineEdit()
        self.pass_num = 0
        self.count = pid_start
        self.testType = QComboBox()
        #self.testType.addItems(['主板：ECM&以太网&按键&LED', '整机：ECM&AI-box自检测试&按键&LED', '按键检测&LED', '主板功能', '以太网检测', 'AI-box自检测试','整机功能'])
        self.testType.addItems([ '主板功能测试','整机功能测试', 'AI-box自检测试-序列号设置','质检测试' ])
        self.btnStart1 = QPushButton('开始测试')
        self.btnStart2 = QPushButton('确认按键')
        self.btnStart2.setEnabled(True)
        self.res = QLabel('未测试')
        self.res.setFont(font)
        self.res.setAlignment(Qt.AlignCenter)
        self.res.setStyleSheet('background-color: rgb(255, 255, 255)')
        self.status = QLabel('空闲')
        self.status.setFont(font)
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet('background-color: rgb(255, 255, 255)')
        self.pass_num_display = QLabel('通过数量： {}'.format(self.pass_num))
        self.pass_num_display.setFont(font)
        self.pass_num_display.setAlignment(Qt.AlignCenter)
        self.pass_num_display.setStyleSheet('background-color: rgb(255, 255, 255)')

        grid.addWidget(QLabel('测试类型:'), 0, 0)
        grid.addWidget(self.testType, 0, 1)
        grid.addWidget(self.btnStart1, 0, 2)
        grid.addWidget(self.btnStart2, 0, 3)
        grid.addWidget(QLabel('测试结果:'), 1, 0)
        grid.addWidget(self.res, 1, 1)
        grid.addWidget(self.status, 1, 2)
        grid.addWidget(self.pass_num_display, 1, 3)

        # get hbox to vbox
        hbox = QHBoxLayout()
        vbox2 = QVBoxLayout()
        hbox.addLayout(vbox2)
        self.leinfor = QTextEdit()
        self.leinfor.setReadOnly(True)
        hbox.addWidget(self.leinfor)
        
        grid2 = QGridLayout()
        self.btnStart3 = QPushButton('生成报告')
        grid2.addWidget(self.btnStart3, 0, 0)

        grid3 = QGridLayout()
        self.btnStart4 = QPushButton('检验是否可以打码')
        grid3.addWidget(self.btnStart4, 0, 0)

        # add hbox and grid to vbox
        vbox = QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addLayout(hbox)
        vbox.addLayout(grid2)
        #vbox.addLayout(grid3)

        self.setLayout(vbox)
        
        #os.system('sudo ip link set can0 down')
        #os.system('sudo ip link set can1 down')
        os.system('sudo sh /home/pi/hlrfw/scripts/disable_platform.sh')
        os.system('sudo python3.7 /home/pi/hlrfw/scripts/serial_handle.py &')

        self.btnStart1.clicked.connect(self.on_btnStart_clicked)
        self.btnStart2.clicked.connect(self.on_btnStart2_clicked)
        self.btnStart3.clicked.connect(self.on_btnStart3_clicked)
        self.btnStart4.clicked.connect(self.on_btnStart4_clicked)

    def set_res(self, test_res):
        # 建议不要这个判断，直接根据在test_ctrl根据测试结果刷新图形界面
        global key_status_dict

        if test_res.find('主板功能测试') != -1:
            if test_res.find('开始主板功能测试') != -1:
                self.auto_load_display(key_status_dict['主板功能测试']['开始测试'])
            elif test_res.find('测试通过') != -1:
                self.auto_load_display(key_status_dict['主板功能测试']['测试通过'])
            elif test_res.find('测试失败') != -1:
                self.auto_load_display(key_status_dict['主板功能测试']['测试失败'])
        elif test_res.find('ACCE') != -1:
            if test_res.find('开始夹具测试') != -1:
                self.auto_load_display(key_status_dict['ACCE']['开始夹具测试'])
            elif test_res.find('开始方向测试') != -1:
                self.auto_load_display(key_status_dict['ACCE']['开始方向测试'])
            elif test_res.find('测试通过') != -1:
                self.auto_load_display(key_status_dict['ACCE']['测试通过'])
            elif test_res.find('测试失败') != -1:
                self.auto_load_display(key_status_dict['ACCE']['测试失败'])
        elif test_res.find('按键') != -1:
            if test_res.find('开始测试') != -1:
                self.auto_load_display(key_status_dict['按键']['开始测试'])
            elif test_res.find(',失败') != -1:
                self.auto_load_display(key_status_dict['按键']['按键测试失败'])
            elif test_res.find(',通过') != -1:
                self.auto_load_display(key_status_dict['按键']['按键测试通过'])
            elif test_res.find('按键1测试通过') != -1:
                self.auto_load_display(key_status_dict['按键']['按键1测试通过'])
            elif test_res.find('按键2测试通过') != -1:
                self.auto_load_display(key_status_dict['按键']['按键2测试通过'])
            elif test_res.find('按键3测试通过') != -1:
                self.auto_load_display(key_status_dict['按键']['按键3测试通过'])
            elif test_res.find('按键4测试通过') != -1:
                self.auto_load_display(key_status_dict['按键']['按键4测试通过'])
            elif test_res.find('按键1测试失败') != -1:
                self.auto_load_display(key_status_dict['按键']['按键1测试失败'])
            elif test_res.find('按键2测试失败') != -1:
                self.auto_load_display(key_status_dict['按键']['按键2测试失败'])
            elif test_res.find('按键3测试失败') != -1:
                self.auto_load_display(key_status_dict['按键']['按键3测试失败'])
            elif test_res.find('按键4测试失败') != -1:
                self.auto_load_display(key_status_dict['按键']['按键4测试失败'])
        elif test_res.find('LED') != -1:
            if test_res.find('开始测试') != -1:
                self.auto_load_display(key_status_dict['LED']['开始测试'])
            elif test_res.find('测试通过') != -1:
                self.auto_load_display(key_status_dict['LED']['测试通过'])
            elif test_res.find('测试失败') != -1:
                self.auto_load_display(key_status_dict['LED']['测试失败'])
        elif test_res.find('继电器') != -1:
            if test_res.find('开始测试') != -1:
                self.auto_load_display(key_status_dict['继电器']['开始测试'])
            elif test_res.find('测试通过') != -1:
                self.auto_load_display(key_status_dict['继电器']['测试通过'])
            elif test_res.find('测试失败') != -1:
                self.auto_load_display(key_status_dict['继电器']['测试失败'])
        elif test_res.find('AI-box自检测试-序列号设置') != -1:
            if test_res.find('开始AI-box自检测试-序列号设置测试') != -1:
                self.auto_load_display(key_status_dict['AI-box自检测试-序列号设置']['开始测试'])
            elif test_res.find('测试通过') != -1:
                self.auto_load_display(key_status_dict['AI-box自检测试-序列号设置']['测试通过'])
            elif test_res.find('测试失败') != -1:
                self.auto_load_display(key_status_dict['AI-box自检测试-序列号设置']['测试失败'])
        elif test_res.find('质检测试') != -1:
            if test_res.find('开始测试') != -1:
                self.auto_load_display(key_status_dict['质检测试']['开始测试'])
            elif test_res.find('测试通过') != -1:
                self.auto_load_display(key_status_dict['质检测试']['测试通过'])
            elif test_res.find('测试失败') != -1:
                self.auto_load_display(key_status_dict['质检测试']['测试失败'])
        elif test_res.find('整机功能测试') != -1:
            if test_res.find('开始整机功能测试') != -1:
                self.auto_load_display(key_status_dict['整机功能测试']['开始测试'])
            elif test_res.find('测试通过') != -1:
                self.auto_load_display(key_status_dict['整机功能测试']['测试通过'])
            elif test_res.find('测试失败') != -1:
                self.auto_load_display(key_status_dict['整机功能测试']['测试失败'])
        elif test_res.find('获取dev_id失败') != -1:
            self.auto_load_display(key_status_dict['获取dev id失败']['测试失败'])
        elif test_res.find('通过数量加1') != -1:
            self.pass_num_add()

    def auto_load_display(self, display):
        self.btnStart1.setEnabled(display[0])
        #self.btnStart2.setEnabled(display[1])
        self.btnStart3.setEnabled(display[2])
        self.res.setText(display[3])
        if display[3].find('检测通过PID为') != -1:
            self.count = self.pid_up(self.count)
            display[3] = '检测通过PID为:'+self.count
        if display[4]:
            self.res.setStyleSheet(display[4])
        self.status.setText(display[5])
        if display[6]:
            self.status.setStyleSheet(display[4])
        if display[7]:
            self.pass_num += 1
            self.pass_num_display.setText('通过数量： {}'.format(self.pass_num))

    def pid_up(self,str_):
        '''
        功能:PID比较并写入配置文件
        参数:被设置的PID
        实例:pid_set|'6850001'
        '''
        pid_1 = str_[:3]
        pid_2 = int(str_[-4:])
        pid_2 += 1
        pid_2 = str(pid_2)
        while len(pid_2)<4:
            pid_2 = '0'+pid_2
        #with open('/home/pi/production/ID_param.py','a') as f:
            #f.write('\n'+'pid_start = '+ '\''+pid_1+pid_2+'\''+'\n')
        return (pid_1+pid_2)
    
    def pass_num_add(self):
        self.pass_num += 1
        self.pass_num_display.setText('通过数量： {}'.format(self.pass_num))

    def set_status(self, text):
        self.status.setText(text)

    def recover_button(self):
        self.btnStart1.setEnabled(True)
        #self.btnStart2.setEnabled(True)

    def on_cmbxProtocol_currentIndexChanged(self,index):
        self.loader.set_protocol(str(self.cmbxProtocol.currentText()))

        for id,s in enumerate(self.loader.GetSteps()):
            self.cbxEnableList[id].setText(s[0])
            self.cbxEnableList[id].setChecked(s[1])

    def on_loader_infor(self,text):
        #self.test_ctrl.save_log_file(text)
        self.set_res(text)
        self.leinfor.append(text)

    def on_btnStart_clicked(self):
        # global RUN_FLAG

        # RUN_FLAG = True
        #self.loader.setTarget(str(self.leApplication.text()),str(self.testType.currentText()),)
        self.btnStart1.setEnabled(False)
        self.loader.setTarget(str(self.testType.currentText()))
        self.loader.start()

    def on_btnStart2_clicked(self):
        # global RUN_FLAG

        # RUN_FLAG = False
        #self.loader2.setTarget(str(self.leApplication.text()),str(self.testType.currentText()),)
        #self.loader2.setTarget(str(self.testType.currentText()))
        self.loader2.start()

    def on_btnStart3_clicked(self):
        global RUN_FLAG

        RUN_FLAG = False
        # self.loader2.setTarget(str(self.leApplication.text()),str(self.testType.currentText()),)

        self.loader3.setTarget(str(self.testType.currentText()),)
        self.loader3.start()
        # self.btnStart1.setEnabled(False)
        # self.btnStart2.setEnabled(False)
        # self.btnStart3.setEnabled(False)

    def on_btnStart4_clicked(self):
        global RUN_FLAG

        RUN_FLAG = False
        self.loader4.setTarget(str(self.testType.currentText()), )
        self.loader4.start()

