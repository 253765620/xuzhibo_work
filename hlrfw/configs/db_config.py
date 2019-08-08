#!coding=utf8
'''
指定数据库的参数
'''

# mysql数据库参数
DB_TYPE = 'mysql+pymysql'
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'zhangroot'
DB_PORT = 3306
DB_NAME = 'hlrfw_test'


# 平台数据表名
GB_TABLE_DICT = {
    'login': 'gbtele_car_login',
    'logout': 'gbtele_car_logout',
    'actual_msg': 'gbtele_car_actual_msg',
    'heartbeat': 'gbtele_car_heartbeat',
    'ter_cor_time': 'gbtele_ter_cor_time',
    }

JTT808_TABLE_DICT = {
    'auth': 'jtt808_car_login',
    'logout': 'jtt808_car_logout',
    'actual_msg': 'jtt808_car_actual_msg',
    'heartbeat': 'jtt808_car_heartbeat',
    'ter_cor_time': 'jtt808_ter_cor_time',
    }

SIRUN_TABLE_DICT = {
    'register': 'sirun_register',
    'login': 'sirun_car_login',
    'logout': 'sirun_car_logout',
    'actual_msg': 'sirun_car_actual_msg',
    'heart_beat': 'sirun_heart_beat',
    'ter_cor_time': 'sirun_ter_cor_time',
    }

ZDMON_TABLE_DICT = {
    'login': 'zdmon_car_login',
    'logout': 'zdmon_car_logout',
    'actual_msg': 'zdmon_car_actual_msg',
    'heart_beat': 'zdmon_heart_beat',
    'ter_cor_time': 'zdmon_ter_cor_time',
    }

ZDGBT2_TABLE_DICT = {
    'login': 'zdgbt2_car_login',
    'logout': 'zdgbt2_car_logout',
    'actual_msg': 'zdgbt2_car_actual_msg',
    'heart_beat': 'zdgbt2_heart_beat',
    'ter_cor_time': 'zdgbt2_ter_cor_time',
    }

SHARENGO_TABLE_DICT = {
    'login': 'sharengo_car_login',
    'logout': 'sharengo_car_logout',
    'actual_msg': 'sharengo_car_actual_msg',
    'heart_beat': 'sharengo_heart_beat',
    'ter_cor_time': 'sharengo_ter_cor_time',
    }

# 获取实时数据 sql 查询语句
SELECT_SQL_DICT = {
    'get_actual_msg_num': 'select * form {}_car_actual_msg where time_ter>{} and time_ter<{}',
    'wait_for_logout': 'select * from {}_car_logout where time_pi > {}',
    'wait_for_login': 'select * from {}_car_login where time_pi > {}',
    'rf_analysis_actual_data': 'select * from {}_car_actual_msg wheree time_ter>{} and time_ter<{}',
    'ser_judge_actual_data': 'select time_ter,test_res from {}_car_actual_msg where time_ter>{} and time_ter<{}',
    'is_logout_or_not': 'select * from {}_car_logout where time_ter>{} and time_ter<{}',
    'is_login_or_not': 'select * from {}_car_login where time_pi>{} and time_pi<{}',
    'select_data_from_actual': 'select time_interval,time_ter,client_msg_id,max_alarm_level_7 from gbtele_car_actual_msg where time_ter > \'{}\' and time_ter < \'{}\' order by time_ter',
    'get_login_cycle': 'select * from {}_car_login where {}<time_ter and time_ter<{}',
    'sleep_heartbeat': 'select time_pi from gbtele_heart_beat where time_pi>{} and time_pi<{}'
    }