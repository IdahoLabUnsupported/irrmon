import Utils.dbTools as dbt
import matplotlib.pyplot as plt
import numpy as np
import Utils.utilityFuncs as uf
from math import floor
from UI import reportgen
from Utils.chart import IrrChart
from PyQt5 import QtWidgets,uic
from PyQt5.QtCore import Qt,QDate
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime

class ReportDialog(QtWidgets.QDialog):
    def __init__(self,parent,db):
        super(ReportDialog,self).__init__(parent)
        uic.loadUi('UI/report.ui',self)
        self.db=db
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Generate Irrigation Reports')
        self.comboBox.setCurrentIndex(-1)
        first_day=dbt.getEarliestDate(self.db)
        dbt.setDatePicker(first_day,self.startDate)
        last_day=dbt.getLatestDate(self.db)
        dbt.setDatePicker(last_day,self.endDate)

        self.getToday()

        self.comboBox.currentIndexChanged.connect(self.indexChanged)
        self.browse.clicked.connect(self.getFileName)
        self.accepted.connect(self.printReports)

    def getFileName(self):
        path=str(QtWidgets.QFileDialog.getExistingDirectory(self,"Select Folder"))
        self.outputLoc.setText(path)
    
    def getToday(self):
        '''Function to set end date to today's date'''
        today=datetime.today()
        date=QDate(today.year,today.month,today.day)
        self.endDate.setMaximumDate(date)
        self.endDate.setDate(date)

    def indexChanged(self):
        if self.comboBox.currentText()=='Farm':
            dbt.fillList(self.db,self.listWidget,'farm','Pivot_Group',True)
        else:
            dbt.fillList(self.db,self.listWidget,'groupID','Pivot_Group',True)

    def printReports(self):
        cat=self.comboBox.currentText()
        path=self.outputLoc.text()
        selItems=[]
        sDateVal=self.startDate.date()
        sDateStr=uf.formatDate(m=sDateVal.month(),d=sDateVal.day(),y=sDateVal.year())
        eDateVal=self.endDate.date()
        eDateStr=uf.formatDate(m=eDateVal.month(),d=eDateVal.day(),y=eDateVal.year())
        aggLev=self.aggLevel.value()
        periodShow=self.periodShow.value()
        for i in range(self.listWidget.count()):
            if self.listWidget.item(i).checkState()==Qt.Checked:
                selItems.append(self.listWidget.item(i).text())
        pp=PdfPages(f'{path}/{cat}_report_{eDateStr}.pdf')
        for i in selItems:
            dates=dbt.uniqueDates(f'Resources/{self.db}',sDateStr,eDateStr)
            if cat=='Farm':
                use,et,precip=IrrChart.getFarmData('Resources/data.db',i,sDateStr,eDateStr)
                mgr = dbt.getFarmMgr(self.db,i)
                title = f'Farm: {i}    Manager: {mgr}'
            elif cat=='Group':
                use,et,precip=IrrChart.getGroupData('Resources/data.db',i,sDateStr,eDateStr)
                row=dbt.getGroupInfo(self.db,i)
                title = f'''Group: {row["groupID"]}    Farm: {row["farm"]}    Manager: {row["manager"]}    Crop: {row["crop"]}    Variety: {row["variety"]}'''
            plot=self.barPlot(pp,dates,use,et,precip,title,aggLev,periodShow)
            pp.savefig(plot)
        pp.close()
        msg=reportgen.ReportMsg(self)
        msg.show()

    def aggData(self,data,days=1,periods=None):
        ''' 
        Function to aggregate data to a specified number of days

        Parameters:
            data (float array): the array of data to be aggrigated
            days (int): the number of days to aggregate

        Return:
            out_data: an array of aggregated data
        '''
        rdata=np.flip(data)
        ag_data=[sum(rdata[i:i+days]) for i in range(0,len(rdata),days)]
        out_data=np.flip(ag_data)
        if periods:
            return out_data[-periods:]
        return out_data

    def aggTitles(self,data,days=1,periods=None):
            ''' 
            Function to generate date strings for data aggregated to a specified number of days

            Parameters:
                data (float array): the array of data to be aggrigated
                days (int): the number of days to aggregate

            Return:
                out_data: an array of date strings
            '''
            rdata=np.flip(data)
            ag_data=[rdata[i] for i in range(0,len(rdata),days)]
            out_data=np.flip(ag_data)
            if periods:
                return out_data[-periods:]
            return out_data

    def chunkList(self,list, chunk_size):
        for i in range(0,len(list),chunk_size):
            yield list[i:i+chunk_size]

    def getOffsets(xTitles,margin=0.05):
        width=(1.-2.*margin)/len(xTitles)
        return width

    def linePlot(self,dates,use,et,precip,title,aggLev=1):
        plt.clf()
        plt.rcParams.update({'font.size':8})
        fig,ax=plt.subplots()
        xTitles=uf.intDateToLabel(dates)
        xTitles=self.aggTitles(xTitles,aggLev)
        x=np.arange(len(xTitles))
        sum_array=np.zeros(len(x))
        pivots=use.pivotID.unique()
        j=0
        markers=[".","v","1","p","P","*","s","X","d","x","h"]
        for p in pivots:
            filVals=use[use['pivotID']==p]
            vals=filVals['waterUsed'].to_list()
            vals=self.aggData(vals,aggLev)
            index=floor(j/10)
            sum_array=np.add(sum_array,vals)
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
            ax.legend(loc="upper left", fontsize=6,ncol=2)
        elif j>40 and j<=60:
            ax.legend(loc="upper left", fontsize=6,ncol=3)
        elif j>60 and j<=80:
            ax.legend(loc="upper left", fontsize=6,ncol=4)
        elif j>80:
            ax.legend(loc="upper left", fontsize=6,ncol=5)
        else:
            ax.legend(loc="upper left", fontsize=8)
        fig.tight_layout()
        
        return fig

    def barPlot(self,pp,dates,use,et,precip,title,aggLev=1,periodShow=None):
        plt.clf()
        plt.rcParams.update({'font.size':8})
        xTitles=uf.intDateToLabel(dates)
        xTitles=self.aggTitles(xTitles,aggLev,periodShow)
        x=np.arange(len(xTitles))
        pivots=use.pivotID.unique()
        piv_groups=list(self.chunkList(pivots,10))
        for grp in piv_groups:
            fig,(ax, ax_table)=plt.subplots(nrows=2, figsize=(8,8))
            ax_table.axis("off")
            width=(1.-2.*0.05)/len(grp)
            rows=[]
            cell_text=[]
            for n,p in enumerate(grp):
                xData=x+0.05+(n*width)
                filVals=use[use['pivotID']==p]
                vals=filVals['waterUsed'].to_list()
                vals=self.aggData(vals,aggLev,periodShow)
                ax.bar(xData,vals,width,label=p)
                rows.append(p)
                cell_text.append([round(x,2)for x in vals])
            crops=et.crop.unique()
            colors=['black','darkorange','limegreen','goldenrod']
            i=0
            for c in crops:
                crop=et[et['crop']==c]
                et_vals=crop['et'].to_list()
                et_vals=self.aggData(et_vals,aggLev,periodShow)
                ax.plot(x+.5,et_vals,color=colors[i],linestyle=(0,(5,5)),label=f'ET-{c}')
                rows.append(f'ET-{c}')
                cell_text.append([round(x,2) for x in et_vals])
                i+=1
            precip_vals=precip['precip'].to_list()
            precip_vals=self.aggData(precip_vals,aggLev,periodShow)
            ax.plot(x+.5,precip_vals,color='blue')
            rows.append(f'Precip')
            cell_text.append([round(x,2) for x in precip_vals])
            the_table=ax_table.table(cellText=cell_text,
                rowLabels=rows, loc='center')
            the_table.scale(1,2)
            ax.set_title(title)
            ax.set_ylabel('Water (ac-in)')
            ax.set_xticks(x+.5)
            ax.set_xticklabels(xTitles)
            ax.legend(loc="upper left", fontsize=8) 
            fig.set_tight_layout(True)
            pp.savefig(fig)
        