#!coding=utf8
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
from app.split import Split_msg
from app.actual_msg_monitor import chargeable_sys

import time

# You can write your logic here, and it's you place!
# You can do save & custom response message if you want!
# And you also can ignore all request just like the position view!

#32960
def load_car(terminal_request):
    print terminal_request
    template = 'client_msg_id|sys_ok|client_msg_vin|client_msg_encryption|sys_fixed_msg_attr2|client_main_version_id|client_minor_version_id|client_time_serial_id|client_msg_content'
    content = terminal_request['client_msg_content']
    terminal_request['client_msg_content'] = terminal_request['client_msg_content'][0:6]
    print terminal_request['client_msg_content']
    '''
    #data save
    my_login_id = content[6]*256 + content[7]
    load_car_msg = {
        'client_msg_vin' : terminal_request['client_msg_vin_save'],
        'time_pi' : terminal_request['time_pi'],
        'time_login_car' : terminal_request['time_ter'],
        'time_interval' : terminal_request['time_interval'],
        'login_id' : (my_login_id,),
        'ICCID' : content[8:28],
        'num_subsys' : (content[28],),
        'len_coding' : (content[29],),
        'sys_coding' : content[30:],
        }
    #datasave(terminal_request,load_car_msg,'car_login')
    '''
    #send message
    return render(terminal_request, template)

        
def logout_car(terminal_request):
    template = 'client_msg_id|sys_ok|client_msg_vin|client_msg_encryption|sys_fixed_msg_attr2|client_msg_content'
    content = terminal_request['client_msg_content']
    terminal_request['client_msg_content'] = terminal_request['client_msg_content'][0:6]
    #data save
    my_login_id = str(content[6]*256 + content[7],)
    logout_car_msg = {
        'client_msg_vin' : terminal_request['client_msg_vin_save'],
        'time_pi' : terminal_request['time_pi'],
        #msg in the content
        'time_logout_car' : terminal_request['time_ter'],
        'time_interval' : terminal_request['time_interval'],
        'login_id' : my_login_id,
        }
    datasave(terminal_request,logout_car_msg,'car_logout')
    
    return render(terminal_request, template)


def actual_msg_report(terminal_request):
    template= 'client_msg_id|sys_ok|client_msg_vin|client_msg_encryption|sys_fixed_msg_attr2|client_msg_content'
    content = terminal_request['client_msg_content']
    split_str_msg = Split_msg(content)
    msg_dict = split_str_msg.split_con()
    car_actual_msg = get_sql_dict(terminal_request, msg_dict)
    try:
        res_dict = chargeable_sys(car_actual_msg)
    except Exception, e:
        pass
    datasave(terminal_request,car_actual_msg,'car_actual_msg')
    
def heartbeat(terminal_request):
    heartbeat_msg = {
        'client_msg_vin':terminal_request['client_msg_vin'],
        'time_pi':terminal_request['time_pi'],
        }
    datasave(terminal_request, heartbeat_msg, 'heart_beat')
    
def ter_cor_time(terminal_request):
    template = 'client_msg_id|sys_ok|client_msg_vin|client_msg_encryption|sys_fixed_msg_attr2|client_msg_content'
    ter_cor_time_msg = {
        'client_msg_vin':terminal_request['client_msg_vin'],
        'time_pi':terminal_request['time_pi'],
        }
    datasave(terminal_request, ter_cor_time_msg, 'ter_cor_time')
    return render(terminal_request, template)

def err_return(terminal_request):
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
    print 'example      :', example
