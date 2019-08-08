#!coding=utf8
import time
from shortcuts.template import render
from app.split import Split_msg
from app.split import PositionSplit
from app.split import TerminalAttributeSplit
from app.admin import ConvertBaseRegister

from app.datasave import datasave
from app.actual_msg_monitor import chargeable_sys
from configs.db_config import GB_TABLE_DICT
from utils.tools import int_to_str_display,ter_time_to_stamp,get_sys_time_int_tuple

# 国标平台应答数据解析
def ter_register(terminal_request):
    '''
    - 注册应答
    '''
    template = 'register_rsp|sys_ok|client_msg_vin|client_msg_encryption|register_len|client_msg_content|com_serial_id'
    terminal_request['client_msg_content'] = terminal_request['client_msg_content'][0:6]
    return render(terminal_request, template)

def load_car(terminal_request):
    '''
    - 登入应答
    '''
    template = 'client_msg_id|sys_ok|client_msg_vin|client_msg_encryption|sys_fixed_msg_attr2|client_msg_content'
    content = terminal_request['client_msg_content']                                     # client_msg_content 消息体数据
    terminal_request['client_msg_content'] = terminal_request['client_msg_content'][0:6] # 截取前6个字节
    terminal_request['time_pi'] = (int(time.time()),)                                    # 树莓派时间
    #data save
    vin = int_to_str_display(terminal_request['client_msg_vin'])                         # 获取vin码
    time_pi = terminal_request['time_pi']
    time_login_car = ter_time_to_stamp(content[:6])                                      # 登入时间
    time_interval = (str(time_pi[0]-time_login_car[0]),)                                 # 登入时间和树莓派时间的时间间隔
    login_id = (str(content[6]*256 + content[7]),)                                       # 登陆流水号
    ICCID = content[8:28]
    num_subsys = content[28:29]
    len_coding = content[29:30]
    sys_coding = content[30:]
    load_car_msg = {
        'client_msg_vin' : vin,
        'time_pi' : time_pi,
        'time_ter' : time_login_car,
        'time_interval' : time_interval,
        'login_id' : login_id,
        'iccid' : ICCID,
        'num_subsys' : num_subsys,
        'len_coding' : len_coding,
        'sys_coding' : sys_coding,
        }
    datasave(terminal_request,load_car_msg,GB_TABLE_DICT['login'])                      # 保存登入数据到数据库
    #send message
    return render(terminal_request, template)                                           # 应答数据组包处理

        
def logout_car(terminal_request):
    '''
    - 登出应答
    '''
    template = 'client_msg_id|sys_ok|client_msg_vin|client_msg_encryption|sys_fixed_msg_attr2|client_msg_content'
    content = terminal_request['client_msg_content']
    terminal_request['client_msg_content'] = terminal_request['client_msg_content'][0:6]
    terminal_request['time_pi'] = (int(time.time()),)
    #data save
    vin = int_to_str_display(terminal_request['client_msg_vin'])
    time_pi = terminal_request['time_pi']
    time_logout_car = ter_time_to_stamp(content[:6])
    time_interval = (str(time_pi[0]-time_logout_car[0]),)
    my_login_id = str(content[6]*256 + content[7],)
    logout_car_msg = {
        'client_msg_vin' : vin,
        'time_pi' : time_pi,
        #msg in the content
        'time_ter' : time_logout_car,
        'time_interval' : time_interval,
        'login_id' : my_login_id,
        }
    datasave(terminal_request,logout_car_msg,GB_TABLE_DICT['logout'])
    
    return render(terminal_request, template)


def actual_msg_report(terminal_request):
    '''
    - 实时上报数据
    '''
    template= 'client_msg_id|sys_ok|client_msg_vin|client_msg_encryption|sys_fixed_msg_attr2|client_msg_content'
    content = terminal_request['client_msg_content']
    terminal_request['time_pi'] = (int(time.time()),)
    #save
    vin = int_to_str_display(terminal_request['client_msg_vin'])
    time_pi = terminal_request['time_pi']
    time_ter = ter_time_to_stamp(content[:6])
    time_interval = (str(time_pi[0]-time_ter[0]),)
    client_msg_id = terminal_request['client_msg_id']
    car_actual_msg = {
        'client_msg_vin' : vin,
        'time_pi' : time_pi,
        #msg in the content
        'time_ter' : time_ter,
        'time_interval' : time_interval,
        'client_msg_id' : client_msg_id,
        }
    split_str_msg = Split_msg(content)
    msg_dict = split_str_msg.split_con()
    car_actual_msg = dict(msg_dict, **car_actual_msg)
    try:
        res_dict = chargeable_sys(car_actual_msg)
    except Exception,e:
        #print 'error: ',e
        pass
    datasave(terminal_request,car_actual_msg,GB_TABLE_DICT['actual_msg'])
    
def heartbeat(terminal_request):
    '''
    - 心跳数据应答
    '''
    template = 'client_msg_id|sys_ok|client_msg_vin|client_msg_encryption|client_msg_attr'
    terminal_request['time_pi'] = (int(time.time()),)
    heartbeat_msg = {
        'client_msg_vin':terminal_request['client_msg_vin'],
        'time_pi':terminal_request['time_pi'],
        }
    datasave(terminal_request, heartbeat_msg, GB_TABLE_DICT['heartbeat'])
    return render(terminal_request, template)
    
def ter_cor_time(terminal_request):
    '''
    - 校时应答
    '''
    template = 'client_msg_id|sys_ok|client_msg_vin|client_msg_encryption|sys_fixed_msg_attr2|sys_time'
    terminal_request['time_pi'] = (int(time.time()),)
    terminal_request['sys_time'] = get_sys_time_int_tuple()
    ter_cor_time_msg = {
        'client_msg_vin':terminal_request['client_msg_vin'],
        'time_pi':terminal_request['time_pi'],
        }
    datasave(terminal_request, ter_cor_time_msg, GB_TABLE_DICT['ter_cor_time'])
    return render(terminal_request, template)

def err_return(terminal_request):
    '''
    - 数据异常应答
    '''
    template = 'client_msg_id|sys_err|client_msg_vin|client_msg_encryption|sys_fixed_msg_attr2|client_msg_content'
    terminal_request['client_msg_content'] = terminal_request['client_msg_content'][0:6]
    terminal_request['client_msg_id'] = (2,)
    return render(terminal_request, template)

if __name__ == '__main__':
    """
    The below sample dicts just for test the register!
    """
    request = {'msg_id': (1, 2), 'msg_attr': (0, 2), 'dev_id': (153, 17, 152, 64, 130, 104), 't_product': (0, 1),
               'content': (81, 82), 'crc': (185,)}
    example = auth(request)
    #print 'example      :', example
