#!coding:utf-8
'''
- robotframework对外开放的功能，只需要实现你要的方法就行，具体使用可以参照robotframwork的说明书中的监控器
'''
import sys
if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')

import os
from hlrfw.configs.ip_config import IP
from hlrfw.configs.sys_config import DING_ADDR_2, USER_EMAIL_LIST
from hlrfw.utils.mail_notice.mail import AutoTestNoticeMail
from hlrfw.utils.ding_notice.ding import AutoTestNoticeDing
from hlauto.iwhole import *

class PythonListener(object):
    ROBOT_LISTENER_API_VERSION = 2
    
    def __init__(self):
        self.mail_notice = AutoTestNoticeMail()
        self.ding = AutoTestNoticeDing('text')
        self.report_dir = 'https://192.168.3.116:11601/iot_p23/branch_report/{}/{}/{}/'.format(imodel, branch, version)
        
    def start_suite(self, name, attrs):
        self._send_text_msg_to_ding(IP+', test suite start:'+attrs.get('longname'))
        
    def end_suite(self, name, attrs):
        self._send_text_msg_to_ding(IP+', test suite end:'+attrs.get('longname')+' '+attrs.get('status'))
       
    def start_test(self, name, attrs):
        pass
        
    def end_test(self, name, attrs):
        if attrs.get('status') == 'FAIL':
            self.mail_notice.set_receivers(self._choice_user_tag(attrs))
            self.mail_notice.set_message(self._attrs_msg(name, attrs))
            self.mail_notice.try_send_mail()
        
    def _attrs_msg(self, name, attrs):
        return('测试失败' + '\n' + self.report_dir + '\n' + '失败提示:' + '\n' + attrs.get('message') + '\n' + '测试用例位置:' + '\n' + IP + ': ' + attrs.get('longname'))            

    def _choice_user_tag(self, attrs):
        tag_list = attrs.get('tags')
        if tag_list:
            for tag in tag_list:
                if tag in USER_EMAIL_LIST:
                    return tag+'@hopelead.com'
        else:
            self._send_text_msg_to_ding(IP+', test suite tag is null:'+attrs.get('longname'))
        return 'chengui@hopelead.com'
            
    def _send_text_msg_to_ding(self, msg):
        self.ding.set_text_msg(msg)
        self.ding.send_to_ding()