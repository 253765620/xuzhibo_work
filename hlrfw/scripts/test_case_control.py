#!coding:utf-8
'''
功能:
- 控制自动化触发的测试用例程序
- 会根据传入的参数，触发手动测试模式，或者是自动测试模式
'''
import os
import sys
import time
import datetime
if 'home/pi' not in sys.path:
    sys.path.append('/home/pi')
    
from hlauto.iwhole import *
from upload_test_report import upload_test_report
from hlrfw.configs.ip_config import myip
from hlrfw.configs.sys_config import DING_ADDR, DING_ADDR_2
from hlrfw.scripts.hlauto_test_script.hlauto_test_utils import TestTagsChoice
from hlauto.iwhole import branch, iclass, igenus
from hlrfw.utils.ding_notice.ding import AutoTestNoticeDing

class TestLevelChoice(object):
    def __init__(self, ignore_tag):
        self.status = None
        self.test_case_level = 0
        self.ignore_tag = ignore_tag
        self.pre_test_case_order = 'pybot --listener PythonListener -d /home/pi/ -P /home/pi/hlrfw/keywords/ --variablefile /home/pi/hlauto/hlauto.py --variablefile {6} -i level{0}ANDstableANDhlautoAND{1}ORsystemANDlevel{0}ANDstableANDhlautoOR{2}OR{3}ANDlevel{0}ANDstableANDhlautoOR{4}ANDlevel{0}ANDstableANDhlautoORautosarANDlevel{0}ANDstableANDhlauto {5} /home/pi/rfcase/'
        self.get_test_case_ignore_tag()
        self.ding = AutoTestNoticeDing('text')
        self.protoc = TestTagsChoice.get_protoc()
        
    def get_test_case_level(self):
        self.test_case_level = self.test_case_level + 1
    
    def get_test_case_ignore_tag(self):
        '''
        - 把需要忽略的tag和执行pybot的命令组合
        '''
        if self.ignore_tag:
            self.ignore_tag = '-e ' + 'OR'.join(self.ignore_tag)
        else:
            self.ignore_tag = ''

    def get_test_case_order(self):
        protoc = self.protoc.format(self.test_case_level)
        self.test_case_order = self.pre_test_case_order.format(self.test_case_level, branch, protoc, iclass, igenus, self.ignore_tag, self.param_file)
        self.send_msg_to_CZG(self.test_case_order)
        
    def send_msg_to_CZG(self, msg):
        '''
        - 给CZG这个群发送消息
        '''
        self.ding.set_text_msg(str(myip)+': '+msg)
        self.ding.send_to_ding()

class TestCaseProcess(TestLevelChoice):
    def __init__(self, ignore_tag, test_type, param_file):
        '''
        param:
        - ignore_tag: 需要忽略的tag数组
        - test_type: informal 非正式 formal 正式
        '''
        self.param_file = param_file
        super(TestCaseProcess,self).__init__(ignore_tag)
        # 在测试开始的时候就根据时间来固定本地要存储的报告的路径
        self.report_dir = '/home/pi/hllocalreport/{}'.format(str(datetime.datetime.now()).replace(' ','_')[:-7])
        self._set_test_type(test_type)
    
    def _set_test_type(self, test_type):
        '''
        - 根据测试的类型，决定测试结果发送到哪个钉钉群
        '''
        if test_type == 'formal':
            self.ding_addr = DING_ADDR
        else:
            self.ding_addr = DING_ADDR_2
    
    def start_level_test(self):
        self.get_test_case_level()
        self.get_test_case_order()
        self.test_status = os.system(self.test_case_order)
        
    def ctrl_process(self,level_num):
        '''
        - 流程控制，执行level1到5的测试用例
        '''
        for item in range(level_num):
            self.delet_test_res_file()                                       # 删除之前的测试报告，之前出现多个测试执行，导致xml乱了的情况，建议后续开始新的测试之前先终止之前的pybot
            self.start_level_test()                                          # 开始测试
            if self.test_status in (0,):                                     # linux系统执行命令，没有错误一般返回的是0代表通过测试, (之前我遇到过一个os.system()打印太多文件，然后终止了的情况)
                access_addr = upload_test_report(item+1, self.report_dir)    # 上传报告到gitlab pages服务器
                self.send_to_ding(access_addr, True, item)                   # 发送消息到钉钉
            elif self.test_status in (64512,):                               # 不同的返回值代表了不同的错误类型,类型有其他的，没有发掘完
                access_addr = upload_test_report(item+1, self.report_dir)
                self.send_to_ding(access_addr, False, item)
            elif self.test_status in (256, 768, 3840):
                access_addr = upload_test_report(item+1, self.report_dir)
                self.send_to_ding(access_addr, False, item)
            else:
                access_addr = upload_test_report(item+1, self.report_dir)
                self.send_to_ding(access_addr, False, item)
            
    def send_to_ding(self, access_addr, test_res, level):
        status_msg_dict = {
            0 : 'PASS',
            256 : 'FAIL',
            768 : 'serial server connetion is not open',
            64512 : 'have no tag with %s'%(level+1),
            3840 : 'unknown error',
            }   # 定义不同的测试结果返回值，钉钉消息的内容
        
        # 三种不同结果对应的图片地址，会显示在钉钉消息上
        pass_pic_url = 'http://a1.qpic.cn/psb?/V11R5XyI22UBBC/CsxKr6Fru5y1eGAL1VbrQWCx2nSjFZd33Aoif9Jnqbs!/m/dFQBAAAAAAAA&ek=1&kp=1&pt=0&bo=2gDiAAAAAAADFwo!&tl=1&vuin=1002840029&tm=1542247200&sce=60-3-3&rf=newphoto&t=5'
        fail_pic_url = 'http://a4.qpic.cn/psb?/V11R5XyI22UBBC/fIa7R8Vub0HoA2Nnr8fPY7g9hYaWVTPsuWfNQJNaWCE!/m/dFMBAAAAAAAA&ek=1&kp=1&pt=0&bo=6ADeAAAAAAADFwQ!&tl=1&vuin=1002840029&tm=1542247200&sce=60-3-3&rf=newphoto&t=5'
        alarm_pic_url = 'http://m.qpic.cn/psb?/V11R5XyI22UBBC/fhRKCd75TowNVoQqabxIrdjGb05Ih4g92mtwrRzjAYA!/b/dMMAAAAAAAAA&bo=9AH0AQAAAAADByI!&rf=viewer_4'
        # 这个是访问report的地址
        messageUrl = access_addr
        # 下面就是组织curl命令，使用shell命令发出去
        status = status_msg_dict.get(self.test_status)
        if status:
            title = 'Level {} Test Result: {} PI:{}'.format(level+1, status, myip)
        else:
            title = 'Level {} Test Result: {}{} PI:{}'.format(level+1, 'unknown error code', self.test_status, myip)
        if self.test_status == 64512:
            picUrl = alarm_pic_url
        elif test_res:
            picUrl = pass_pic_url
        else:
            picUrl = fail_pic_url
        text = access_addr
        order = 'curl \'%s\' -H \'Content-Type: application/json\' -d \'{\"msgtype\": \"link\", \"link\": {\"messageUrl\": \"%s\", \"picUrl\": \"%s\",\"title\":\"%s\",\"text\":\"%s\", }}\''%(self.ding_addr,messageUrl,picUrl,title,text)
        os.system(order)
        
    def delet_test_res_file(self):
        '''
        - 删除报告文件
        '''
        os.system('rm -rf /home/pi/*.html')
        os.system('rm -rf /home/pi/output.xml')
            
if __name__ == '__main__':
    #获取外部变量是否为正式测试
    file_name, sys_arg, param_file = sys.argv
    ignore_tag = TestTagsChoice.get_ignore_tag_list()              # 遍历版本的参数文件（就是hlauto下的文件），确认需要过滤tag
    test_case_p = TestCaseProcess(ignore_tag, sys_arg, param_file)
    test_case_p.ctrl_process(5)
    