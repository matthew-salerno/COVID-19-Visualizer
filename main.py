#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 19:53:27 2020

@author: matt
"""

#TODO: Move out of main.py
#TODO: Add docstrings to functions

import sys
import CovidData
import plotter

from PyQt5.QtWidgets import QMainWindow, QLineEdit, QDockWidget, QComboBox, QCalendarWidget, QPushButton, QWidget, QGridLayout, QListWidget, QApplication, QLabel#, QAbstractItemView
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, pyqtSlot, QDate
from copy import deepcopy
import matplotlib.dates as mdates
import datetime
from converters import QDate2DateNum, DateNum2QDate, Path2Name

class App(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        self.initUI()
    def initUI(self):
        #setup
        self.mainWidget = QWidget()
        self.mainGrid = QGridLayout(self)
        self.mainWidget.setLayout(self.mainGrid)
        self.setCentralWidget(self.mainWidget)
        #add widgets
        self.regions = regionSelectWidget()
        self.plotSettings = plotSettings()
        self.cal = calendar()
        self.plot = plotButton()
        
        self.mainGrid.addWidget(self.regions, 1,0,5,1)
        self.mainGrid.addWidget(self.plotSettings, 0,0,1,1)
        self.mainGrid.addWidget(self.cal, 0,1,3,1)
        self.mainGrid.addWidget(self.plot, 7,0,1,2)

        #finalize
        self.plot.button.clicked.connect(self.plotData)
        self.show()
        
    def plotData(self):
        COMBINE = 'seperate'
        XSCALE = 'linear'
        YSCALE = 'linear'
        plotter.plot(self.regions.getRootRegion(),self.regions.getPathList(),
                     self.cal.getRange(),self.cal.getEvents(),COMBINE,
                     [self.plotSettings.getYField()],self.plotSettings.getXField(),
                     XSCALE,YSCALE)


class plotSettings(QWidget):
    def __init__(self, *args, **kwargs):
        super(plotSettings, self).__init__(*args, **kwargs)
        self.initUI()
        
    def initUI(self):
        self._grid = QGridLayout(self)
        self.setLayout(self._grid)
        
        #dependent field
        self.depMenu = QComboBox()
        self.depMenu.addItems(['None'] + list(set(CovidData.region().getData().getAll())))
        self._grid.addWidget(self.depMenu, 1,0,1,1)
        self.depMenu.currentIndexChanged.connect(self.setYField)
        
        #independent field
        self.indepMenu = QComboBox()
        self.indepMenu.addItems(['None'] + list(set(CovidData.region().getData().getAll())))
        self._grid.addWidget(self.indepMenu, 1,1,1,1)
        self.indepMenu.currentIndexChanged.connect(self.setXField)
        
        #independent label
        self.xLabel =  QLabel('X')
        self.xLabel.setAlignment(Qt.AlignCenter)
        self._grid.addWidget(self.xLabel, 0,1,1,1)
        
        
        #Dependent Label
        self.yLabel =  QLabel('Y')
        self.yLabel.setAlignment(Qt.AlignCenter)
        self._grid.addWidget(self.yLabel, 0,0,1,1)
    
    def setXField(self, index):
        self.xField = self.indepMenu.itemText(index)
    def setYField(self, index):
        self.yField = self.depMenu.itemText(index)
    def getXField(self):
        return self.xField
    def getYField(self):
        return self.yField
    
class plotButton(QWidget):
        def __init__(self, *args, **kwargs):
            super(plotButton, self).__init__(*args, **kwargs)
            self.initUI()
        def initUI(self):
            self._grid = QGridLayout(self)
            self.button = QPushButton('Plot')
            self._grid.addWidget(self.button, 0,0,1,1)


class calendar(QWidget):
    def __init__(self, *args, **kwargs):
        super(calendar, self).__init__(*args, **kwargs)
        self.initUI()
        self._minDate = None
        self._maxDate = None
        self._events = {}
        
    def initUI(self):
        self._grid = QGridLayout(self)
        self.setLayout(self._grid)
        
        self.textbox = QLineEdit()
        self.cal = QCalendarWidget()
        self.addButton = QPushButton('Save Event')
        self.minButton = QPushButton('Set Start')
        self.maxButton = QPushButton('Set End')
        self.resetRangeButton = QPushButton('Reset Start/End Dates')
        self.resetEventsButton = QPushButton('Remove All Events')
        
        self.cal.clicked.connect(self._dayChanged)
        self.minButton.clicked.connect(self._updateMin)
        self.maxButton.clicked.connect(self._updateMax)
        self.addButton.clicked.connect(lambda x:self.saveEvent())
        self.resetRangeButton.clicked.connect(self.resetRange)
        self.resetEventsButton.clicked.connect(self.removeAllEvents)
        
        self._grid.addWidget(self.cal, 0,0,1,4)
        self._grid.addWidget(self.textbox, 3,0,1,3)
        self._grid.addWidget(self.minButton, 1,0,1,2)
        self._grid.addWidget(self.maxButton, 1,2,1,2)
        self._grid.addWidget(self.addButton, 3,3,1,1)
        self._grid.addWidget(self.resetRangeButton, 2,0,1,4)
        self._grid.addWidget(self.resetEventsButton, 5,0,1,4)
        
        
    def _getText(self):
        return self.textbox.text()
    
    def _dayChanged(self, date):
        self.textbox.setText(self.getEvent(date))
        
    def _updateMin(self):
        date = self.getDate()
        self._setRangeFormat(False)
        if self._maxDate is not None:
            if self._maxDate > date:
                self._minDate = date
        else:
            self._minDate = date
        self._setRangeFormat(True)
            
    def _updateMax(self):
        date = self.getDate()
        self._setRangeFormat(False)
        if self._minDate is not None:
            if self._minDate < date:
                self._maxDate = date
        else:
            self._maxDate = date
        self._setRangeFormat(True)
    
    def getRange(self):
        if self._maxDate is not None and self._minDate is not None:
            return (QDate2DateNum(self._minDate),QDate2DateNum(self._maxDate))
        else:
            return None
        
    def _setRangeFormat(self, bold):
        if self._maxDate is not None and self._minDate is not None:
            curDate = deepcopy(self._minDate)
            while curDate <= self._maxDate:
                if bold:
                    self._makeDateBold(curDate)
                else:
                    self._makeDateNotBold(curDate)
                curDate = curDate.addDays(1)
    
    def saveEvent(self, date = None):
        if date is None:
            date = self.getDate()
        if type(date) == QDate:
            dateNum = QDate2DateNum(date)
        elif type(date) == float:
            dateNum = date
            date = DateNum2QDate(date)
        text = self._getText()
        if text == '':
            if dateNum in self._events:
                self.removeEvent(date)
        else:
            self._events[dateNum] = text
            self._underlineDate(date)
    
    def removeEvent(self, date):
        dateNum = 0
        if type(date) == float:
            dateNum = date
            date = DateNum2QDate(date)
        else:
            dateNum = QDate2DateNum(date)
        del self._events[dateNum]
        self._removeDateUnderline(date)
    
    def getEvent(self, date):
        dateNum = 0
        if type(date) == float:
            dateNum = date
            date = DateNum2QDate(date)
        else:
            dateNum = QDate2DateNum(date)
        if dateNum in self._events:
            return self._events[dateNum]
        else:
            return None
    
    def getEvents(self):
        return self._events
        
    def getDate(self):
        return self.cal.selectedDate()
    
    def resetRange(self):
        print(self.getRange())
        self._setRangeFormat(False)
        self._minDate = None
        self._maxDate = None
        print(self.getRange())
    
    def removeAllEvents(self):
        events = tuple(self._events)
        for i in events:
            self.removeEvent(i)
        self.textbox.setText('')
    
    def _makeDateBold(self, date):
        textFormat = self.cal.dateTextFormat(date)
        textFormat.setFontWeight(QFont.Bold)
        self.cal.setDateTextFormat(date,textFormat)
    
    def _makeDateNotBold(self, date):
        textFormat = self.cal.dateTextFormat(date)
        textFormat.setFontWeight(QFont.Normal)
        self.cal.setDateTextFormat(date,textFormat)
    
    def _underlineDate(self,date):
        textFormat = self.cal.dateTextFormat(date)
        textFormat.setFontUnderline(True)
        self.cal.setDateTextFormat(date,textFormat)
    
    def _removeDateUnderline(self, date):
        textFormat = self.cal.dateTextFormat(date)
        textFormat.setFontUnderline(False)
        self.cal.setDateTextFormat(date,textFormat)
    
class regionSelectWidget(QWidget):
    def __init__(self, *args, **kwargs):
        if 'region' not in kwargs:    
            region = CovidData.region('root')
            region.addSubRegion(CovidData.USADataFromCSV())
        else:
            region = kwargs['region']
        super(regionSelectWidget, self).__init__(*args, **kwargs)
        #self.setSelectionMode(QAbstractItemView.ExtendedSelection) #temporarily removed
        
        self._region = region
        self._path = []
        self._paths = []
        self.regionList = QListWidget()
        self.pathList = QListWidget()
        self.addItemsFromRegion()
        self.initUI()
        
    def initUI(self):
        
        self._grid = QGridLayout(self)
        self.setLayout(self._grid)
        
        #RegionList 
        self.regionList.setWindowTitle('Regions')
        self.regionList.itemDoubleClicked.connect(self.regionDoubleClicked)
        self._grid.addWidget(self.regionList, 1,0,4,2)
        
        #pathlist
        self.pathList.setWindowTitle('Paths')
        self._grid.addWidget(self.pathList, 6,0,4,2)
        
        #add button
        self.addButton = QPushButton('add')
        self.addButton.clicked.connect(self.addSelectedToPath)
        self._grid.addWidget(self.addButton, 5,1,1,1)
        
        #clear button
        self.clearButton = QPushButton('clear')
        self.clearButton.clicked.connect(self.clearPathItems)
        self._grid.addWidget(self.clearButton, 10,0,1,2)
        
        #regionList title
        self.regionLabel =  QLabel('Region:')
        self.regionLabel.setAlignment(Qt.AlignCenter)
        self._grid.addWidget(self.regionLabel, 0,0,1,2)
        
        #Back button
        self.backButton = QPushButton('back')
        self.backButton.clicked.connect(self.back)
        self._grid.addWidget(self.backButton, 5,0,1,1)
        
    def getPath(self):
        return self._path
        
    def addItemsFromRegion(self, region = None):
        self.regionList.clear()
        if region is None:
            region = self.getCurrentObject()
        self.regionList.addItems(sorted(region.getSubRegions()))
        
    def getCurrentObject(self):
        curObject = self._region
        for i in self._path:
            curObject = curObject.getSubRegion(i)
        return curObject            
    def getRootRegion(self):
        return self._region

    def regionDoubleClicked(self,item):
        clickedObj = self.getCurrentObject().getSubRegion(item.text())
        if clickedObj.getSubRegions():
            self._path.append(item.text())
            self.addItemsFromRegion()

    def back(self):
        if self._path:
            self._path.pop()
            self.addItemsFromRegion()

    def addSelectedToPath(self):
        self._paths.append(self._path + [self.regionList.currentItem().text()])
        self.pathList.addItem(Path2Name(self._paths[-1]))
        
    def clearPathItems(self):
        self._paths.clear()
        self.pathList.clear()
        
    def getPathList(self):
        return self._paths
        
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())