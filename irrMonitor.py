from PyQt5 import QtWidgets,QtGui
from UI import splash, mainForm
import sys

try:
    from ctypes import windll
    myappid='gov.inl.irrigationmonitor.0.1'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

if __name__=='__main__':
    app=QtWidgets.QApplication(sys.argv)
    spl_screen=splash.SplashScreen('UI/pivot.jpg')
    window=mainForm.MainWindow(spl_screen.groupID,spl_screen.db,spl_screen.yearStart)
    window.setWindowIcon(QtGui.QIcon('UI/icons/WaterDrop.ico'))
    spl_screen.finish(window)
    app.exec_()