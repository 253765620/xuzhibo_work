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

from test_ctrl import TestControl, CombinationReport
from hlrfw.keywords.NetTest.__init__ import NetTest

__all__ = ['UIFlashloader']
RUN_FLAG = True
# 状态位表示： 开始测试，按键测试，结束测试， 显示内容/样式， 显示内容/样式，显示的数字累加。None就是表示不做操作
key_status_dict = {
    'ECM': {'开始测试': [False, False, False, '等待结果', 'background-color: rgb(255, 255, 0)', '繁忙', None, None], 
            '测试通过': [True, False, True, 'ECMPASS', 'background-color: rgb(0, 255, 0)', '空闲', None, True],
            '测试失败': [True, False, True, 'ECMFail', 'background-color: rgb(255, 0, 0)', '空闲', None, None],},
    '按键': {'开始测试': [False, True, False, '按下4个按钮', 'background-color: rgb(255, 255, 0)', '查看信息提示结果', 'background-color: rgb(255, 255, 0)', None],
            '按键1测试通过': [False, True, True, '按键1PASS', 'background-color: rgb(0, 255, 0)', '请按下按键2', None, None],
            '按键1测试失败': [False, True, True, '按键1Fail', 'background-color: rgb(255, 0, 0)', '请按下按键2', None, None],
            '按键2测试通过': [False, True, True, '按键2PASS', 'background-color: rgb(0, 255, 0)', '请按下按键3', None, None],
            '按键2测试失败': [False, True, True, '按键2Fail', 'background-color: rgb(255, 0, 0)', '请按下按键3', None, None],
            '按键3测试通过': [False, True, True, '按键3PASS', 'background-color: rgb(0, 255, 0)', '请按下按键4', None, None],
            '按键3测试失败': [False, True, True, '按键3Fail', 'background-color: rgb(255, 0, 0)', '请按下按键4', None, None],
            '按键4测试通过': [True, False, True, '按键4PASS', 'background-color: rgb(0, 255, 0)', '按键测试结束', None, None],
            '按键4测试失败': [True, False, True, '按键4Fail', 'background-color: rgb(255, 0, 0)', '按键测试结束', None, None],
            '按键测试失败': [True, False, True, '按键测试Fail', 'background-color: rgb(255, 0, 0)', '按键测试结束', None, None],
            '按键测试通过': [True, False, True, '按键测试PASS', 'background-color: rgb(0, 255, 0)', '按键测试结束', None, None],
            },
    '以太网': {'开始测试': [False, False, False, '等待结果', 'background-color: rgb(255, 255, 0)', '繁忙', None, None], 
            '测试通过': [True, False, True, '以太网PASS', 'background-color: rgb(0, 255, 0)', '空闲', None, True],
            '测试失败': [True, False, True, '以太网Fail', 'background-color: rgb(255, 0, 0)', '空闲', None, None],},
    'AI-box自检测试': {'开始测试': [False, False, False, '等待结果', 'background-color: rgb(255, 255, 0)', '繁忙', None, None], 
            '测试通过': [True, False, True, 'AI-box自检PASS', 'background-color: rgb(0, 255, 0)', '空闲', None, True],
            '测试失败': [True, False, True, 'AI-box自检Fail', 'background-color: rgb(255, 0, 0)', '空闲', None, None],},
    '获取dev id失败': {'测试失败': [True, False, True, '获取dev id失败', 'background-color: rgb(255, 0, 0)', '空闲', None, None],}
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

    def get_usb_status(self):
        for i in range(300):
            dev_status = self.nettest.get_net_state('usb0')
            if dev_status == 1:
                self.test_ctrl.start_usb_test()
                return 1
            if dev_status == 0 and flag:
                self.infor.emit('检测到USB')
                flag = False
            sleep(0.1)
        return 0
    
    def run(self):
        test_type = self.testType
        flag = True
        if test_type == 'ECM&以太网&按键':
            self.infor.emit('开始测试ECM, 请插入USB ECM')
            dev_status = self.get_usb_status()
            if dev_status != 1:
                self.infor.emit('USB ECM测试失败, 没检测到USB ECM')
            else:
                self.test_ctrl.set_rfcase_dir('/home/pi/ProductionTool/nettest.txt')
                self.test_ctrl.start_usb_test()
            sleep(1)
            self.infor.emit('开始测试以太网')
            self.test_ctrl.set_rfcase_dir('/home/pi/ProductionTool/ethernet_test.txt')
            self.test_ctrl.start_usb_test()
            sleep(1)
            self.infor.emit('开始测试按键')
            self.test_ctrl.start_key_test()
        elif test_type == '以太网检测':
            self.infor.emit('开始测试以太网')
            self.test_ctrl.set_rfcase_dir('/home/pi/ProductionTool/ethernet_test.txt')
            self.test_ctrl.start_usb_test()
        elif test_type == 'USB ECM检测':
            self.infor.emit('开始测试ECM, 请插入USB ECM')
            dev_status = self.get_usb_status()
            if dev_status != 1:
                self.infor.emit('USB ECM测试失败, 没检测到USB ECM')
        elif test_type == '按键检测':
            self.infor.emit('开始测试按键')
            self.test_ctrl.start_key_test()
        elif test_type == 'AI-box自检测试':
            self.test_ctrl.set_rfcase_dir('/home/pi/ProductionTool/ai_test.txt')
            self.test_ctrl.start_usb_test()
    # def run(self):
    #     global RUN_FLAG

    #     flag = True
    #     self.infor.emit(self.testType+'\n')
    #     while RUN_FLAG:
    #         dev_status = self.nettest.get_net_state('usb0')
    #         if dev_status == 1 and RUN_FLAG:
    #             self.infor.emit('开始测试')
    #             self.test_ctrl.start_test(self.infor)
    #             self.retrigger_test()
    #             flag = True
    #         if dev_status == 0 and flag and RUN_FLAG:
    #             self.infor.emit('检测到USB')
    #             flag = False
    #         sleep(0.2)

    # def retrigger_test(self):
    #     global RUN_FLAG

    #     while RUN_FLAG:
    #         dev_status = self.nettest.get_net_state('usb0')
    #         if dev_status == -1:
    #             break
    #         sleep(0.1)


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
        TestControl.key_test_flag = True


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
        os.system('sudo ip link set can0 down')
        os.system('sudo ip link set can1 down')
        os.system('sudo sh /home/pi/hlrfw/scripts/disable_platform.sh')
        os.system('sudo python3.7 /home/pi/hlrfw/scripts/serial_handle.py &')

        self.loader = AsFlashloader()
        self.loader.infor.connect(self.on_loader_infor)
        self.loader2 = AsFlashloader2()
        self.loader2.infor.connect(self.on_loader_infor)
        self.loader3 = AsFlashloader3()
        self.loader3.infor.connect(self.on_loader_infor)

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
        self.testType = QComboBox()
        self.testType.addItems(['ECM&以太网&按键', 'USB ECM检测', '按键检测', '以太网检测', 'AI-box自检测试'])
        self.btnStart1 = QPushButton('开始测试')
        #self.btnStart2 = QPushButton('按键切换')
        #self.btnStart2.setEnabled(False)
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
        #grid.addWidget(self.btnStart2, 0, 3)
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

        # add hbox and grid to vbox
        vbox = QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addLayout(hbox)
        vbox.addLayout(grid2)

        self.setLayout(vbox)

        self.btnStart1.clicked.connect(self.on_btnStart_clicked)
        #self.btnStart2.clicked.connect(self.on_btnStart2_clicked)
        self.btnStart3.clicked.connect(self.on_btnStart3_clicked)

    def set_res(self, test_res):
        global key_status_dict

        if test_res.find('ECM') != -1:
            if test_res.find('开始测试') != -1:
                self.auto_load_display(key_status_dict['ECM']['开始测试'])
            elif test_res.find('测试通过') != -1:
                self.auto_load_display(key_status_dict['ECM']['测试通过'])
            elif test_res.find('测试失败') != -1:
                self.auto_load_display(key_status_dict['ECM']['测试失败'])
        elif test_res.find('按键') != -1:
            if test_res.find('开始测试') != -1:
                self.auto_load_display(key_status_dict['按键']['开始测试'])
            elif test_res.find(',失败') != -1:
                self.auto_load_display(key_status_dict['按键']['按键测试失败'])
            elif test_res.find(',通过') != -1:
                self.auto_load_display(key_status_dict['按键']['按键测试通过'])
            #elif test_res.find('按键1测试通过') != -1:
            #    self.auto_load_display(key_status_dict['按键']['按键1测试通过'])
            #elif test_res.find('按键2测试通过') != -1:
            #    self.auto_load_display(key_status_dict['按键']['按键2测试通过'])
            #elif test_res.find('按键3测试通过') != -1:
            #    self.auto_load_display(key_status_dict['按键']['按键3测试通过'])
            #elif test_res.find('按键4测试通过') != -1:
            #    self.auto_load_display(key_status_dict['按键']['按键4测试通过'])
            #elif test_res.find('按键1测试失败') != -1:
            #    self.auto_load_display(key_status_dict['按键']['按键1测试失败'])
            #elif test_res.find('按键2测试失败') != -1:
            #    self.auto_load_display(key_status_dict['按键']['按键2测试失败'])
            #elif test_res.find('按键3测试失败') != -1:
            #    self.auto_load_display(key_status_dict['按键']['按键3测试失败'])
            #elif test_res.find('按键4测试失败') != -1:
            #    self.auto_load_display(key_status_dict['按键']['按键4测试失败'])
        elif test_res.find('自检') != -1:
            if test_res.find('开始测试') != -1:
                self.auto_load_display(key_status_dict['AI-box自检测试']['开始测试'])
            elif test_res.find('测试通过') != -1:
                self.auto_load_display(key_status_dict['AI-box自检测试']['测试通过'])
            elif test_res.find('测试失败') != -1:
                self.auto_load_display(key_status_dict['AI-box自检测试']['测试失败'])
        elif test_res.find('以太网') != -1:
            if test_res.find('开始测试') != -1:
                self.auto_load_display(key_status_dict['以太网']['开始测试'])
            elif test_res.find('测试通过') != -1:
                self.auto_load_display(key_status_dict['以太网']['测试通过'])
            elif test_res.find('测试失败') != -1:
                self.auto_load_display(key_status_dict['以太网']['测试失败'])
        elif test_res.find('获取dev_id失败') != -1:
            self.auto_load_display(key_status_dict['获取dev id失败']['测试失败'])


    def auto_load_display(self, display):
        self.btnStart1.setEnabled(display[0])
        #self.btnStart2.setEnabled(display[1])
        self.btnStart3.setEnabled(display[2])
        self.res.setText(display[3])
        if display[4]:
            self.res.setStyleSheet(display[4])
        self.status.setText(display[5])
        if display[6]:
            self.status.setStyleSheet(display[4])
        if display[7]:
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
