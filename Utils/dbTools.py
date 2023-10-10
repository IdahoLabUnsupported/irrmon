from sqlite3 import Connection
from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt,QDate
import re
import sqlite3

def createDataBase(name):
    with Connection(f'Resources/{name}.db') as conn:
        c=conn.cursor()
        c.execute('''
                  CREATE TABLE IF NOT EXISTS Pivot_Data
                  ([pivotID] TEXT, [date] INTEGER, [waterUsed] REAL)
                  ''')
        c.execute('''
                  CREATE TABLE IF NOT EXISTS ET_Data
                  ([weatherStn] TEXT, [crop] TEXT, [date] INTEGER, [et] REAL)
                  ''')
        c.execute('''
                  CREATE TABLE IF NOT EXISTS Pivot_Group
                  ([groupID] INTEGER, [farm] TEXT, [manager] TEXT, [crop] Text,
                  [variety] TEXT, [weatherStn] TEXT)
                  ''')
        c.execute('''
                  CREATE TABLE IF NOT EXISTS Precip_Data
                  ([weatherStn] TEXT, [date] INTEGER, [precip] REAL)
                  ''')
        c.execute('''
                  CREATE TABLE IF NOT EXISTS Pivot_Assign
                  ([pivotID] TEXT, [groupID] INTEGER)
                  ''')
        conn.commit()
        

def insertPivotData(db,records):
    with Connection(f'Resources/{db}') as conn:
        q='INSERT INTO Pivot_Data VALUES(?,?,?)'
        c=conn.cursor()
        c.executemany(q,records)
        conn.commit()

def insertETData(db,records):
    with Connection(f'Resources/{db}') as conn:
        q='INSERT INTO ET_Data Values (?,?,?,?)'
        c=conn.cursor()
        c.executemany(q,records)
        conn.commit()

def insertPrecipData(db,records):
    with Connection(f'Resources/{db}') as conn:
        q='INSERT INTO Precip_Data Values (?,?,?)'
        c=conn.cursor()
        c.executemany(q,records)
        conn.commit()

def getWeatherStn(db):
        stn=[]
        with Connection(f'Resources/{db}') as conn:
            q='SELECT Distinct weatherStn FROM Pivot_Group'
            c=conn.cursor().execute(q)
            rtn=c.fetchall()
            if rtn:
                for r in rtn:
                    stn.append(r[0])
                return stn
            else:
                return 
def getEarliestDate(db: str):
    '''Function set start date tpo earliest date associated with data in database'''
    with sqlite3.Connection(f'Resources/{db}') as conn:
        q='SELECT Min(date) from Pivot_Data'
        cur=conn.cursor()
        cur.execute(q)
        data=cur.fetchone()[0]
        return data

def getLatestDate(db): 
    with sqlite3.Connection(f'Resources/{db}') as conn:
        q='SELECT Max(date) from Pivot_Data'
        cur=conn.cursor()
        cur.execute(q)
        data=cur.fetchone()[0]
        return data       

def setDatePicker(data,dateEdit):
    y=int(str(data)[:4])
    m=int(str(data)[4:6])
    d=int(str(data)[6:])
    date=QDate(y,m,d)
    dateEdit.setMinimumDate(date)
    dateEdit.setDate(date)

def getMaxDate(db,table,defDate='01/01',wstn=None):
    with Connection(f'Resources/{db}') as conn:
        if wstn:
            q=f'SELECT MAX(date) FROM {table} where weatherStn="{wstn}"'
        else:
            q=f'SELECT MAX(date) FROM {table}'
        cur=conn.cursor()
        cur.execute(q)
        val=cur.fetchone()[0]
        val_str=str(val)
        date_str=f'{val_str[:4]}-{val_str[4:6]}-{val_str[6:]}'
        try:
            return datetime.strptime(date_str,'%Y-%m-%d')
        except(ValueError):
            year=datetime.today().year
            m,d=re.split('/|-',defDate)
            def_date_str=f'{year}-{m}-{d}'
            return datetime.strptime(def_date_str,'%Y-%m-%d')

def getFarmMgr(db,farm):
    with Connection(f'Resources/{db}') as conn:
        q=f'SELECT manager FROM Pivot_Group WHERE farm="{farm}"'
        conn.row_factory=lambda cursor,row: row[0]
        c=conn.cursor()
        mgr=c.execute(q).fetchone()
        return mgr

def getGroupInfo(db,group):
    with Connection(f'Resources/{db}') as conn:
        q=f'SELECT * FROM Pivot_Group WHERE groupID={group}'
        conn.row_factory=sqlite3.Row
        c=conn.cursor()
        row=c.execute(q).fetchone()
        return row

def fillComboBox(db,cboBox,col,table,distinct=False):
    '''Function to retrieve farm names and fill comboboxes'''
    cboBox.blockSignals(True)
    cboBox.clear()
    with Connection(f'Resources/{db}') as conn:
        if distinct:
            q=f'SELECT distinct({col}) FROM {table}'
        else:
            q=f'SELECT {col} FROM {table}'
        cur=conn.cursor()
        cur.execute(q)
        data=cur.fetchall()
        data.sort()
        for d in data:
            val=d[0]
            cboBox.addItem(str(val))
    cboBox.setCurrentIndex(-1)
    cboBox.blockSignals(False)

def fillList(db,listWidget,col,table,distinct=False):
    def alphnum_sort(list):
        convert=lambda text: int(text) if text.isdigit() else text
        alphanum_key=lambda key: [convert(c) for c in re.split('([0-9]+)',key)]
        return sorted(list, key=alphanum_key)

    listWidget.clear()
    if distinct:
        q1=f'SELECT Distinct {col} FROM {table}'
    else:
        q1=f'SELECT {col} FROM {table}'
    list_vals=[]
    with sqlite3.Connection(f'Resources/{db}') as conn:
        cur=conn.cursor()
        values=[p[0] for p in cur.execute(q1).fetchall()]
        for v in values:
            list_vals.append(str(v))
    for l in alphnum_sort(list_vals):
        item=QtWidgets.QListWidgetItem(l)
        item.setCheckState(Qt.Unchecked)
        listWidget.addItem(item)

def uniqueDates(db,start, end):
    if isinstance(start,str):
        start=''.join(start.split('-'))
    if isinstance(start,str):
        end=''.join(end.split('-'))
    query=f'SELECT DISTINCT date FROM Pivot_Data WHERE date>={start} AND date<={end}'
    with sqlite3.Connection(db) as conn:
        conn.row_factory = lambda cursor, row: row[0]
        c=conn.cursor()
        dates=c.execute(query).fetchall()
        return dates

def getGroupPivotIDs(db,group):
    with sqlite3.Connection(db) as conn:
        conn.row_factory = lambda cursor, row: row[0]
        c=conn.cursor()
        q=f'SELECT pivotID FROM Pivot_Assign WHERE groupID={group}'
        pivots=c.execute(q).fetchall()
        return pivots

def getFarmPivotIDs(db,farm):
    with sqlite3.Connection(db) as conn:
        conn.row_factory = lambda cursor, row: row[0]
        c=conn.cursor()
        q=f'''SELECT a.pivotID 
            FROM Pivot_Assign as a, Pivot_Group as g 
            WHERE g.farm="{farm}" and a.groupID=g.groupID'''
        pivots=c.execute(q).fetchall()
        return pivots

def getUseValue(db,pivot,date):
    with sqlite3.Connection(db) as conn:
        q=f'SELECT waterUsed FROM Pivot_Data WHERE pivotID="{pivot}" AND date={date}'
        c=conn.cursor()
        value=c.execute(q).fetchone()
        return value

def pivotUsageReport(db):
    with sqlite3.Connection(f'Resources/{db}') as conn:
        q='''SELECT pivotID, sum(waterUsed) as YTD_Water_Use FROM Pivot_Data
            GROUP BY pivotID ORDER BY pivotID ASC'''
        conn.row_factory=lambda cursor,row:row[:]
        c=conn.cursor()
        value=c.execute(q).fetchall()
        return value

def farmUsageReport(db):
    with sqlite3.Connection(f'Resources/{db}')as conn:
        q='''SELECT g.farm, sum(p.waterUsed) as YTD_Water_Use
             FROM Pivot_Data as p
             INNER JOIN Pivot_Assign as a ON p.pivotID = a.pivotID
             INNER JOIN Pivot_Group as g ON a.groupID = g.groupID
             GROUP BY g.farm
             ORDER BY g.farm ASC'''
        conn.row_factory=lambda cursor,row:row[:]
        c=conn.cursor()
        value=c.execute(q).fetchall()
        return value

def groupUsageReport(db):
    with sqlite3.Connection(f'Resources/{db}')as conn:
        q='''SELECT g.groupID, sum(p.waterUsed) as YTD_Water_Use
             FROM Pivot_Data as p
             INNER JOIN Pivot_Assign as a ON p.pivotID = a.pivotID
             INNER JOIN Pivot_Group as g ON a.groupID = g.groupID
             GROUP BY g.groupID
             ORDER BY g.groupID ASC'''
        conn.row_factory=lambda cursor,row:row[:]
        c=conn.cursor()
        value=c.execute(q).fetchall()
        return value

def fillMissing(db,start,end):
    with sqlite3.Connection(f'Resources/{db}') as conn:
        q='''SELECT DISTINCT pivotID FROM Pivot_Data'''
        conn.row_factory=lambda cursor,row:row[0]
        c=conn.cursor()
        pivots=c.execute(q).fetchall()
        dates=uniqueDates(f'Resources/{db}',start,end)
        for p in pivots:
            for d in dates:
                q2=f'''SELECT waterUsed FROM Pivot_Data
                      WHERE pivotID="{p}" and date={d}'''
                value=c.execute(q2).fetchone()
                if value==None:
                    row=[p,d,0.0]
                    q3=f'''INSERT INTO Pivot_Data(pivotID,
                           date, waterUsed) VALUES (?,?,?)'''
                    c.execute(q3,row)
                    conn.commit()