import os
import sys
if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')
from hlrfw.configs.ip_config import PORT_DICT


def kill_process(port):
    res = os.popen("lsof -i:%s | awk '{ print $2 }'" % (port))
    for i in res:
        if i[:-1].isdigit():
            print(i)
            os.system('sudo kill -9 {}'.format(i))
            
if __name__ == "__main__":
    for k in PORT_DICT:
        kill_process(PORT_DICT[k])
    kill_process(2560)