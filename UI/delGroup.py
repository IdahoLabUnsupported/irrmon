import sqlite3
from PyQt5 import QtWidgets,uic
import json

class DelGroup(QtWidgets.QDialog):
    def __init__(self,parent,db):
        super(DelGroup,self).__init__(parent)
        uic.loadUi('UI/groupDel.ui',self)
        self.db=db
        self.crops={}
        self.initUI()
        self.show()
    
    def initUI(self):
        self.fillTbl()
        self.accepted.connect(self.delValues)

    def fillTbl(self):
        self.tableWidget.clear()
        with sqlite3.Connection(f'Resources/{self.db}') as conn:
            q='SELECT * FROM Pivot_Group ORDER BY groupID asc '
            cur=conn.cursor()
            cur.execute(q)
            data=cur.fetchall()
            if data:
                self.tableWidget.setRowCount(len(data)+1)
                self.tableWidget.setColumnCount(len(data[0]))
                row=0
                for d in data:
                    col=0
                    for v in d:
                        self.tableWidget.setItem(row,col,QtWidgets.QTableWidgetItem(str(v)))
                        col+=1
                    row+=1
            else:
                self.tableWidget.setRowCount(0)

    def delValues(self):
        selected=self.tableWidget.selectedItems()
        if selected:
            for item in selected:
                if item.column()==0:
                    id=item.text()
                    q1=f'DELETE FROM Pivot_Assign WHERE groupID={id}'
                    q2=f'DELETE FROM Pivot_Group WHERE groupID={id}'
                    with sqlite3.Connection(f'Resources/{self.db}') as conn:
                        cur=conn.cursor()
                        cur.execute(q1)
                        conn.commit()
                        cur.execute(q2)
                        conn.commit()
        self.fillTbl()
        self.show()
        




    @classmethod
    def launch(cls, parent=None):
        vals=[]
        dlg=cls(parent)
        if dlg.exec_():
            vals=dlg.getValues()
        return vals
