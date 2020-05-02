# -*- coding: utf-8 -*-

from PyQt5.QtCore import QDate
import matplotlib.dates as mdates

def Path2Name(path):
    pathName = ''
    pathName += path[-1]
    for i in range(len(path)-2,-1,-1):
            pathName += ', ' + path[i]
    return pathName

def QDate2DateNum(date):
    return mdates.datestr2num(date.toString('yyyy-MM-dd'))
                              
def DateNum2QDate(date):
    date = mdates.num2date(date)
    return QDate(date.year,date.month,date.day)