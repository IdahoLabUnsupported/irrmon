import sqlite3
from PyQt5 import QtWidgets,uic
import json
from Utils.update import IRR_Updater

class AddGroup(QtWidgets.QDialog):
    def __init__(self,parent,db):
        super(AddGroup,self).__init__(parent)
        uic.loadUi('UI/addGroup.ui',self)
        self.db=db
        self.crops={}
        self.initUI()
        self.show()
    
    def initUI(self):
        self.fillCropCbo()
        self.fillWthStnCbo()
        self.accepted.connect(self.getValues)

    def fillCropCbo(self):
        with open('Resources/crops.txt','r') as file:
            lines=file.readlines()
            for l in lines:
                vals=l.split('-')
                t_vals=[x.strip() for x in vals]
                self.cboCrop.addItem(t_vals[1])
                self.crops[t_vals[1]]=t_vals[0]

    def fillWthStnCbo(self):
        with open('Resources/usbr_map.json') as file:
            data=json.load(file)
            stns=data['features']
            for s in stns:
                id=s['properties']['siteid']
                name=s['properties']['title']
                self.cboWStn.addItem(f'{id} : {name}')

    def validateGroup(self,value):
        with sqlite3.Connection(f'Resources/{self.db}') as conn:
            q=f'SELECT count(*) FROM Pivot_Group WHERE groupID={value}'
            cur=conn.cursor()
            cur.execute(q)
            data=cur.fetchone()[0]
            if data != 0:
                return False
            else:
                return True


    def getValues(self):
        groupId=self.spinGroup.value()
        farm=self.txtFarm.text()
        mgr=self.txtMgr.text()
        crop=self.crops[self.cboCrop.currentText()]
        var=self.txtVar.text()
        wStn=self.cboWStn.currentText()[:4]
        validGroup=self.validateGroup(groupId)
        if not validGroup:
            QtWidgets.QMessageBox.about(
                self,
                "Group Index Exists",
                f"Group ID {groupId} already exists in the database please select another Group ID"
                )
            self.show()
        else:
            with sqlite3.Connection(f'Resources/{self.db}') as conn:
                vals=[groupId,farm,mgr,crop,var,wStn]
                q='INSERT INTO Pivot_Group VALUES (?,?,?,?,?,?)'
                cur=conn.cursor()
                cur.execute(q,vals)
                conn.commit()
            self.spinGroup.setValue(groupId+1)
            self.txtFarm.setText('')
            self.txtMgr.setText('')
            self.cboCrop.setCurrentIndex(-1)
            self.txtVar.setText('')
            self.cboWStn.setCurrentIndex(-1)
            IRR_Updater.updateETData(self.db,'01/01')
            self.show()

