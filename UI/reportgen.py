'''Copyright 2023, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED'''

from PyQt5 import QtWidgets,uic


class ReportMsg(QtWidgets.QDialog):
    def __init__(self,parent):
        super(ReportMsg,self).__init__(parent)
        uic.loadUi('UI/reportgen.ui',self)