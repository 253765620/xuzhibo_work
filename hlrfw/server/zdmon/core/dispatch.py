"""
According the message id,this function will dispatch each to
it destination!
"""
import re
import time

from shortcuts.template import render
from conf.protocols import MSG_ID   # A Global Dicts
from app.urls import urlpatterns
from core.split import SplitBase
from visual.visual_decorator import error, warning, info
from conf.rest import SOCKET_DESCRIPTOR  # A Global Dicts
from configs.sys_config import SERVER_LOG_FILE_ZDMON

try:
    import tongue
except ImportError, msg:
    error(msg)
    info_msg = "Run 'pip install tongue' will fix this!"

"""
urlpatterns is a function Dicts,and it will automatic looking
for the target function according your menu_key is !
"""

##
f = open(SERVER_LOG_FILE_ZDMON, 'a')

def reflect(flag, request):
    """
    By checking the flag of urlpatterns Dicts,and then
    reflect will do something for next!
    :param flag:
    :param request:
    :return: a data for send to terminal!
    """
    return urlpatterns[flag](request)


class MainSplit(SplitBase):
    # override the parent attribute
    prefix = 'client_'
    crc_check = True
    split_list = ['head_tag/2', 'msg_id/1', 'msg_response/1', 'msg_iccid/17',
                  'msg_encryption/1', 'msg_attr/2',
                  'msg_content/24~-1','crc/1'
                  ]


class Dispatch:
    """
    According the JTT808 protocol, and what we should do
    depend on message id! so, if you want to know what current
    message id mean! you should ask the protocol!
    """

    def __init__(self, request, conn, protocol=MSG_ID):
        global f
        receiver = request.encode('hex')
        print 'rec_msg:'+receiver
        f.write(receiver+'\n')
        self.protocol = protocol
        self.request = request
        self.conn = conn
        self.request_data = None
        self.client_tuple_data = None
        self.hex_format_data = None
        self.split_instance = None
        self.msg_key = None
        self.menu_key = None  # Just a key of urlpatterns Dicts
        self.request_dict = None
        self.PUB = True
        self.resolution()
        if self.PUB:
            self.distribute()
        else:
            error("Can't publish your data!")

    def resolution(self):
        """
        step1: Decode the binary data to a tuple
        step2: Split each element by the JTT808 protocol
        step3: Recognize the message id ,and then checking Dicts!
        something like {'(1,0)':'ter_reg_req'}
        :return: None
        """
        self.request_data = tongue.Decode(self.request)
        self.client_tuple_data = self.request_data.dst  # Don't forget get dst attribute
        if self.client_tuple_data[3] == 254:
            self.client_tuple_data = tuple(self.client_tuple_data)
            self.split_instance = MainSplit(self.client_tuple_data)
            self.request_dict = self.split_instance.result
            
            #Error request special processing
            if self.split_instance.flag:
                self.request_dict['client_msg_id'] = (9,)

            
            if self.split_instance.debug:
                self.request_dict['GET'] = self.conn
                self.msg_key = str(self.request_dict['client_msg_id'])
            else:
                warning('No Split instance !')
                self.PUB = False
        else:
            warning('Not a command package')
            self.PUB = False
            
    def distribute(self):
        """
        step1: checking if we have a key call self.msg_key
        step2: set a value to self.menu_key
        something maybe like self.menu_key='ter_reg_req'
        step3: if you have the key call 'ter_req_req'
        we need to keep ask which function can be available!
        step4: so,we need to ask the reflect function !
        :param : self.flag is a key of protocol Dicts!
        :param : self.conn is socket file desc
        :return:
        """

        # self.msg_key like '(1,2)' so, it's tuple-like
        # and then,you self.menu_key will set 'ter_aut_req'

        if self.msg_key in self.protocol:
            self.menu_key = self.protocol[self.msg_key]
            reflect(self.menu_key, self.request_dict)
            return True

        else:
            return None


if __name__ == '__main__':
    # Test the Split class
    sample1 = (126, 1, 0, 0, 2, 78, 56, 45, 34, 25, 78, 0, 1, 51, 52, 43, 126)
    result = MainSplit(sample1)
    print result.result
