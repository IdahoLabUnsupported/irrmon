import re
from datetime import datetime
import pandas as pd
import numpy as np
import sqlite3
import Utils.dbTools as dbt


def splitDate(date):
    res=re.split('/|-',date)
    if len(res[0])==4:
        return [int(x) for x in res]
    else:
        return int(res[2]),int(res[0]),int(res[1])


def isLeapYear(year):
    if (year%400==0) and (year%100==0):
        return True
    elif (year%4==0) and (year%100!=0):
        return True
    else:
        return False


def formatDate(m,d,y=None,delim='-'):
    if not y:
        if m<10:
            if d<10:
                return f'0{m}{delim}0{d}'
            else:
                return f'0{m}{delim}{d}'
        else:
            if d<10:
                return f'{m}{delim}0{d}'
            else:
                return f'{m}{delim}{d}'
    else:
        if m<10:
            if d<10:
                return f'{y}{delim}0{m}{delim}0{d}'
            else:
                return f'{y}{delim}0{m}{delim}{d}'
        else:
            if d<10:
                return f'{y}{delim}{m}{delim}0{d}'
            else:
                return f'{y}{delim}{m}{delim}{d}'


def dateIncrementer(start,end):
    sm,sd=start.split('/')
    em,ed=end.split('/')
    months=range(int(sm),int(em)+1)
    sm,sd,em,ed=[int(x) for x in [sm,sd,em,ed]]
    dates=[]
    thirty_day=[4,6,9,11]
    for m in months:
        if m==int(sm):
            if m == em:
                for d in range(sd,ed):
                        dates.append(formatDate(m,d,delim='/'))
            else:
                if m in thirty_day:
                    for d in range(sd,31):
                        dates.append(formatDate(m,d,delim='/'))
                elif m==2:
                    if isLeapYear(datetime.datetime.today().year):
                        for d in range(sd,30):
                            dates.append(formatDate(m,d,delim='/'))
                    else:
                        for d in range(sd,29):
                            dates.append(formatDate(m,d,delim='/'))
                else:
                    for d in range(sd,32):
                        dates.append(formatDate(m,d,delim='/'))
        else:
            if m==em:
                for d in range(1,ed):
                    dates.append(formatDate(m,d,delim='/'))
            else:
                if m in thirty_day:
                    for d in range(1,31):
                        dates.append(formatDate(m,d,delim='/'))
                elif m==2:
                    if isLeapYear(datetime.datetime.today().year):
                        for d in range(1,30):
                            dates.append(formatDate(m,d,delim='/'))
                    else:
                        for d in range(1,29):
                            dates.append(formatDate(m,d,delim='/'))
                else:
                    for d in range(1,32):
                        dates.append(formatDate(m,d,delim='/'))
    return dates


def responseToDataFrame(response):
    data=response.content
    rows=data.split(b'\n')
    heads=re.split(r'\s{1,}',rows[2].decode().strip())
    values=[]
    for r in rows[4:]:
        row_vals=re.split(r'\s{1,}',r.decode().strip())
        vals=[]
        for v in row_vals:
            if v =='--':
                vals.append(0.00)
            else:
                try:
                    vals.append(float(v))
                except(ValueError):
                    vals.append(v)
        values.append(vals)
    df=pd.DataFrame(values,columns=heads)
    return df.replace(np.nan,0)


def getData(db,query):
    con=sqlite3.connect(db)
    df=pd.read_sql_query(query,con,)
    con.close()
    return df


def filterByDate(df,start=None,end=None):
    if start != None and end != None:
        y,m,d=splitDate(start)
        strtVal=int(formatDate(y=y,m=m,d=d,delim=''))
        y,m,d=splitDate(end)
        endVal=int(formatDate(y=y,m=m,d=d,delim=''))
        return df.loc[(df['date']>=strtVal) & (df['date']<=endVal)]
    elif start != None and end == None:
        y,m,d=splitDate(start)
        strtDate=int(f'{y}{m}{d}')
        return df[df['date']>=strtDate]
    else:
        return df


def intDateToLabel(dates):
    fmtDates=[]
    for date in dates:
        dStr=str(date)
        y=dStr[:4]
        m=dStr[4:6]
        d=dStr[6:]
        fmtDates.append(f'{m}-{d}-{y}')
    return fmtDates


def getOffsets(bins):
    offsets=[]
    if len(bins)%2==0:
        itr=int(len(bins)/2)
        for i in range(itr,-itr,-1):
            offsets.append(i-.5)
    else:
        itr=int(len(bins)/2)
        for i in range(itr,-itr-1,-1):
            offsets.append(i) 
    return offsets

def getGroupUseData(db,group,start,end):
    dates=dbt.uniqueDates(db,start,end)
    useDict={}
    pivots=dbt.getGroupPivotIDs(db,group)
    for pivot in pivots:
        values=[]
        for date in dates:
            value=dbt.getUseValue(db,pivot,date)
            if value:
                values.append(value[0])
            else:
                values.append(0.0)
        useDict[pivot]=values
    return useDict

def getFarmUseData(db,farm,start,end):
    dates=dbt.uniqueDates(db,start,end)
    useDict={}
    pivots=dbt.getFarmPivotIDs(db,farm)
    for pivot in pivots:
        values=[]
        for date in dates:
            value=dbt.getUseValue(db,pivot,date)
            if value:
                values.append(value[0])
            else:
                values.append(0.0)
        useDict[pivot]=values
    return useDict