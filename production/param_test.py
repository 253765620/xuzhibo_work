import sys
if '/home/pi/production' not in sys.path:
    sys.path.append('/home/pi/production')

#from config.power_config import *
#from config.adc_config import *
#from config.acce_config import *
from param import *
from ID_param import *
from test_item import *
try:
    from iccid_sim import *
except:
    print('iccid_sim卡导入失败')
