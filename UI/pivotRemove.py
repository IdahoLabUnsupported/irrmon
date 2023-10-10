from PyQt5 import QtWidgets,uic,QtGui
from PyQt5.QtCore import Qt
import sqlite3


class PivotRemoveDialog(QtWidgets.QDialog):
    def __init__(self,parent,db):
        super(PivotRemoveDialog,self).__init__(parent)
        uic.loadUi('UI/pivotAssign.ui',self)
        self.db=db
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Remove Pivots from Groups')
        self.fillGroupCbo()
        self.cboGroup.currentIndexChanged.connect(self.groupIndexChanged)

    def fillGroupCbo(self):
        q='SELECT groupID FROM Pivot_Group'
        with sqlite3.Connection(f'Resources/{self.db}') as conn:
            cur=conn.cursor()
            cur.execute(q)
            data=cur.fetchall()
            data.sort()
            for d in data:
                self.cboGroup.addItem(str(d[0]))
        self.cboGroup.setCurrentIndex(-1)
        self.accepted.connect(self.removePivots)

    def fillPivotLst(self):
        self.listWidget.clear()
        q2=f'SELECT pivotID FROM Pivot_Assign Where groupID={self.cboGroup.currentText()}'
        list_vals=[]
        with sqlite3.Connection(f'Resources/{self.db}') as conn:
            cur=conn.cursor()
            assigned=[a[0] for a in cur.execute(q2).fetchall()]
            for a in assigned:
                list_vals.append(a)
        for l in list_vals:
            item=QtWidgets.QListWidgetItem(l)
            item.setCheckState(Qt.Unchecked)
            self.listWidget.addItem(item)

    def groupIndexChanged(self):
        groupID=self.cboGroup.currentText()
        if groupID !='' and groupID != None:
            q=f'SELECT farm, manager, crop, variety FROM Pivot_Group WHERE groupID={groupID}'
            with sqlite3.Connection(f'Resources/{self.db}') as conn:
                cur=conn.cursor()
                data=cur.execute(q).fetchone()
                self.txtFarm.setText(data[0])
                self.txtMgr.setText(data[1])
                self.txtCrop.setText(data[2])
                self.txtVar.setText(data[3])
            self.fillPivotLst()
        else:
            self.txtFarm.setText('')
            self.txtMgr.setText('')
            self.txtCrop.setText('')
            self.txtVar.setText('')
            self.listWidget.clear()

    def removePivots(self):
        groupID=int(self.cboGroup.currentText())
        with sqlite3.Connection(f'Resources/{self.db}') as conn:
            cur=conn.cursor()
            for i in range(self.listWidget.count()):
                if self.listWidget.item(i).checkState()==Qt.Checked:
                    pivotID=self.listWidget.item(i).text()
                    q=f'DELETE FROM Pivot_Assign WHERE groupID={groupID} and pivotID="{pivotID}"'
                    cur.execute(q)
                    conn.commit()
        self.cboGroup.setCurrentIndex(-1)
        self.show()

