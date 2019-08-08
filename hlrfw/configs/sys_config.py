# -*- coding: utf-8 -*-
'''
指定系统文件的常量
'''

from .ip_config import myip
#from hlrfw.keywords.EXP import EXP
import time

#当前时间
SAVE_TIME = int(time.time())


# 系统日志目录
SYS_LOG_DIR = '/home/pi/Desktop/journal_log'
# 平台日志文件
SERVER_LOG_FILE_32960 = '{}/{}_server_data_gbtele.txt'.format(SYS_LOG_DIR,myip)
SERVER_LOG_FILE_JTT808 = '{}/{}_server_data_jtt808.txt'.format(SYS_LOG_DIR,myip)
SERVER_LOG_FILE_SIRUN = '{}/{}_server_data_sirun.txt'.format(SYS_LOG_DIR,myip)
SERVER_LOG_FILE_ZDMON = '{}/{}_server_data_zdmon.txt'.format(SYS_LOG_DIR,myip)
SERVER_LOG_FILE_SHARENGO = '{}/{}_server_data_sharengo.txt'.format(SYS_LOG_DIR,myip)
SERVER_LOG_FILE_ZDGBT2 = '{}/{}_server_data_zdgbt2.txt'.format(SYS_LOG_DIR,myip)
# 串口日志
SERIAL_LOG_USB0 = '{}/{}_serial_usb0_data.txt'.format(SYS_LOG_DIR,myip)

SERIAL_LOG_AMA0 = '{}/{}_serial_ama0_data_{}.txt'.format(SYS_LOG_DIR,myip,SAVE_TIME)
SERIAL_LOG_USB1 = '{}/{}_serial_usb1_data_{}.txt'.format(SYS_LOG_DIR,myip,SAVE_TIME)
SERIAL_LOG_USB2= '{}/{}_serial_usb2_data_{}.txt'.format(SYS_LOG_DIR,myip,SAVE_TIME)
SERIAL_LOG_USB3 = '{}/{}_serial_usb3_data_{}.txt'.format(SYS_LOG_DIR,myip,SAVE_TIME)
# serial choice 串口设备 
SERIAL_EQUIP = '/dev/USB0'

# dingding url DING_ADDR is hlauto , DING_ADDR_2 is myself
DING_ADDR = 'https://oapi.dingtalk.com/robot/send?access_token=24808c62402eb21fa6d512ab83695206df410475e83784e17d04a52954867393'
DING_ADDR_2 = 'https://oapi.dingtalk.com/robot/send?access_token=440a22ca6f3a28e05bc8f4eec4a4978e9e223b3e804d97b89b100eac176d9700'

# thingsboard 的token配置
EQUIPMENT_ID_DICT = {
    '120': '001',
    '121': '002',
    '122': '003',
    '123': '004',
    '124': '005',
    '125': '006',
    '126': '007',
    '127': '008',
    '128': '009',
    '129': '010',
    '130': '011',
    '131': '012',
    '132': '013',
    '133': '014',
    '134': '015',
    '135': '016',
    '136': '017',
    '137': '018',
    '138': '019',
    '139': '020',
    '181' : 'hlrmt001',
    '182' : 'hlrmt002',
    }

EQUIPMENT_TOKEN_DICT = {
    '001': 'lmomu1jQlUCiiWmiTbkg',
    '002': 'j5QbrsdW7GO683DuIVjH',
    '003': 'VioedR23iu7bisxq40zp',
    '004': '5SL94pioJ6wIXDlThBE0',
    '005': 'edXp0LETy28hvOwRihmy',
    '006': 'WHJcJKODGUi9GHnoTCiW',
    '007': 'wg4qxmVL6hbs5iD63G4A',
    '008': 'vV0iKytjP8PEbc3ECN0J',
    '009': 'XfCLh4tJ5oGuBlri6XNH',
    '010': 'DHQYwlhoL5WjvqyYP4bH',
    '011': 'vozDk7QBjc18Tl1fTS1c',
    '012': 'jvmizDobe3ge8H8C9bdC',
    '013': 'Uni1tveFcVriFFyCNYT2',
    '014': 'OyLo0GU0jdvJwDsYl77B',
    '015': '13YjxGURzktiTWaZbc1C',
    '016': 'G9za8c8xBFiEF90rgQQA',
    '017': 'ayIqCfMBujCPEyuV7TEp',
    '018': 'YTS7nYqGLcY79GMaA3NA',
    '019': 'AVd1fHVpYJzZXKqAPx3c',
    '020': 'ro2ErD5XohrsusvMPS7A',
    'hlrmt001' : 'TNlBtNWvJhHOq9mnVGXs',
    'hlrmt002' : 'h7ST1PoY9I7Wfk1yz6kX',
    }

#user email config
USER_EMAIL_LIST = [
    'pengliping',
    'xuzhibo',
    'xingyuanyuan',
    'zhoumeizhen',
    'xielianlian',
    'liutiantian',
    'chenglujian',
    'zhangxianyue',
    'huangkai',
    'liushuqi',
    'xiajiahui',
    'zhuhaoming',
    'zhangxue',
    'mahaoran',
    'xieanyue',
    'lilisha',
    ]
