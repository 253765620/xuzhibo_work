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
from app.datasave import Split_msg_to_str
from utils.tools import time_tuple_to_timestamp_tuple, int_to_str_display
from configs.db_config import ZDMON_TABLE_DICT
import time
# You can write your logic here, and it's you place!
# You can do save & custom response message if you want!
# And you also can ignore all request just like the position view!

def load_car(terminal_request):
    template = 'client_msg_id|sys_ok|client_msg_iccid|client_msg_encryption|sys_fixed_msg_attr2|client_msg_content'
    content = terminal_request['client_msg_content']
    terminal_request['client_msg_content'] = terminal_request['client_msg_content'][0:6]
    #data save
    #get parameter
    #encryption = terminal_request['client_msg_encryption']
    #msg_attr = terminal_request['client_msg_attr']
    iccid = terminal_request['client_msg_iccid']
    time_ter = time_tuple_to_timestamp_tuple(content[:6])
    my_login_id = (content[6]*256 + content[7],)
    vin = int_to_str_display(content[8:28])
    num_subsys = content[28:29]
    len_coding = content[29:30]
    sys_coding = content[30:]
    time_pi = (int(time.time()),)
    
    login_car_msg = {
        'client_msg_vin': vin,
        'time_pi': time_pi,
        'time_ter': time_ter,
        'login_id': my_login_id,
        'ICCID': iccid,
        'num_subsys': num_subsys,
        'len_coding': len_coding,
        'sys_coding': sys_coding,
        }
    datasave(terminal_request,login_car_msg,ZDMON_TABLE_DICT['login'])
    #send message
    return render(terminal_request, template)

        
def logout_car(terminal_request):
    template = 'client_msg_id|sys_ok|client_msg_iccid|client_msg_encryption|sys_fixed_msg_attr2|client_msg_content'
    content = terminal_request['client_msg_content']
    terminal_request['client_msg_content'] = terminal_request['client_msg_content'][0:6]
    #terminal_request['time_pi'] = (int(time.time()),)
    '''
    #data save
    time_pi = terminal_request['time_pi']
    time_ter = time_tuple_to_timestamp_tuple(content[:6])
    my_login_id = (content[6]*256 + content[7],)
    logout_car_msg = {
        'client_msg_vin':terminal_request['client_msg_vin'],
        'time_pi':terminal_request['time_pi'],
        #msg in the content
        'time_logout_car': time_ter,
        'login_id':my_login_id,
        }
    datasave(terminal_request,logout_car_msg,ZDMON_TABLE_DICT['logout'])
    '''
    return render(terminal_request, template)


def actual_msg_report(terminal_request):
    template = 'client_msg_id|sys_ok|client_msg_iccid|client_msg_encryption|sys_fixed_msg_attr2|client_msg_content'
    terminal_request['client_msg_content'] = terminal_request['client_msg_content'][:6]
    '''
    content = terminal_request['client_msg_content'][:6]
    con_res = Split_msg(content)
    res = con_res.split_con()
    interval_time = get_ter_interval_time(content)
    split_str_msg = Split_msg_to_str(content)
    str_msg = split_str_msg.split_con()
    car_actual_msg = get_sql_dict(terminal_request, content, str_msg)
    datasave(terminal_request,car_actual_msg,'car_actual_msg')
    '''
    return render(terminal_request, template)
    
def heartbeat(terminal_request):
    template = 'client_msg_id|sys_ok|client_msg_iccid|client_msg_encryption|sys_msg_product'
    #terminal_request['client_msg_content'] = 
    return render(terminal_request, template)

def terminal_correcting_time(terminal_request):
    now = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))[2:]
    mytime = []
    num = 0
    for i in range(6):
        mytime.append(int(now[num:num + 2]))
        num = num + 2
    mytime = tuple(mytime)
    template = 'client_msg_id|sys_ok|client_msg_iccid|client_msg_encryption|sys_fixed_msg_attr2|client_msg_content'
    terminal_request['client_msg_content'] = mytime
    return render(terminal_request, template)

def err_return(terminal_request):
    template = 'client_msg_id|sys_err|client_msg_iccid|client_msg_encryption|sys_fixed_msg_attr2|client_msg_content'
    #terminal_request['client_msg_content'] = 
    terminal_request['client_msg_id'] = (2,)
    #return render(terminal_request, template)

if __name__ == '__main__':
    """
    The below sample dicts just for test the register!
    """
    request = {'msg_id': (1, 2), 'msg_attr': (0, 2), 'dev_id': (153, 17, 152, 64, 130, 104), 't_product': (0, 1),
               'content': (81, 82), 'crc': (185,)}
    example = auth(request)
    print 'example      :', example
