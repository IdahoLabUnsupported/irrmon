from PyQt5 import QtWidgets,uic,QtGui
from PyQt5.QtCore import Qt
import Utils.dbTools as dbt
import sqlite3
import re


class PivotAssignDialog(QtWidgets.QDialog):
    def __init__(self,parent,db):
        super(PivotAssignDialog,self).__init__(parent)
        self.db=db
        uic.loadUi('UI/pivotAssign.ui',self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Assign Pivots to Groups')
        dbt.fillComboBox(self.db,self.cboGroup,'groupID','Pivot_Group')
        self.fillPivotLst()
        self.accepted.connect(self.assignPivots)
        self.cboGroup.currentIndexChanged.connect(self.groupIndexChanged)

    def fillPivotLst(self):
        self.listWidget.clear()
        q1='SELECT Distinct pivotID FROM Pivot_Data'
        q2='SELECT pivotID FROM Pivot_Assign'
        list_vals=[]
        with sqlite3.Connection(f'Resources/{self.db}') as conn:
            cur=conn.cursor()
            pivots=[p[0] for p in cur.execute(q1).fetchall()]
            assigned=[a[0] for a in cur.execute(q2).fetchall()]
            for p in pivots:
                if p not in assigned:
                    list_vals.append(p)
        for l in self.alphnum_sort(list_vals):
            item=QtWidgets.QListWidgetItem(l)
            item.setCheckState(Qt.Unchecked)
            self.listWidget.addItem(item)

    def alphnum_sort(self,list):
        convert=lambda text: int(text) if text.isdigit() else text
        alphanum_key=lambda key: [convert(c) for c in re.split('([0-9]+)',key)]
        return sorted(list, key=alphanum_key)

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
        else:
            self.txtFarm.setText('')
            self.txtMgr.setText('')
            self.txtCrop.setText('')
            self.txtVar.setText('')

    def assignPivots(self):
        groupID=int(self.cboGroup.currentText())
        selItems=[]
        for i in range(self.listWidget.count()):
            if self.listWidget.item(i).checkState()==Qt.Checked:
                selItems.append((self.listWidget.item(i).text(),groupID))
        if len(selItems) != 0:
            q='INSERT INTO Pivot_Assign VALUES (?,?)'
            with sqlite3.Connection(f'Resources/{self.db}') as conn:
                cur=conn.cursor()
                cur.executemany(q,selItems)
                conn.commit()
        self.cboGroup.setCurrentIndex(-1)
        self.fillPivotLst()
        self.show()

