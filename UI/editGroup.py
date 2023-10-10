import sqlite3
from PyQt5 import QtWidgets,uic
import json
from Utils.update import IRR_Updater

class EditGroup(QtWidgets.QDialog):
    def __init__(self,parent,db):
        super(EditGroup,self).__init__(parent)
        uic.loadUi('UI/editGroup.ui',self)
        self.db=db
        self.crops={}
        self.initUI()
        self.show()
    
    def initUI(self):
        self.fillGrpCbo()
        self.fillCropCbo()
        self.fillWthStnCbo()
        self.cboGroup.currentIndexChanged.connect(self.grpChange)
        self.accepted.connect(self.getValues)

    def fillGrpCbo(self):
        with sqlite3.Connection(f'Resources/{self.db}') as conn:
            conn.row_factory=lambda cursor, row: row[0]
            cur=conn.cursor()
            q='SELECT groupID FROM Pivot_Group'
            ids=cur.execute(q).fetchall()
            for i in ids:
                self.cboGroup.addItem(str(i))
            self.cboGroup.setCurrentIndex(-1)


    def fillCropCbo(self):
        with open('Resources/crops.txt','r') as file:
            lines=file.readlines()
            for l in lines:
                vals=l.split('-')
                t_vals=[x.strip() for x in vals]
                self.cboCrop.addItem(t_vals[1])
                self.crops[t_vals[1]]=t_vals[0]
            self.cboCrop.setCurrentIndex(-1)

    def grpChange(self):
        with sqlite3.Connection(f'Resources/{self.db}') as conn:
            conn.row_factory=sqlite3.Row
            cur=conn.cursor()
            grp=self.cboGroup.currentText()
            q=f'SELECT * FROM Pivot_Group WHERE groupID={grp}'
            row=cur.execute(q).fetchone()
            self.txtFarm.setText(row[1])
            self.txtMgr.setText(row[2])
            self.cboCrop.setCurrentText(self.getKey(row[3]))
            self.txtVar.setText(row[4])
            self.cboWStn.setCurrentText(self.getStn(row[5]))

    def fillWthStnCbo(self):
        with open('Resources/usbr_map.json') as file:
            data=json.load(file)
            stns=data['features']
            for s in stns:
                id=s['properties']['siteid']
                name=s['properties']['title']
                self.cboWStn.addItem(f'{id} : {name}')
            self.cboWStn.setCurrentIndex(-1)

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

    def getKey(self,val):
        for k,v in self.crops.items():
            if val==v:
                return k
    
    def getStn(self, val):
        with open('Resources/usbr_map.json') as file:
            data=json.load(file)
            stns=data['features']
            for s in stns:
                id=s['properties']['siteid']
                name=s['properties']['title']
                if id==val:
                    return f'{id} : {name}'

    def getValues(self):
        groupId=self.cboGroup.currentText()
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
                q=f'UPDATE Pivot_Group SET farm=?, manager=?, crop=?, variety=?, weatherStn=? WHERE groupID={groupId}'
                col_vals=vals[1:]
                cur=conn.cursor()
                cur.execute(q,col_vals)
                conn.commit()
            self.spinGroup.setValue(groupId+1)
            self.txtFarm.setText('')
            self.txtMgr.setText('')
            self.cboCrop.setCurrentIndex(-1)
            self.txtVar.setText('')
            self.cboWStn.setCurrentIndex(-1)
            self.show()
