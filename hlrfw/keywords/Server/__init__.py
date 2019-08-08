# -*- coding: utf-8 -*-
#Server keyword
import sys
if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')
    
import os
import time
import socket

from hlrfw.database.MyDatabase import MyDatabase
from hlrfw.configs.ip_config import PORT_DICT,SERVER_TO_TER_IP,IP
from hlrfw.configs.order_config import ORDER_DICT
from hlrfw.configs.db_config import SELECT_SQL_DICT
from hlrfw.configs.sys_config import EQUIPMENT_ID_DICT,EQUIPMENT_TOKEN_DICT

from robot.api import logger
from robot.utils import asserts
from robot.version import get_version

REMOTE_CONTROL_DOMAIN_DICT = {
    '企标平台': 'http://devprotocol.demo.cas-tian.com/',
    }
REMOTE_CONTROL_ROUTE_DICT = {
    '远程上电': 'downCmd?',
    '远程下电': 'downCmd?',
    '制冷1档': 'acControlDownCmd?',
    '制冷2档': 'acControlDownCmd?',
    '制冷3档': 'acControlDownCmd?',
    '关闭制冷': 'acControlDownCmd?',
    '制热1档': 'ptcControlDownCmd?',
    '制热2档': 'ptcControlDownCmd?',
    '制热3档': 'ptcControlDownCmd?',
    '关闭制热': 'ptcControlDownCmd?',
    '预约充电': 'chargingRemoteDownCmd?',
    '关闭预约': 'chargingRemoteDownCmd?',
    }
REMOTE_CONTROL_ORDER_DICT = {
    '远程上电': {'commandId': '133',},
    '远程下电': {'commandId': '134',},
    '制冷1档': {'acSwitch': '1', 'acSetType': '2', 'acValue': '0'},
    '制冷2档': {'acSwitch': '1', 'acSetType': '2', 'acValue': '1'},
    '制冷3档': {'acSwitch': '1', 'acSetType': '2', 'acValue': '2'},
    '关闭制冷': {'acSwitch': '2', 'acSetType': '2', 'acValue': '1'},
    '制热1档': {'remotePtcSwitch': '2', 'ptcSetType': '2', 'ptcValue': '0'},
    '制热2档': {'remotePtcSwitch': '2', 'ptcSetType': '2', 'ptcValue': '1'},
    '制热3档': {'remotePtcSwitch': '2', 'ptcSetType': '2', 'ptcValue': '2'},
    '关闭制热': {'remotePtcSwitch': '1', 'ptcSetType': '2', 'ptcValue': '1'},
    '预约充电': {'type': '2', 'beginTime': '2020-11-1%2019:35', 'endTime': '2020-11-1%2019:36'},
    '关闭预约': {'type': '0', 'beginTime': '2020-11-1%2019:35', 'endTime': '2020-11-1%2019:36'},
    }

#tool
def str_to_timestamp(str_time):
    '''
    将20180101010101类似的时间转化为对应的时间戳
    '''
    str_time = str(str_time)
    timeArray = time.strptime(str_time, '%Y%m%d%H%M%S')
    mytimestamp = int(time.mktime(timeArray))
    return mytimestamp

def hex_str_to_int(val):
    '''
    将终端的数据，转化为整型
    '''
    location = 0
    for i in range(len(val)):
        ret_val = ret_val + int('0x'+val[location:location+2],16)
        location = location + 2
    return ret_val

def get_data_day(start_time):
    return time.localtime(start_time).tm_mday

def _wait_for_login(start_time, wait_time, platform1, platform2, vin, init):
    '''
    确认终端登入和登出的信息
    成功动作返回True，失败返回Flase
    '''
    is_action = False
    start_time = str_to_timestamp(start_time) 
    wait_time = int(wait_time)
    select_sql1 = SELECT_SQL_DICT['wait_for_login'].format(platform1, start_time)
    if platform2:
        select_sql2 = SELECT_SQL_DICT['wait_for_login'].format(platform2, start_time)
    if vin:
        select_sql1 = select_sql1 + ' and client_msg_vin=\'{0}\''.format(vin)
    select_res1_flag = True
    select_res2_flag = True
    for i in range(wait_time):
        time.sleep(1)
        if select_res1_flag:
            select_res1 = self.mydatabase.select_all_data(select_sql1)
            if select_res1:
                print(platform1 + 'login platform in ' + str(select_res1[-1]['time_ter']))
                select_res1_flag = False
        if platform2:
            if select_res2_flag:
                select_res2 = self.mydatabase.select_all_data(select_sql2)
                if select_res2:
                    print(platform2 + 'login platform in ' + str(select_res2[-1]['time_ter']))
                    select_res2_flag = False
        else:
            select_res2_flag = False
        if not select_res1_flag and not select_res2_flag:
            is_action = True
            break
    if is_action and platform1=='gbtele':
        login_id = int(select_res1[0]['login_id'])
        login_time = int(select_res1[0]['time_ter'])
        if init and str(init) == '1':
            if login_id != 1:
                asserts.fail(unicode('登录流水号没有置0',encoding='utf-8'))
        else:
            sql = 'select time_ter,login_id from gb_car_login where time_pi < {} order by time_pi desc limit 1'.format(start_time)
            select_login_id_res = self.mydatabase.select_all_data(sql)
            if select_login_id_res:
                last_login_time = int(select_login_id_res[0]['time_ter'])
                last_login_id = int(select_login_id_res[0]['login_id'])
                login_day = int(get_data_day(login_time))
                last_login_day = int(get_data_day(last_login_time))
                if login_day == last_login_day:
                    if login_id - last_login_id != 1:
                        asserts.fail(unicode('登录流水号累加错误',encoding='utf-8'))
                elif login_id != 1:
                    asserts.fail(unicode('凌晨登录流水号置0错误',encoding='utf-8'))
    return is_action
    
def is_alarm(data, is_alarm_data):
    '''
    参数：数据库的实时上报数据
    功能：判断终端是否产生报警
    返回值：如果有报警数据，则返回包含产生报警的时间点的元组，如果没有报警数据就返回一个空的元组
    '''
    alarm_time = []                                 
    item_time_ter = ''                              
    for item in data:
        len_alarm = len(alarm_time) - 1
        if item['max_alarm_level_7'][0] == '3':
            item_time_ter = item['time_ter']
            if alarm_time == []:
                alarm_time.append(item_time_ter)
                continue
            item_alarm_time = alarm_time[len_alarm]
            if item_alarm_time == item_time_ter:
                continue
            interval_time = item_time_ter - item_alarm_time
            if interval_time < 0:
                alarm_time[len_alarm] = item_time_ter
            if interval_time > 30:
                alarm_time.append(item_time_ter)
            if is_alarm_data:
                if item['com_alarm_sign_7'] != '00000200':
                    asserts.fail('do not have alarm data')
    return alarm_time

def is_interval_time_normal(data, ter_actual_report_interval, alarm_time):
    '''
    参数：分析的数据，实时上报的正确时间间隔，报警产生的时间点
    功能：分析数据时间间隔是否正确
    返回值：报警数据条数，时间间隔错误的时间，终端时间和服务器时间差大于10秒的数据
    '''  
    ter_actual_report_interval = int(ter_actual_report_interval)
    interval_error_time = []
    all_interval_dict = []
    alarm_info_num = 0
    last_data_time = None
    server_interval_error = []
    for item in data:
        if float(item['time_interval']) > 10 and item['client_msg_id'] == '02':
            server_interval_error.append(item['time_ter'])
        item_ter_time = item['time_ter']
        if last_data_time == None:
            last_data_time = item_ter_time
            continue
        interval = item_ter_time - last_data_time
        if interval == ter_actual_report_interval:
            last_data_time = item_ter_time
            continue
        elif interval == 0:
            continue
        elif interval == 1:
            alarm_info_num = alarm_info_num + 1
            if item['max_alarm_level_7'][0] == '3':
                last_data_time = item_ter_time
                continue
            else:
                special_time = item_ter_time + 30
                sql = 'select * from gb_car_actual_msg where time_ter=\'{0}\''.format(special_time)
                special_data = self.mydatabase.select_last_data(sql)
                if special_data == None:
                    last_data_time = item_ter_time
                    continue
                elif special_data['max_alarm_level_7'][0] == '3':
                    last_data_time = item_ter_time
                    continue
        elif alarm_time != []:
            if item_ter_time + 30 == alarm_time[0]:
                last_data_time = item_ter_time
                continue
            else:
                pass
        last_data_time = item_ter_time
        interval_error_time.append((item_ter_time,interval))
    return alarm_info_num, interval_error_time, server_interval_error

def get_login_info(start_time, stop_time, vin_id):
    '''
    参数：查询的登入数据的开始时间,查询的登出数据的结束时间
    功能：查询登入数据
    返回值：错误的登入信息时间，所有的登入时间
    '''   
    error_select1_res = []
    last_item = None
    select1_sql = 'select * from gb_car_login where time_ter>\'{0}\' and time_ter<\'{1}\''.format(start_time, stop_time)
    select1_res = self.mydatabase.select_all_data(select1_sql)
    for item in select1_res:
        this_time = item['time_ter']
        this_login_id = int(item['login_id'])
        #第一条数据不做判断
        if last_item == None:
            last_item = item
        else:
            m_this_time = time.localtime(float(this_time))
            m_last_time = time.localtime(float(last_item['time_ter']))
            #判断前后两次登入是不是同一天,是同一天则判断流水号是否增1
            if m_this_time.tm_mday == m_last_time.tm_mday:
                if int(this_login_id) - int(last_item['login_id']) == 1:
                    pass
                else:
                    error_select1_res.append(this_time)
            elif this_login_id == 1:
                pass
            else:
                error_select1_res.append(this_time)
            last_item = item
    return select1_res,error_select1_res

def get_logout_info(start_time, stop_time):
    '''
    参数：查询的登出数据的开始时间,查询的登出数据的结束时间
    功能：查询登出数据
    返回值：错误的登出信息时间，所有的登出时间
    '''   
    error_select1_res = []
    select1_sql = 'select * from gb_car_logout where time_logout_car>\'{0}\' and time_logout_car<\'{1}\''.format(start_time, stop_time)
    select1_res = self.mydatabase.select_all_data(select1_sql)
    for item in select1_res:
        logout_time = item['time_logout_car']
        select2_sql = 'select * from gb_car_login where 1 and time_ter < {} order by time_ter desc limit 1'.format(logout_time)
        select2_res = self.mydatabase.select_last_data(select2_sql)
        if select2_res == None:
            continue
        if item['login_id'] == select2_res['login_id']:
            if item['client_msg_vin'] == select2_res['client_msg_vin']:
                continue
            else:
                pass
        else:
            pass
        error_select1_res.append(logout_time)
    if error_select1_res == []:
        error_select1_res = 'data normal'
    return error_select1_res,select1_res

def judge_alarm_data(data):
    '''
    参数：数据，正确的报警次数
    功能：判断报警数据是否正确，如果报警数据错误间隔条数不为59，或者没有报警数据，或者时间间隔错误就报错
    元素0：报警时间，元素1：时间间隔错误数据，元素2：上报02数据的时间错误，与服务器时间差10s以上
    '''
    err_info = ''
    if int(data[0]) != 59 and int(data[0]) != 60:
        err_info = err_info + 'alarm info num error \n'
    if data[1] != []:
        err_info = err_info + 'interval time error {0}\n'.format(data[1])
    if data[2] != []:
        err_info = err_info + 'terminal time is not accurate {0}\n'.format(data[2])
    if err_info != '':
        asserts.fail(err_info)
    
class Server(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def __init__(self):
        self.mydatabase = MyDatabase()
    
    def get_login_cycle(self, start_time=None, stop_time=None, platform='gbtele', **kwargs):
        '''
        功能：
        - 获取登入周期
        
        参数：
        - start_time : 开始时间
        - stop_time : 结束时间
        - platform : 选择平台, 可填：gbtele,sirun,zdmon,zdgbt2,sharengo
        - 返回 ： 得出的登入周期数组
        '''
        cycle_list = []
        start_time = str_to_timestamp(start_time)
        stop_time = str_to_timestamp(stop_time)
        select_sql = SELECT_SQL_DICT['get_login_cycle'].format(platform, start_time, stop_time)
        select_res = self.mydatabase.select_all_data(select_sql)
        try:
            login_times = len(select_res)
        except:
            asserts.fail('had not login')
        for i in range(login_times):
            if i < login_times-1:
                cycle_list.append((select_res[i]['time_ter'],select_res[i+1]['time_ter']))
            else:
                cycle_list.append((select_res[i]['time_ter'],stop_time))
        if cycle_list == []:
            cycle_list.append((start_time, stop_time))
        return cycle_list
    
    def select_data_from_actual(self, cycle_list, ter_actual_report_interval, is_alarm_data=None):
        '''
        功能:
        - 查询实时上报数据,同时判断报警数据是否正常(暂时只有国标)
        
        参数：
        - cycle_list : ``get_login_cycle``关键字返回值
        - ter_actual_report_interval : 实时上报间隔
        - is_alarm_data : 是否需要判断具体的报警数据, 默认不判断,填True就会判断
        - 返回值：报警时间，时间间隔为1的数据条数，时间间隔错误的数据时间
        '''
        ter_actual_report_interval = int(ter_actual_report_interval) / 1000
        try:
            for item in cycle_list:
                start_time = item[0]
                stop_time = item[1]
                select_sql  = SELECT_SQL_DICT['select_data_from_actual'].format(start_time, stop_time)
                last_time_data = self.mydatabase.select_all_data(select_sql)
                alarm_res = is_alarm(last_time_data, is_alarm_data)
                data_res = is_interval_time_normal(last_time_data, ter_actual_report_interval, alarm_res)
                if alarm_res == []:
                    asserts.fail('have not alarm data')
                    continue
                print('报警数据时间:',alarm_res)
                print('时间间隔为1的数据数:',data_res[0])
                print('时间间隔错误数据:',data_res[1])
                judge_alarm_data(data_res)
        except Exception as e:
            asserts.fail(e)

    def server_login_wait(self, start_time, wait_time, platform1='gbtele', platform2='', vin=None, init=0):
        '''
        功能：
        - 等待终端上线
        - 通过条件 : 终端在规定时间内上线
        
        参数：
        - start_time : 初始时间
        - wait_time : 等待时间
        - platform : 选择的平台, 可选的平台有：gb,sirun,zdmon,zdgbt2,sharengo
        '''
        self.wat_for_login_res = True
        try:
            res = _wait_for_login(start_time, wait_time, platform1, platform2, vin, init)
        except Exception as e:
            asserts.fail(e)
        if not res:
            self.wat_for_login_res = False
            asserts.fail('car is not login platform')
        
    def server_logout_wait(self, wait_time, platform='gbtele'):
        '''
        功能：
        - 等待终端登出
        - 通过条件 : 终端在规定时间内登出
        
        参数：
        - start_time : 初始时间
        - wait_time : 等待时间
        - platform : 选择的平台, 可选的平台有：gb,sirun,zdmon,zdgbt2,sharengo
        '''
        wait_time = int(wait_time)
        error_logout_time = None
        start_time = time.time() - 1
        stop_time = start_time + wait_time
        select_sql = SELECT_SQL_DICT['wait_for_logout'].format(platform, start_time)
        for i in range(wait_time):
            time.sleep(1)
            select_res = self.mydatabase.select_all_data(select_sql)
            if select_res:
                return select_res[-1]['login_id']
        else:
            asserts.fail('platform had not logout')
        
    def server_port_get(self, platform):
        '''
        功能：
        - 获取平台端口
        - 返回对应平台的端口
        
        参数：
        - platform : 选择的平台, 可选的平台有gbtele,jtt808,sirun,zdmon,sharengo,zdgbt2     
        '''
        return  PORT_DICT[platform]

    def server_order_get(self, platform):
        '''
        功能：
        - 获取设置终端链路的串口指令
        
        参数：
        - platform : 选择的平台, 可选的平台有gbtele,jtt808,sirun,zdmon,sharengo,zdgbt2     
    
        '''
        return ORDER_DICT[platform]
    
    def server_login_data_query(self, start_time, stop_time, vin_id):
        '''
        功能：
        - 查询登入数据
        
        参数：
        - start_time : 查询的登入数据的开始时间
        - stop_time : 查询的登入数据的结束时间
        - vin_id : 对应的终端VIN码
        - 返回值：错误的登入时间，所有的登入时间
        '''
        start_time = str_to_timestamp(start_time)
        stop_time  = str_to_timestamp(stop_time)
        login_time, error_login_time = get_login_info(start_time, stop_time, vin_id)
        print('车辆登入错误数据:', len(error_login_time), error_login_time)

    def server_logout_data_query(self, start_time, stop_time):
        '''
        功能：
        - 查询登出数据
        
        参数：
        - start_time : 查询的登出数据的开始时间
        - stop_time : 查询的登出数据的结束时间
        - 返回值：错误的登出时间，所有的登出时间
        '''
        start_time = str_to_timestamp(start_time)
        stop_time  = str_to_timestamp(stop_time)
        error_logout_time, logout_time = get_logout_info(start_time, stop_time)
        print('车辆登出错误数据:', error_logout_time)

    def server_data_send_ter(self, send_msg, platform='gbtele'):
        '''
        功能：
        - 发送数据到的终端,(如果填写close connection就会关闭平台链路)
        
        参数：
        - send_msg : 发送的数据
        - platform : 平台选择, gbtele
        '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(SERVER_TO_TER_IP[platform])
        sock.send(send_msg.encode())
        sock.close()
        return 1

    def server_login_or_not(self, start_time, stop_time, platform='gb'):
        '''
        功能：
        - 查询在这时间段内终端是否登录国标平台
        
        参数：
        - start_time : 开始时间
        - stop_time : 结束时间
        '''
        start_time = str_to_timestamp(start_time)
        stop_time = str_to_timestamp(stop_time)
        select_sql = SELECT_SQL_DICT['is_login_or_not'].format(platform, start_time, stop_time)
        select_res = self.mydatabase.select_all_data(select_sql)
        if select_res:
            print('login platfrom in ' + str(select_res[-1]['time_ter']))
        else:
            asserts.fail('car had not login platform during the time')

    def server_logout_or_not(self, start_time, stop_time, platform='gb'):
        '''
        功能：
        - 查询在这时间段内终端是否登出国标平台
        
        参数：
        - start_time : 开始时间
        - stop_time : 结束时间
        '''
        start_time = str_to_timestamp(start_time)
        stop_time = str_to_timestamp(stop_time)
        select_sql = SELECT_SQL_DICT['is_logout_or_not'].format(platform, start_time, stop_time)
        select_res = self.mydatabase.select_all_data(select_sql)
        if select_res:
            print('logout platform in ' + str(select_res[-1]['time_logout_car']))
        else:
            asserts.fail('car had not logout platform during the time')
        
    def server_actual_data_judge(self, start_time, stop_time, platform):
        '''
        功能：
        - 判断每条实时数据是否正确
        
        参数：
        - start_time : 开始时间
        - stop_time : 结束时间
        '''
        start_time = str_to_timestamp(start_time)
        stop_time = str_to_timestamp(stop_time)
        select_sql = SELECT_SQL_DICT['ser_judge_actual_data'].format(platform, start_time, stop_time)
        select_res = self.mydatabase.select_all_data(select_sql)
        for item in select_res:
            if int(item['test_res']) != 0:
                asserts.fail('error data:'+str(item['time_ter']))

    def server_actual_data_rf_analysis(slef, start_time, stop_time, platform='gbtele'):
        '''
        功能：
        - 判断实时数据变化趋势和结果是否正确
        
        参数：
        - start_time : 开始时间
        - stop_time : 结束时间
        '''
        start_time = str_to_timestamp(start_time)
        stop_time = str_to_timestamp(stop_time)
        select_sql = SELECT_SQL_DICT['rf_analysis_actual_data'].format(platform, start_time, stop_time)
        select_res = self.mydatabase.select_all_data(select_sql)
        start_id = 0
        num = 0
        for item in select_res:
            if hex_str_to_int(item['total_current_1']) < 1000:
                if start_id == 0:
                    start_id = i
                num = num + 1
            else:
                if num >=10:
                    for item in select_res[start_id:start_id+num]:
                        if item['charge_state'] != '02':
                            asserts.fail('charg state error:'+ str(item['time_ter']))
                        
        
 #   def calculate_date(self, start_time, stop_time, interval=5):
 #       '''
 #       参数：初始时间，累加的时间
 #       功能：计算时间的累加
 #       返回：累加后的时间
 #       不需要使用这个关键字
 #       '''
 #       start_timestamp = str_to_timestamp(start_time)
 #       stop_timestamp = str_to_timestamp(stop_time)
 #       true_interval = stop_timestamp - start_timestamp
 #       if true_interval > interval:
 #           asserts.fail('Failed: start:{0} interval:{1}'.format(start_time, true_interval))
 #       else:
 #           print('Pass: start:{0} interval:{1}'.format(start_time, true_interval))

    def server_pitime_to_hextime(self):
        '''
        功能：
        - 取系统时间转化成类似20180102030405
        - 在终端查询到的时间不准确的时候使用
        - 返回转化的时间
        '''
        now = int(time.time())
        timeArray = time.localtime(now)
        rt_date = time.strftime('%Y%m%d%H%M%S', timeArray)
        
        return rt_date
          
    def server_actual_msg_get_num(self, start_time, interval_time, msg_num=None, platform='gb'):
        '''
        功能：
        - 验证这时间段内的实时数据量是否正常(验证盲区数据的时候使用)

        参数：
        - start_time : 开始时间
        - stop_time : 结束时间
        - msg_num : 应得数据数量
        '''
        start_time = str_to_timestamp(start_time)
        interval_time = int(interval_time)
        stop_time = start_time + interval_time
        if interval_time > 0:
            select_sql = SELECT_SQL_DICT['get_actual_msg_num'].format(platform, start_time,stop_time)
        else:
            select_sql = get_actual_msg_num['get_actual_msg_num'].format(platform, stop_time, start_time)
        select_res = self.mydatabase.select_all_data(select_sql)
        if select_res:
            actual_msg_num = len(select_res)
            if msg_num:
                msg_num = int(msg_num)
                if actual_msg_num != msg_num:
                    asserts.fail('actual msg num error:'.format(msg_num))
            else:
                return actual_msg_num
        else:
            asserts.fail('do not have actual msg')

    def server_sleep_heartbeat_mon(self, start_time, stop_time, interval_time):
        '''
        功能：
        - 验证这时间段内心跳数据间隔是否正常

        参数：
        - start_time : 开始时间
        - stop_time : 结束时间
        - interval_time : 心跳数据间隔
        '''
        start_time = str_to_timestamp(start_time)
        stop_time = str_to_timestamp(stop_time)
        select_sql = SELECT_SQL_DICT['sleep_heartbeat'].format(start_time, stop_time)
        select_res = self.mydatabase.select_all_data(select_sql)
        if select_res:
            cur_time = 0
            for item in select_res:
                if cur_time == 0:
                    cur_time = item['time_pi']
                else:
                    myinterval = int(item['time_pi']) - int(cur_time)
                    if abs(myinterval - int(interval_time)) > 5:
                        print(item['time_pi'],cur_time)
                        print('interval time is ',myinterval)
                        asserts.fail('heartbeat error')
                    cur_time = item['time_pi']
        else:
            asserts.fail('don not had heartbeat data')
        print('heartbeat msg normal')

    def server_network_is_normal(self, platform):
        '''
        功能：
        - 验证网络状况是否正常
        - 验证平台状态是否正常

        参数：
        - platform : 可选的平台有：gb,sirun,zdmon,zdgbt2,sharengo
        '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            sock.connect((IP,PORT_DICT[platform]))
            logger.info('platform is ok')
        except:
            asserts.fail('platform is GG')

        try:
            sock.connect(('112.17.120.37',PORT_DICT[platform]))
            logger.info('network is ok')
        except:
            asserts.fail('network is GG')


    def update_thingsboard_status(self, key, value):
        '''
        功能：
        - 更新things board的属性值
        参数：
        - key：更新的键
        - value：键对应的值
        '''
        local_token = EQUIPMENT_TOKEN_DICT.get(EQUIPMENT_ID_DICT.get(self.get_local_ip()))
        if not local_token:
            asserts.faile('在things board,IP找不到对应的设备')
        order = "curl -v -X POST -d \"{\\\"" + str(key) + "\\\": \\\"" + str(value) + "\\\"}\" http://47.96.109.89:8080/api/v1/" + local_token +"/attributes --header 'Content-Type:application/json'"
        #print order
        #order = order.format(str(key), str(value), equipment_dict[str(equipment)])
        #print order
        res = os.system(order)
        
    def server_local_ip_acquire(self):
        '''
        功能：
        - 获取当前测试台的IP
        - 返回当前测试台的IP
        '''
        output = os.popen('hostname -I')
        for ip in output:
            return ip[-5:-2]
        
    def server_remote_control(self, order, platform='企标平台', vin='1234567890ABCDEFG'):
        '''
        功能：
        - 控制下发远程控制指令
        
        参数：
        - order: 发送的命令，可选项(远程上电,远程下电,制冷1档,制冷2档,制冷3档,关闭制冷,制热1档,制热2档,制热3档,关闭制热,预约充电,关闭预约充电)
        - platform: 平台
        - vin: vin码
        
        例子:
        | remote_control | 远程上电 | platform='企标平台' | vin='1234567890ABCDEFG' |
        '''
        domain = REMOTE_CONTROL_DOMAIN_DICT[platform] + REMOTE_CONTROL_ROUTE_DICT[order]
        myparam_dict = REMOTE_CONTROL_ORDER_DICT[order]
        myparam_list = ['vin=%s'%(vin)]
        for key in myparam_dict:
            myparam_list.append(key+'='+myparam_dict[key])
        exe_param = '&'.join(myparam_list)
        order = "curl -d \"%s\" \"%s\" &" % (exe_param, domain)
        os.system(order)
