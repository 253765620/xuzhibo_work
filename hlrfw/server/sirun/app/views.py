#!coding=utf8
import time
from shortcuts.template import render
from app.split import Split_msg
from app.split import PositionSplit
from app.split import TerminalAttributeSplit
from app.admin import ConvertBaseRegister

from app.datasave import datasave, get_sql_dict
from app.datasave import Split_msg_to_str
from configs.db_config import SIRUN_TABLE_DICT

from utils.tools import is_complete,display_sys_time,display_stamp_to_date
from utils.tools import to_md5_data,get_B11G_timestamp
from utils.tools import get_sys_time_list,change_tuple
from utils.check_code import check
from visual.visual_decorator import error

from database import MyDatabase
# You can write your logic here, and it's you place!
# You can do save & custom response message if you want!
# And you also can ignore all request just like the position view!

#global parameter
roll_num = (1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6)

#Tbox
def t_register(terminal_request):
    global roll_num
    peraeskey = terminal_request['client_ser_data'][:16]
    vin       = terminal_request['client_ser_data'][16:33]
    t_box_sn  = terminal_request['client_ser_data'][33:62]
    imsi      = terminal_request['client_ser_data'][62:77]
    rollnum   = terminal_request['client_ser_data'][77:93]
    iccid     = terminal_request['client_ser_data'][93:]
    msg_flag = terminal_request['client_msg_flag']
    event_creation_time = terminal_request['client_event_creation_time']
    dispatch_creation_time  = get_B11G_timestamp(terminal_request['client_dispatch_creation_time'])
    msg_counter = terminal_request['client_msg_conuter']
    ser_data_len = terminal_request['client_ser_data_len']
    sec_ver = terminal_request['client_sec_ver']
    
    bid = (0,0,0,10)
    #msg result
    terminal_request['client_result'] = (121,)
    md5_data = peraeskey + rollnum + roll_num
    #get callback num
    callbacknum = to_md5_data(md5_data)
    terminal_request['client_ser_data'] = (0,) + callbacknum + bid
    #data save
    sirun_register = {
            'bid'            : bid,
            'message_flag'   : msg_flag,
            'event_creation_time': event_creation_time,
            'dispatch_creation_time' : dispatch_creation_time,
            'message_counter' : msg_counter,
            'service_data_length': ser_data_len,
            'security_version' : sec_ver,
            'peraeskey'      : peraeskey,
            'vin'            : vin,
            't_box_sn'       : t_box_sn,
            'imsi'           : imsi,
            'roll_number'    : rollnum,
            'iccid'          : iccid,
            'callback_number': callbacknum,
            }
    datasave(terminal_request,sirun_register,SIRUN_TABLE_DICT['register'])
        
    #data check code
    terminal_request['client_ser_data_check'] = (check(terminal_request['client_ser_data']+(1,)),)
    #data length
    len_data = len(terminal_request['client_ser_data'])
    terminal_request['client_ser_data_len'] = (len_data/100, len_data%100)
    #msg mid
    terminal_request['client_mid'] = (2,)
    terminal_request['client_bid'] = bid
    template = 'client_fix_header|client_ser_data_check|client_ser_ver|client_bid|client_msg_flag|client_event_creation_time|client_aid|client_mid|client_msg_conuter|client_ser_data_len|client_result|client_sec_ver|client_dispatch_creation_time|client_ser_data'
    #return msg
    render(terminal_request, template)

def t_login(terminal_request):
    platrandom  = (48,51,67,51,55,66,57,50,51,55,50,68,52,48,57,52)
    mydatabase = MyDatabase.MyDatabase()
    select_sql = 'select * from sirun_register where 1 order by dispatch_creation_time desc limit 1'
    select_data = mydatabase.select_last_data(select_sql)
    
    #get data
    time_login_car = get_B11G_timestamp(terminal_request['client_dispatch_creation_time'])
    time_pi = (int(time.time()),)
    bid = terminal_request['client_bid']
    msg_flag = terminal_request['client_msg_flag']
    event_creation_time = terminal_request['client_event_creation_time']
    dispatch_creation_time = get_B11G_timestamp(terminal_request['client_dispatch_creation_time'])
    msg_counter = terminal_request['client_msg_conuter']
    ser_data_len = terminal_request['client_ser_data_len']
    sec_ver = terminal_request['client_sec_ver']
    
    if terminal_request['client_mid'] == (1,):
        keytype     = terminal_request['client_ser_data'][0:1]
        tboxsn      = terminal_request['client_ser_data'][1:30]
        vin         = terminal_request['client_ser_data'][30:47]
        tboxrandom  = terminal_request['client_ser_data'][47:]
        
        try:
            encryption_key = select_data['callback_number']
        except:
            error('you should register terminal')
        encryption_key = change_tuple(encryption_key)
        val = tboxrandom + encryption_key + platrandom
        md5_data = to_md5_data(val)
        terminal_request['client_ser_data'] = md5_data + platrandom
        terminal_request['client_mid'] = (2,)
        #save data
        sirun_car_login = {
            'time_ter': time_login_car,
            'time_pi' : time_pi,
            'bid'            : bid,
            'message_flag'   : msg_flag,
            'event_creation_time': event_creation_time,
            'dispatch_creation_time' : dispatch_creation_time,
            'message_counter' : msg_counter,
            'service_data_length': ser_data_len,
            'security_version' : sec_ver,
            'message_flag' : msg_flag,
            'key_type'      : keytype,
            't_box_sn'      : tboxsn,
            'vin'           : vin,
            't_box_random'  : tboxrandom,
            }
        datasave(terminal_request,sirun_car_login,SIRUN_TABLE_DICT['login'])
        
    if terminal_request['client_mid'] == (3,):
        serial_up = terminal_request['client_ser_data'][:16]
        acess_key = terminal_request['client_ser_data'][16:32]
        success_key = (0,0,0,0,0,0,0,0)
        terminal_request['client_ser_data'] = platrandom + (0,) + success_key + success_key + success_key
        terminal_request['client_mid'] = (5,)
        #save data
        sirun_car_login = {
            'time_ter': time_login_car,
            'time_pi': time_pi,
            'bid'            : bid,
            'message_flag'   : msg_flag,
            'event_creation_time': event_creation_time,
            'dispatch_creation_time' : dispatch_creation_time,
            'message_counter' : msg_counter,
            'service_data_length': ser_data_len,
            'security_version' : sec_ver,
            'message_flag' : msg_flag,
            'serial_up' : serial_up,
            'acess_key' : acess_key,
            }
        datasave(terminal_request,sirun_car_login,SIRUN_TABLE_DICT['login'])
    
    #get sys time
    terminal_request['client_dispatch_creation_time'] = get_sys_time_list()
    #data check code
    terminal_request['client_ser_data_check'] = (check(terminal_request['client_ser_data']+(1,)),)
    #data length
    len_data = len(terminal_request['client_ser_data'])
    terminal_request['client_ser_data_len'] = (len_data/100, len_data%100)
    #msg result
    terminal_request['client_result'] = (0,)
    template = 'client_fix_header|client_ser_data_check|client_ser_ver|client_bid|client_msg_flag|client_event_creation_time|client_aid|client_mid|client_msg_conuter|client_ser_data_len|client_result|client_sec_ver|client_dispatch_creation_time|client_ser_data'
    #####
    display_sys_time()
    display_stamp_to_date(time_login_car[0])
    
    #return msg
    render(terminal_request, template)

def t_logout(terminal_request):
    #get sys time
    terminal_request['client_dispatch_creation_time'] = get_sys_time_list()
    #data check code
    terminal_request['client_ser_data_check'] = (check(terminal_request['client_ser_data']+(1,)),)
    #data length
    len_data = len(terminal_request['client_ser_data'])
    terminal_request['client_ser_data_len'] = (0,0)

    #get_data
    time_logout_car = get_B11G_timestamp(terminal_request['client_dispatch_creation_time'])
    time_pi = (int(time.time()),)
    bid = terminal_request['client_bid']
    msg_flag = terminal_request['client_msg_flag']
    event_creation_time = terminal_request['client_event_creation_time']
    dispatch_creation_time = get_B11G_timestamp(terminal_request['client_dispatch_creation_time'])
    msg_counter = terminal_request['client_msg_conuter']
    ser_data_len = terminal_request['client_ser_data_len']
    sec_ver = terminal_request['client_sec_ver']
    #save data
    sirun_car_logout = {
        'time_logout_car': time_logout_car,
        'time_pi': time_pi,
        'bid'            : bid,
        'message_flag'   : msg_flag,
        'event_creation_time': event_creation_time,
        'dispatch_creation_time' : dispatch_creation_time,
        'message_counter' : msg_counter,
        'service_data_length': ser_data_len,
        'security_version' : sec_ver,
        'message_flag' : msg_flag,
        }
    datasave(terminal_request,sirun_car_logout,SIRUN_TABLE_DICT['logout'])
    #msg result
    terminal_request['client_result'] = (0,)
    terminal_request['client_mid']    = (2,)
    template = 'client_fix_header|client_ser_data_check|client_ser_ver|client_bid|client_msg_flag|client_event_creation_time|client_aid|client_mid|client_msg_conuter|client_ser_data_len|client_result|client_sec_ver|client_dispatch_creation_time|client_ser_data'
    render(terminal_request, template)

def t_relogin(terminal_request):
    print 't_relogin'

def t_keep_active(terminal_request):
    #change client mid
    terminal_request['client_mid'] = (2,)
    #get sys time
    terminal_request['client_dispatch_creation_time'] = get_sys_time_list()
    #data check code
    terminal_request['client_ser_data_check'] = (check(terminal_request['client_ser_data']+(1,)),)
    #data length
    len_data = len(terminal_request['client_ser_data'])
    terminal_request['client_ser_data_len'] = (0,0)
    #msg result
    terminal_request['client_result'] = (0,)
    template = 'client_fix_header|client_ser_data_check|client_ser_ver|client_bid|client_msg_flag|client_event_creation_time|client_aid|client_mid|client_msg_conuter|client_ser_data_len|client_result|client_sec_ver|client_dispatch_creation_time|client_ser_data'
    render(terminal_request, template)

def t_err_rep(terminal_request):
    content = terminal_request['client_ser_data']
    if len(content) > 6:
        pass
    else:
        ems = 1
    

    
def t_actual_msg_rep(terminal_request):
    print terminal_request
    #deal with data
    if terminal_request['client_mid'] == (1,):
        terminal_request['client_mid'] == (2,)
        terminal_request['client_ser_data'] = ()
        terminal_request['client_ser_data_len'] = (0,0)
    if terminal_request['client_mid'] == (4,):
        terminal_request['client_mid'] = (3,)
        time_ter = get_B11G_timestamp(terminal_request['client_dispatch_creation_time'])
        time_pi = (int(time.time()),)
        version_id = terminal_request['client_ser_data'][0:4]
        fixtime    = terminal_request['client_ser_data'][4:8]
        position   = terminal_request['client_ser_data'][8:21]
        car_status = terminal_request['client_ser_data'][21:29]
        car_data   = terminal_request['client_ser_data'][29:]
        sirun_actual_msg_dict = {
            'time_ter' : time_ter,
            'time_pi' : time_pi,
            'version_id': version_id,
            'fixtime'   : fixtime,
            'position'  : position,
            'car_status': car_status,
            'car_data'  : car_data,
            }
        datasave(terminal_request,sirun_actual_msg_dict,SIRUN_TABLE_DICT['actual_msg'])
    #get sys time
    terminal_request['client_dispatch_creation_time'] = get_sys_time_list()
    #data check code
    terminal_request['client_ser_data_check'] = (check(terminal_request['client_ser_data']+(1,)),)
    #msg result
    terminal_request['client_result'] = (0,)
    template = 'client_fix_header|client_ser_data_check|client_ser_ver|client_bid|client_msg_flag|client_event_creation_time|client_aid|client_mid|client_msg_conuter|client_ser_data_len|client_result|client_sec_ver|client_dispatch_creation_time|client_ser_data'
    render(terminal_request, template)
def t_E_call(terminal_request):
    print 'e_call'
    
def t_UBI_rep(terminal_request):
    print 'UBI'

def t_update(terminal_request):
    print 'update!!!!'

###tools




if __name__ == '__main__':
    """
    The below sample dicts just for test the register!
    """
    request = {'msg_id': (1, 2), 'msg_attr': (0, 2), 'dev_id': (153, 17, 152, 64, 130, 104), 't_product': (0, 1),
               'content': (81, 82), 'crc': (185,)}
    example = auth(request)
    print 'example      :', example
