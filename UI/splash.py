from PyQt5 import QtWidgets,uic
from PyQt5.QtCore import Qt,QTimer
from PyQt5.QtGui import QPixmap,QFont
from UI import im_resources,mainForm,groupDia
from Utils.update import IRR_Updater as irr
import Utils.dbTools as dbt 
from time import sleep
import json

class SplashScreen(QtWidgets.QSplashScreen):
    def __init__(self,img):
        image=QPixmap(img)
        super(SplashScreen,self).__init__(pixmap=image)
        self.groupID=None
        self.db=None
        self.yearStart=None
        self.initUI()
        self.show()
        self.process()
        sleep(5)

    def initUI(self):
        self.layout_box=QtWidgets.QVBoxLayout(self)
        self.lblTitle=QtWidgets.QLabel("Irrigation Monitor")
        self.lblTitle.setFont(QFont("Helvetica",30,87))
        self.lblTitle.setAlignment(Qt.AlignCenter)
        self.progressBar=QtWidgets.QProgressBar()
        self.layout_box.addWidget(self.lblTitle)
        self.layout_box.addWidget(self.progressBar)
        self.setLayout(self.layout_box)
    
    def process(self):
        with open('Resources/config.json') as con:
            data=json.load(con)
            groupID=data['groupID']
            dbi=data['dataBase']
            yearStart=data['yearStart']
            if groupID == "" or dbi == "" or yearStart=="":
                groupID,dbo,yearStart=groupDia.GroupIdDialog.launch(self,data)
                if dbi=="":
                    dbt.createDataBase(dbo)
                    self.db=f'{dbo}.db'
                else:
                    self.db=f'{dbi}.db'

            else:
                self.db=f'{dbi}.db'
            self.groupID=groupID
            self.yearStart=yearStart
            irr.updatePivotData(self.db,groupID,self.progressBar,yearStart)
            start=dbt.getEarliestDate(self.db)
            end=dbt.getLatestDate(self.db)
            dbt.fillMissing(self.db,start,end)
            irr.updateETData(self.db,yearStart)
            irr.updatePrecipData(self.db,yearStart)


   

    
