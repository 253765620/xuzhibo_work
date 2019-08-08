import os
import sys
sys.path.append(os.getcwd())
from flashloader import *
from PyQt5 import QtWidgets
import sys
app = QtWidgets.QApplication(sys.argv)
flash = UIFlashloader()
flash.showMaximized()
sys.exit(app.exec_())