import sys
'''
if '/home/pi' not in sys.path:
    sys.path.append('/home/pi')
from production.excelread import *
iccidpy()
'''
import os

sys.path.append(os.getcwd())
from flashloader import *
from PyQt5 import QtWidgets
import sys
app = QtWidgets.QApplication(sys.argv)
flash = UIFlashloader()
flash.showMaximized()
sys.exit(app.exec_())