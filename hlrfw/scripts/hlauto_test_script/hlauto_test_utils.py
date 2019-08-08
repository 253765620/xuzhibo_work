'''
- 用于筛选自动化测试的tag标签
'''
import sys,os
if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')
import hlauto.iconfig
from hlauto.iconfig import *
from hlrfw.utils.ding_notice.ding import AutoTestNoticeDing

class TestTagsChoice(object):
    
    @staticmethod
    def get_ignore_tag_list():
        # 需要筛选的标签
        config_tag_list = ['autosar','backups','cartt','eeprom','gbtele','geely','glmeth','gnss','hplead',
                            'iblue','iotend','irun_enable','jt808','jtt808','kandi','lzo','matrix','mbedtls',
                            'motion','mpond','mutual','native','osl','packet','pateo','phone','pkthub',
                            'plugin','property','record','remote','repose','sercom','setting','sharengo',
                            'shutdown','sirun','spiflash','statis','storage','suyun','sysdiag','sysheap',
                            'systime','target','update','watchdog','wwan','zdgbt','zdlease','zdmon','zotye']
        ignore_tag_list = []
        for item in dir(hlauto.iconfig):
            if item in ['__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__',]:
                continue
            tag_flag = eval(item)
            if tag_flag == 'n':
                tag = item[7:].lower()
                if tag in config_tag_list:
                    ignore_tag_list.append(tag)
        # 返回需要忽略的标签
        return ignore_tag_list
    
    @staticmethod
    def get_protoc():
        '''
        - 筛选平台协议，拿到需要使用的协议
        '''
        try:
            PROTOC_DICT = {
                'gbtele': CONFIG_GBTELE,
                'cartt': CONFIG_CARTT,
                'geely': CONFIG_GEELY,
                'glmeth': CONFIG_GLMETH,
                'iblue': CONFIG_IBLUE,
                'kandi': CONFIG_KANDI,
                #CONFIG_MUTUAL: 'mutual',
                'pateo': CONFIG_PATEO,
                'sharengo': CONFIG_SHARENGO,
                #CONFIG_SHGLEASE: 'shglease',
                'sirun': CONFIG_SIRUN,
                'suyun': CONFIG_SUYUN,
                'zdgbt2': CONFIG_ZDGBT2,
                'zdlease': CONFIG_ZDLEASE,
                'zdmon': CONFIG_ZDMON,
                'zotye': CONFIG_ZOTYE
                }
        except Exception as e:
            ding = AutoTestNoticeDing('text')
            ding.set_text_msg('protoc协议筛选出错啦:%s'%e)
            ding.send_to_ding()
        ret_protoc_list = []
        for tags in PROTOC_DICT:
            if PROTOC_DICT[tags] == 'y':
                ret_protoc_list.append(tags+'ANDlevel{0}ANDstableANDhlauto')
        ret_protoc = 'OR'.join(ret_protoc_list)
        # 如果没找到协议，就通知钉钉
        if not ret_protoc_list:
            ding = AutoTestNoticeDing('text')
            ding.set_text_msg('protoc协议筛选出错啦:%s'%e)
            ding.send_to_ding()
        return ret_protoc
