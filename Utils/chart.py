'''Copyright 2023, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED'''

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re
import Utils.utilityFuncs as uf
class IrrChart():
    @staticmethod
    def getGroupData(db,group,start=None,end=None):
        use_query=f'''SELECT p.*
            FROM Pivot_Data as p, Pivot_Group as g, Pivot_Assign as a
            WHERE g.groupID={group} and g.groupID=a.groupID
            and a.pivotID=p.pivotID'''
        use=uf.filterByDate(uf.getData(db,use_query),start,end)
        et_query=f'''SELECT e.*
            FROM ET_Data as e, Pivot_Group as g
            WHERE g.groupID={group} and 
            e.weatherStn=g.weatherStn and
            e.crop=g.crop'''
        et=uf.filterByDate(uf.getData(db,et_query),start,end)
        precip_query=f'''SELECT p.* FROM Precip_Data as p, Pivot_Group as g
            WHERE g.groupID={group} and p.weatherStn=g.weatherStn'''
        precip=uf.filterByDate(uf.getData(db,precip_query),start,end)
        return use,et,precip

    @staticmethod
    def getFarmData(db,farm,start=None,end=None):
        use_query=f'''SELECT p.*
            FROM Pivot_Data as p, Pivot_Group as g, Pivot_Assign as a
            WHERE g.farm="{farm}" and g.groupID=a.groupID and a.pivotID=p.pivotID'''
        use=uf.filterByDate(uf.getData(db,use_query),start,end)
        et_query=f'''SELECT DISTINCT e.*
            FROM ET_Data as e, Pivot_Group as g
            WHERE g.farm="{farm}" and 
            e.weatherStn=g.weatherStn and
            e.crop=g.crop'''
        et=uf.filterByDate(uf.getData(db,et_query),start,end)
        precip_query=f'''SELECT DISTINCT p.* FROM Precip_Data as p, Pivot_Group as g
            WHERE g.farm="{farm}" and p.weatherStn=g.weatherStn'''
        precip=uf.filterByDate(uf.getData(db,precip_query),start,end)
        return use,et,precip

    @staticmethod
    def groupedBarPlot(use,et):
        fig,ax = plt.subplots()
        dates=use.date.unique()
        xTitles=uf.intDateToLabel(dates)
        x=np.arange(len(xTitles))
        pivotIds=use.pivotID.unique()
        barOffsets=uf.getOffsets(pivotIds)
        for p,o in zip(pivotIds,barOffsets):
            filtered=use[use['pivotID']==p]
            vals=filtered['waterUsed'].to_list()
            ax.bar(x-(o*.1),vals,.1,label=p)
        et_vals=et['et'].to_list()
        ax.plot(x,et_vals,color='black')
        ax.set_ylabel('Water (ac-in)')
        ax.set_xticks(x)
        ax.set_xticklabels(xTitles)
        ax.legend() 
        fig.set_tight_layout(True)
        return fig,ax

    @staticmethod
    def linePlot(use,et,precip):
        fig,ax = plt.subplots()
        dates=use.date.unique()
        sum_array=np.zeros(len(dates))
        xTitles=uf.intDateToLabel(dates)
        x=np.arange(len(xTitles))
        pivotIds=use.pivotID.unique()
        for p in pivotIds:
            filtered=use[use['pivotID']==p]
            vals=filtered['waterUsed'].to_numpy()
            sum_array=np.add(sum_array,vals)
            ax.scatter(x,vals,label=p)
        avg_array=sum_array/len(pivotIds)
        ax.plot(x,avg_array,color='red',linestyle='dashed',label='Avg. Water Use')
        crops=et.crop.unique()
        for c in crops:
            crop=et[et['crop']==p]
            et_vals=crop['et'].to_list()
            ax.plot(x,et_vals,color='black',linestyle=(0,(5,5)),label=f'ET-{c}')
        precip_vals=precip['precip'].to_list()
        ax.plot(x,precip_vals,color='blue',linestyle=(0,(5,5)),label='Precip')
        ax.set_ylabel('Water (ac-in)')
        ax.set_xticks(x)
        ax.set_xticklabels(xTitles, rotation = -90)
        ax.legend()
        fig.set_tight_layout(True)
        return fig,ax
