'''Copyright 2023, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED'''

from PyQt5 import QtWidgets, uic
import json

class GroupIdDialog(QtWidgets.QDialog):
    def __init__(self,parent,jsonObj):
        super(GroupIdDialog,self).__init__(parent)
        uic.loadUi('UI/groupIDDialog.ui',self)
        self.jsonObj=jsonObj

    def addGroupId(self):
        self.jsonObj['groupID']=self.lineEdit.text()
        self.jsonObj['dataBase']=self.lineEdit_2.text()
        self.jsonObj['yearStart']=self.lineEdit_3.text()
        with open('Resources/config.json','w') as o_file:
            json.dump(self.jsonObj,o_file)
        return [self.lineEdit.text(),self.lineEdit_2.text(),self.lineEdit_3.text().replace('-','/')]

    @classmethod
    def launch(cls, parent=None, jsonObj=None):
        val=None
        dlg=cls(parent,jsonObj)
        if dlg.exec_():
            val=dlg.addGroupId()
        return val
        