import json
import sqlite3
import requests
import urllib3
import re
import sys
import pandas as pd
import Utils.utilityFuncs as uf
import Utils.dbTools as dbt
from datetime import datetime,timedelta,date

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
class IRR_Updater():
    
    def getPivotData(self,db,groupID,date):
        url=f'http://pivotrac.com:3001/groups/irrigation_stats?groupId={groupID}&start={date}&finish={date}'
        response=requests.get(url,verify=False)
        data=response.json()
        date=data['start'][:10]
        pivots=data['siteLocations']
        records=[]
        for p in pivots:
            id=p['name']
            try:
                water=p['data']['inches']
                records.append((id,int(date.replace('-','')),float(water)))
            except(TypeError):
                water=0.00
                records.append((id,int(date.replace('-','')),float(water)))
        dbt.insertPivotData(db,records)
        start=dbt.getEarliestDate(db)
        end=dbt.getLatestDate(db)
        dbt.fillMissing(db,start,end)
        
    
    def getETData(self,db,stn,start=None,end=None):
        if start != None:
            sy,sm,sd=uf.splitDate(start)
        else:
            max_date=dbt.getMaxDate('ET_Data')
            sy,sm,sd=uf.splitDate(datetime.strftime(max_date,'%Y-%m-%d'))
        if end != None:
            ey,em,ed=uf.splitDate(end)
        else:
            today=datetime.today()
            ey=today.year
            em=today.month
            ed=today.day
        url=f'https://www.usbr.gov/pn/agrimet/chart/{stn}{str(sy)[2:4]}et.txt'
        response=requests.get(url, verify=False)
        et_data=uf.responseToDataFrame(response)
        for d in uf.dateIncrementer(f'{sm}/{sd}',f'{em}/{ed}'):
            mo,da=d.split('/')
            date=f'{sy}{mo}{da}'
            heads=et_data.columns.to_list()
            row=et_data[et_data['DATE']==d]
            records=[]
            for h in heads[2:]:
                crop=h
                value=row[h].values[0]
                if value=='NaN':
                    value=0.00
                records.append((stn,crop,int(date),value))
            dbt.insertETData(db,records)
        
            

    def getPrecipData(self,db,stn,start,end):
        sy,sm,sd=uf.splitDate(start)
        ey,em,ed=uf.splitDate(end)
        url=f'https://www.usbr.gov/pn-bin/daily.pl?station={stn}&year={sy}&month={sm}&day={sd}&year={ey}&month={em}&day={ed}&pcode=PP'
        response=requests.get(url,verify=False)
        data=response.content.decode()
        start=data.find('DATE')
        end=data.find('END')
        trim_data=data[start:end]
        trim_data=trim_data.split('\n')
        records=[]
        for t in trim_data[1:-1]:
            row_vals=t.split(',')
            m,d,y=row_vals[0].split('/')
            precip=row_vals[1].strip()
            if precip != 'NO RECORD' and float(precip) > 0:
                records.append((stn,int(f'{y}{m}{d}'),float(precip)))
            else:
                records.append((stn,int(f'{y}{m}{d}'),0.00))
        dbt.insertPrecipData(db,records)

    @staticmethod
    def updateETData(db,yearStart):
        wstn=dbt.getWeatherStn(db)
        if wstn:
            for w in wstn:
                max_date=dbt.getMaxDate(db,'ET_Data',yearStart,w)
                today=datetime.today()-timedelta(days=1)
                today=today.replace(hour=0,minute=0,second=0,microsecond=0)
                if max_date != today:
                    today_str=datetime.strftime(today+timedelta(days=1),'%Y-%m-%d')
                    max_date_str=datetime.strftime(max_date+timedelta(days=1),'%Y-%m-%d')
                    IRR_Updater.getETData(IRR_Updater,db,w,max_date_str,today_str)

    @staticmethod
    def updatePrecipData(db,yearStart):
        wstn=dbt.getWeatherStn(db)
        if wstn:
            for w in wstn:
                max_date=dbt.getMaxDate(db,'Precip_Data',yearStart,w)
                today=datetime.today()-timedelta(days=1)
                today=today.replace(hour=0,minute=0,second=0,microsecond=0)
                if max_date != today:
                    today_str=datetime.strftime(today,'%Y-%m-%d')
                    max_date_str=datetime.strftime(max_date+timedelta(days=1),'%Y-%m-%d')
                    IRR_Updater.getPrecipData(IRR_Updater,db,w,max_date_str,today_str)
        
    @staticmethod    
    def updatePivotData(db,groupID,progressBar=None,yearStart=None):
        today=datetime.today()
        today=today.replace(hour=0,minute=0,second=0,microsecond=0)
        max_date=dbt.getMaxDate(db,'Pivot_Data',yearStart)
        if today!=max_date+timedelta(days=1):
            t_delt=today-max_date
            if progressBar:
                progressBar.setMaximum(t_delt.days-1)
            for i in range(1,t_delt.days):
                ret_day=datetime.strftime(max_date+timedelta(days=i),'%Y-%m-%d')
                IRR_Updater.getPivotData(IRR_Updater,db,groupID,ret_day)
                if progressBar:
                    progressBar.setValue(i)
        else:
            if progressBar:
                progressBar.setValue(progressBar.maximum())

if __name__=='__main__':
    today=datetime.today()
    max_date=datetime(2022,4,5)
    if today!=max_date:
        t_delt=today-max_date
        for i in range(1,t_delt.days):
            ret_day=datetime.strftime(max_date+timedelta(days=i),'%Y-%m-%d')
            sys.stdout.write(f'{i}                       \r')
            IRR_Updater.getPivotData(IRR_Updater,ret_day)
    