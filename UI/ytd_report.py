import Utils.dbTools as dbt
from csv import writer
from PyQt5 import QtWidgets,uic
from datetime import datetime

class ReportDialog(QtWidgets.QDialog):
    def __init__(self,parent,db):
        super(ReportDialog,self).__init__(parent)
        uic.loadUi('UI/ytd_report.ui',self)
        self.db=db
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Year To Date Use Reports')
        self.comboBox.setCurrentIndex(-1)
        self.browse.clicked.connect(self.getFileName)
        self.accepted.connect(self.printReports)

    def getFileName(self):
        path=str(QtWidgets.QFileDialog.getExistingDirectory(self,"Select Folder"))
        self.outputLoc.setText(path)

    def printReports(self):
        cat=self.comboBox.currentText()
        path=self.outputLoc.text()
        today=datetime.today()
        
        if cat=='Farm':
            rows=dbt.farmUsageReport(self.db)
        elif cat=='Group':
            rows=dbt.groupUsageReport(self.db)
        elif cat=='Pivot':
            rows=dbt.pivotUsageReport(self.db)
        with open(f'{path}/{cat}_YTD_use_report_{today.year}{today.month}{today.day}.csv','w',newline='') as outfile:
            report=writer(outfile)
            report.writerow([cat,'YTD Water Use'])
            report.writerows(rows)