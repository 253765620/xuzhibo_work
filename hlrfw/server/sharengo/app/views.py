#!coding=utf8
import time
from shortcuts.template import render
from app.split import Split_msg
from app.split import PositionSplit
from app.split import TerminalAttributeSplit
from app.admin import ConvertBaseRegister

#from app.models import PositionTable
#from app.models import session
#from app.models import Base, engine

#Base.metadata.create_all(engine)
from app.datasave import datasave, get_sql_dict
from app.datasave import Split_msg_to_str
from configs.db_config import SHARENGO_TABLE_DICT

from utils.tools import to_md5_data
from utils.tools import get_sys_localtime_tuple
from utils.tools import get_config_bin_str
from utils.tools import int_tuple_to_hex_str
from utils.check_code import check
from visual.visual_decorator import error

from database import MyDatabase
# You can write your logic here, and it's you place!
# You can do save & custom response message if you want!
# And you also can ignore all request just like the position view!
data_len_dict = {
            '0' : 14,
            '1' : 1,
            '2' : 2,
            '3' : 3,
            '4' : 99,
            '5' : 99,
            '6' : 99,
            '7' : 99,
            '8' : 99,
            '9' : 99,
            '10' : 99,
            '11' : 99,
            '12' : 1,
            '13' : 2,
            '14' : 99,
            '15' : 2,
            '16' : 1,
        }

def cur_rsp(val):
    msg_id = val['client_main_com'][0]
    content = val['client_content']
    if msg_id == 50:
        state = content[0]
        vip_id = content[1:5]
        config = content[5:9]
        car_state = content[9:13]
        alarm_state = content[13:17]
        timestamp = content[17:24]
        log_dict = {
            'state' : state,
            'vip_id' : vip_id,
            'config' : config,
            'car_state' : car_state,
            'alarm_state' : alarm_state,
            'timestamp' : timestamp,
        }
        #log the config data
        config_bin_str = get_config_bin_str(config)
        location = 24
        for i in range(17):
            a = 31 - i
            if config_bin_str[a] == '1':
                if i == 16:
                    mylen = 1 + content[location]
                else:
                    mylen = data_len_dict[str(i)]
                config_msg_tuple = content[location:location+mylen]
                #config_msg_hex_str = int_tuple_to_hex_str(config_msg_tuple)
                location = location + mylen
                log_dict[i] = config_msg_tuple
    if msg_id == 51:
        software_version = content[0:3]
        vin_len = content[3]
        cell_phone_num_len = content[4+vin_len]
        bluetooth_len = content[5+vin_len+cell_phone_num_len]
        bluetooth_mac_len = content[5+vin_len+cell_phone_num_len+bluetooth_len]
        if vin_len != 0:
            vin_id = content[4:4+vin_len]
        else:
            vin_id = ()
        if cell_phone_num_len != 0:
            cell_phone_num = content[4+vin_len:5+vin_len+cell_phone_num_len]
        else:
            cell_phone_num = ()
        if bluetooth_len != 0:
            bluetooth_name = content[5+vin_len+cell_phone_num_len:5+vin_len+cell_phone_num_len+bluetooth_len]
        else:
            bluetooth_name = ()
        if bluetooth_mac_len != 0:
            bluetooth_mac = content[5+vin_len+cell_phone_num_len+bluetooth_len:-1]
        else:
            buletooth_mac = ()
        lease_mode = content[-1]
        log_dict = {
            'software version' : software_version,
            'vin' : (vin_len,)+vin_id,
            'cell phone num' : (cell_phone_num_len,)+cell_phone_num,
            'bluetooth' : (bluetooth_len,)+bluetooth_name,
            'bluetooth_mac' : (bluetooth_mac_len,)+bluetooth_mac,
            'lease_mode' : lease_mode,
        }
    if msg_id == 52 or msg_id == 53:
        GPS_altitude = content[0:4]
        GPS_longitude = content[4:8]
        direction = content[8:10]
        elevation = content[10:12]
        GPS_speed = content[12:14]
        alarm_type = content[14]
        timestamp = content[15:22]
        log_dict = {
            'GPS_altitude' : GPS_altitude,
            'GPS_longitude' : GPS_longitude,
            'direction' : direction,
            'elevation' : elevation,
            'GPS_speed' : GPS_speed,
            'alarm_type' : alarm_type,
            'timestamp' : timestamp,
        }
    if msg_id != 36 and msg_id != 37:
        print log_dict

def actual_msg_report(terminal_request):
    template = 'client_msg_header|sys_com_rsp|sys_fixed_msg_attr3|client_sign|client_msg_id|client_main_com|sys_ok|err_code|sys_time|sys_inf_code'
    terminal_request['sys_time'] = get_sys_localtime_tuple()
    return render(terminal_request, template)
    
def load_car(terminal_request):
    #print terminal_request
    template = 'client_msg_header|sys_com_rsp|sys_fixed_msg_attr3|client_sign|client_msg_id|client_main_com|sys_ok|err_code|sys_time|sys_inf_code'
    terminal_request['sys_time'] = get_sys_localtime_tuple()
    time_login_car = (int(time.time()),)
    sharengo_login_dict = {
        'time_login_car' : time_login_car,
        'time_pi': (int(time.time()),),
        }
    datasave(terminal_request, sharengo_login_dict, sharengo_table_dict['login'])
    return render(terminal_request, template)

    
def err_rep(terminal_request):
    template = 'client_msg_header|sys_com_rsp|sys_fixed_msg_attr3|client_sign|client_msg_id|client_main_com|sys_ok|err_code|sys_time|sys_inf_code'
    terminal_request['sys_time'] = get_sys_localtime_tuple()
    return render(terminal_request, template)
    
def regular_err_rep(terminal_request):
    template = 'client_msg_header|sys_com_rsp|sys_fixed_msg_attr3|client_sign|client_msg_id|client_main_com|sys_ok|err_code|sys_time|sys_inf_code'
    terminal_request['sys_time'] = get_sys_localtime_tuple()
    return render(terminal_request, template)
    
def log(terminal_request):
    template = 'client_msg_header|sys_com_rsp|sys_fixed_msg_attr3|client_sign|client_msg_id|client_main_com|sys_ok|err_code|sys_time|sys_inf_code'
    terminal_request['sys_time'] = get_sys_localtime_tuple()
    return render(terminal_request, template)
    
def heart_beat(terminal_request):
    template = 'client_msg_header|sys_com_rsp|sys_fixed_msg_attr3|client_sign|client_msg_id|client_main_com|sys_ok|err_code|sys_time|sys_inf_code'
    terminal_request['sys_time'] = get_sys_localtime_tuple()
    return render(terminal_request, template)


if __name__ == '__main__':
    """
    The below sample dicts just for test the register!
    """
    request = {'msg_id': (1, 2), 'msg_attr': (0, 2), 'dev_id': (153, 17, 152, 64, 130, 104), 't_product': (0, 1),
               'content': (81, 82), 'crc': (185,)}
    example = auth(request)
    print 'example      :', example
