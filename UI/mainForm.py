'''Copyright 2023, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED'''

import sip
from numpy import add,arange,flip,zeros
import matplotlib.pyplot as plt
from Utils.update import IRR_Updater
import Utils.utilityFuncs as uf
from UI import addGroup,pivotAssign,pivotRemove,delGroup,editGroup,report,ytd_report
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigCanvas, NavigationToolbar2QT as NavToolbar
from matplotlib.figure import Figure
from Utils.chart import IrrChart
from datetime import datetime
from math import floor
import Utils.dbTools as dbt

from PyQt5 import QtWidgets, QtGui, uic, QtCore

class MatplotlibCanvas(FigCanvas):
    '''
    Class to define Figure Canvas
    '''
    def __init__(self,parent=None, dpi=100):
        '''
        The class constructor for the MatplotlibCanvas class

        Parameters:
            parent (PyQt Widget): The widget that contains the MatplotlibCanvas class
            dpi (int): image resolution
        '''
        fig=Figure(dpi=dpi)
        self.axes=fig.add_subplot(111)
        super(MatplotlibCanvas,self).__init__(fig)
        fig.tight_layout()


class MainWindow(QtWidgets.QMainWindow):
    ''' Class that specifies the contents and actions of the MainWindow '''
    def __init__(self,groupID,db,yearStart):
        ''' The class constructor for the MainWindow class'''
        super(MainWindow,self).__init__()
        uic.loadUi('UI/mainForm.ui',self)
        self.groupID=groupID
        self.db=db
        self.yearStart=yearStart
        self.initUi()
        self.show()

    def initUi(self):
        '''The function to define appearance,data and function  '''
        screen=0
        monitor=QtWidgets.QDesktopWidget().screenGeometry(screen)
        # self.setFixedHeight(monitor.height()*.75)
        # self.setFixedWidth(monitor.width()*.75)
        self.move(monitor.center().x()-self.width()/2,monitor.center().y()-self.height()/2)
        self.canvas=MatplotlibCanvas(self)
        self.spacer=QtWidgets.QSpacerItem(20,40,QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(self.spacer)
        self.lblCbo.setText('')
        self.sbAgDays.setMinimum(1)
        self.sbAgDays.setValue(7)
        self.cboPltLevel.setCurrentIndex(-1)
        self.fileMenu=self.menubar.addMenu('File')
        self.groupMenu=self.menubar.addMenu('Group')
        self.dataMenu=self.menubar.addMenu('Data')
        self.reportMenu=self.menubar.addMenu('Reports')
        ed=dbt.getEarliestDate(self.db)
        dbt.setDatePicker(ed,self.startDate)
        self.getToday()
        

        ##File Menu
        ##TODO: Add File menu actions

        ##Group Submenu Items
        self.createGroup=QtWidgets.QAction('Create Group')
        self.deleteGroup=QtWidgets.QAction('Delete Group')
        self.editGroup=QtWidgets.QAction('Edit Group')
        self.assignPiv=QtWidgets.QAction('Assign Pivots to Groups')
        self.removePiv=QtWidgets.QAction('Remove Pivots from Group')
        self.groupMenu.addAction(self.createGroup)
        self.groupMenu.addAction(self.deleteGroup)
        self.groupMenu.addAction(self.editGroup)
        self.groupMenu.addAction(self.assignPiv)
        self.groupMenu.addAction(self.removePiv)
        self.createGroup.triggered.connect(self.createNewGroup)
        self.deleteGroup.triggered.connect(self.deleteExistingGroup)
        self.editGroup.triggered.connect(self.editExistingGroup)
        self.assignPiv.triggered.connect(self.assignPivots)
        self.removePiv.triggered.connect(self.removePivots)

        ##Data Submenu Items
        self.refreshPivot=QtWidgets.QAction('Refresh Pivot Data')
        self.refreshET=QtWidgets.QAction('Refresh ET Data')
        self.refreshPrecip=QtWidgets.QAction('Refresh Precip')
        self.dataMenu.addAction(self.refreshPivot)
        self.dataMenu.addAction(self.refreshET)
        self.dataMenu.addAction(self.refreshPrecip)
        self.refreshPivot.triggered.connect(lambda:IRR_Updater.updatePivotData(self.db,self.groupID,yearStart=self.yearStart))
        self.refreshET.triggered.connect(lambda:IRR_Updater.updateETData(self.db,self.yearStart))
        self.refreshPrecip.triggered.connect(lambda:IRR_Updater.updatePrecipData(self.db,self.yearStart))

        ##Report Submenu Items
        self.printReport=QtWidgets.QAction('Print Reports')
        self.ytdReport=QtWidgets.QAction('YTD Usage Report')
        self.reportMenu.addAction(self.printReport)
        self.reportMenu.addAction(self.ytdReport)
        self.printReport.triggered.connect(self.createReport)
        self.ytdReport.triggered.connect(self.ytdUsage)
        
        
        self.cboPltLevel.currentIndexChanged.connect(self.chgPltLvl)
        self.sbAgDays.valueChanged.connect(self.chgIndex)
        self.cboGroup.currentIndexChanged.connect(self.chgIndex)

    def getToday(self):
        '''Function to set end date to today's date'''
        today=datetime.today()
        date=QtCore.QDate(today.year,today.month,today.day)
        self.endDate.setMaximumDate(date)
        self.endDate.setDate(date)

    def chgPltLvl(self):
        ''' Defines action associated with changing the plot level combobox'''
        if self.cboPltLevel.currentIndex()==0:
            dbt.fillComboBox(self.db,self.cboGroup,'farm','Pivot_Group',True)
            self.lblCbo.setText('Farm')
        elif self.cboPltLevel.currentIndex()==1:
            dbt.fillComboBox(self.db,self.cboGroup,'groupID','Pivot_Group')
            self.lblCbo.setText('Group')

    def chgIndex(self):
        '''Function to define action when Farm/Group index is changed'''
        sDateVal=self.startDate.date()
        sDateStr=uf.formatDate(m=sDateVal.month(),d=sDateVal.day(),y=sDateVal.year())
        eDateVal=self.endDate.date()
        eDateStr=uf.formatDate(m=eDateVal.month(),d=eDateVal.day(),y=eDateVal.year())
        dates=dbt.uniqueDates(f'Resources/{self.db}',sDateStr,eDateStr)
        if self.cboPltLevel.currentIndex()==1:
            use,et,precip=IrrChart.getGroupData(
                f'Resources/{self.db}',
                self.cboGroup.currentText(),
                sDateStr,
                eDateStr
            )
        else:
            use,et,precip=IrrChart.getFarmData(
                f'Resources/{self.db}',
                self.cboGroup.currentText(),
                sDateStr,
                eDateStr
            )
        aggLev=self.sbAgDays.value()
        title=self.buildChartTitle()
        self.linePlot(dates,use,et,precip,title,aggLev)

    def aggData(self,data,days=1):
        ''' 
        Function to aggregate data to a specified number of days

        Parameters:
            data (float array): the array of data to be aggrigated
            days (int): the number of days to aggregate

        Return:
            out_data: an array of aggregated data
        '''
        rdata=flip(data)
        ag_data=[sum(rdata[i:i+days]) for i in range(0,len(rdata),days)]
        out_data=flip(ag_data)
        return out_data

    def aggTitles(self,data,days=1):
        ''' 
        Function to generate date strings for data aggregated to a specified number of days

        Parameters:
            data (float array): the array of data to be aggrigated
            days (int): the number of days to aggregate

        Return:
            out_data: an array of date strings
        '''
        rdata=flip(data)
        ag_data=[rdata[i] for i in range(0,len(rdata),days)]
        out_data=flip(ag_data)
        return out_data

    def buildChartTitle(self):
        if self.cboPltLevel.currentIndex()==0:
            farm=self.cboGroup.currentText()
            mgr=dbt.getFarmMgr(self.db,farm)
            return f'Farm: {farm}    Manager: {mgr}'
        else:
            group=self.cboGroup.currentText()
            row=dbt.getGroupInfo(self.db,group)
            return f'''Group: {row["groupID"]}    Farm: {row["farm"]}    Manager: {row["manager"]}    Crop: {row["crop"]}    Variety: {row["variety"]}'''

    def linePlot(self,dates,use,et,precip,title,aggLev=1):
        plt.clf()
        try:
            self.verticalLayout.removeWidget(self.toolbar)
            self.verticalLayout.removeWidget(self.canvas)
            sip.delete(self.toolbar)
            sip.delete(self.canvas)
            self.toolbar=None
            self.canvas=None
            self.verticalLayout.removeItem(self.spacer)
        except Exception as e:
            self.verticalLayout.removeItem(self.spacer)
            pass
        self.canvas=MatplotlibCanvas(self)
        self.toolbar=NavToolbar(self.canvas,self.centralwidget)
        self.verticalLayout.addWidget(self.toolbar)
        self.verticalLayout.addWidget(self.canvas)
        self.canvas.axes.cla()
        ax=self.canvas.axes
        xTitles=uf.intDateToLabel(dates)
        xTitles=self.aggTitles(xTitles,aggLev)
        x=arange(len(xTitles))
        sum_array=zeros(len(x))
        pivots=use.pivotID.unique()
        j=0
        markers=[".","v","1","p","P","*","s","X","d","x","h"]
        for p in pivots:
            filVals=use[use['pivotID']==p]
            vals=filVals['waterUsed'].to_list()
            vals=self.aggData(vals,aggLev)
            index=floor(j/10)
            sum_array=add(sum_array,vals)
            ax.scatter(x,vals,label=p,marker=markers[index])
            j+=1
        avg_array=sum_array/j
        crops=et.crop.unique()
        colors=['black','darkorange','limegreen','goldenrod']
        i=0
        for c in crops:
            crop=et[et['crop']==c]
            et_vals=crop['et'].to_list()
            et_vals=self.aggData(et_vals,aggLev)
            ax.plot(x,et_vals,color=colors[i],linestyle=(0,(5,5)),label=f'ET-{c}')
            i+=1
        precip_vals=precip['precip'].to_list()
        precip_vals=self.aggData(precip_vals,aggLev)
        ax.plot(x,avg_array,color='red',linestyle='dashed',label='Avg. Water Use')
        ax.plot(x,precip_vals,color='blue',linestyle=(0,(5,5)),label='Precip')
        ax.set_title(title)
        ax.set_ylabel('Water (ac-in)')
        ax.set_xticks(x)
        ax.set_xticklabels(xTitles, rotation = -90)
        if j>20 and j<=40:
            ax.legend(loc="upper left", fontsize=8,ncol=2)
        elif j>40 and j<=60:
            ax.legend(loc="upper left", fontsize=8,ncol=3)
        elif j>60 and j<=80:
            ax.legend(loc="upper left", fontsize=8,ncol=4)
        elif j>80:
            ax.legend(loc="upper left", fontsize=8,ncol=5)
        else:
            ax.legend(loc="upper left", fontsize=8)
        self.canvas.draw() 

    def ytdUsage(self):
        yr=ytd_report.ReportDialog(self,self.db)
        yr.show()

    def createNewGroup(self):
        grp_add=addGroup.AddGroup(self,self.db)
        grp_add.show()

    def deleteExistingGroup(self):
        grp_del=delGroup.DelGroup(self,self.db)
        grp_del.show()
    
    def editExistingGroup(self):
        grp_ed=editGroup.EditGroup(self,self.db)
        grp_ed.show()

    def assignPivots(self):
        pvt_adr=pivotAssign.PivotAssignDialog(self,self.db)
        pvt_adr.show()

    def removePivots(self):
        pvt_rmv=pivotRemove.PivotRemoveDialog(self,self.db)
        pvt_rmv.show()

    def createReport(self):
        cr=report.ReportDialog(self,self.db)
        cr.show()