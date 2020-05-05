# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import CovidData
import constants
import copy
import numpy as np
import sys
from converters import Path2Name

def plot(rootRegion, paths, dateRange, events, combine,
          dependentVariables, independentVariable, xScale, yScale):
    """Plots disease data
    arguments:
    rootRegion -- the region containing all the data, should be of type region
    paths -- a list containing paths to all used subregion
    dateRange -- a list of two dateNums representing the inclusive
        range of dates to use for data
    events -- a dict with dateNum (float) keys which point to a string
        describing an event to be marked on the graph
    combine -- a string which can be either 'add', 'seperate' or 'stack'
        'add' adds the data together for all regions in paths
        'seperate' plots each region as its own line
        'stack' stacks the graphs on top of eachother, where the value of the
            dependent variable is equal to the difference of the line and the
            line below it
    dependentVariables -- this is a list of keys found in rootRegion to be
        used as dependent variables these values will be displayed as seperate
        lines, does not work withcombine == 'stack'
    xScale -- scale for x axis, can be 'linear' 'log' or 'semilog'
    yScale -- scale for x axis, can be 'linear' 'log' or 'semilog'
    """

    #setup data
    allData = graphData(rootRegion, dependentVariables, independentVariable,
                        paths, events, dateRange, combine)
    #plot
    fig, ax = plt.subplots()


    for i in allData:
        plt.plot(i[constants.INDEPENDENT_KEY()],
                 i[constants.DEPENDENT_KEY()],
                 '-',
                 label = i[constants.LABEL_KEY()])
        for j in i[constants.EVENTS_KEY()]:
            plt.annotate(xy=[j[0],j[1]], s=j[2], xytext=[-20, 20],
            textcoords='offset points', arrowprops=dict(arrowstyle="-"))

    ax.set(xlabel=allData.getXLabel(), ylabel=allData.getYLabel(),
           title=allData.getTitle())
    
    dateRange = allData.getDateRange()
    if independentVariable == constants.DATE_KEY():
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        #plt.gcf().autofmt_xdate()
        plt.xticks(np.arange(dateRange[0], dateRange[1]+1,
                  ((dateRange[1]-dateRange[0])/float(constants.XTICKS()-1))),
                   rotation = constants.XTICK_ROTATION())
    #show legend
    plt.legend(loc="best")
    plt.show()



class graphData():
    def __init__(self, init_region, init_dependentKeys, init_independentKey,
             init_pathsList, init_eventsList = [], init_dateRange = None,
             init_combine = 'seperate'):
        #checks
        if type(init_region) is not CovidData.region:
            raise TypeError("Expected region of type CovidData.region, got " +
                            str(type(init_region)))
        if type(init_dependentKeys) is not list:
            raise TypeError("Expected type of list from dependentKeys, got " +
                            str(type(init_dependentKeys)))
        if type(init_independentKey) is not str:
            raise TypeError("Expected type of str from independentKey, got " +
                            str(type(init_independentKey)))
        if type(init_pathsList) is not list:
            raise TypeError("Expected type of list from pathsList, got " +
                            str(type(init_pathsList)))
        if type(init_eventsList) is not dict:
            raise TypeError("Expected type of dict from eventsList, got " +
                            str(type(init_eventsList)))

        if type(init_combine) is not str:
            raise TypeError("Expected type of str from combine, got " +
                            str(type(init_combine)))
        
        if not init_dependentKeys:
            raise ValueError("dependentKeys cannot be empty")
        if not init_pathsList:
            raise ValueError("pathsList cannot be empty")
        
        if type(init_dependentKeys[0]) is not str:
            raise TypeError("dependentKeys does not contain str, got " + 
                            str(type(init_dependentKeys[0])))
        if type(init_pathsList[0]) is not list:
            raise TypeError("pathsList[0] is not list, got " + 
                            str(type(init_pathsList[0])))
        if type(init_pathsList[0][0]) is not str:
            raise TypeError("pathsList[0][0] is not str, got " + 
                            str(type(init_pathsList[0])))
        if init_dateRange is not None:
            if type(init_dateRange) is not tuple and\
               type(init_dateRange) is not list:
                   raise TypeError("Expected type of tuple, list, or none" +
                                   "from dateRange, got "
                                   + str(type(init_dateRange)))
            if type(init_dateRange[0]) is not float and\
               type(init_dateRange[0]) is not int:
                raise TypeError("Expected float or int inside dateRange, got "
                                + str(type(init_dateRange[0])))
            if len(init_dateRange) > 2:
                raise ValueError("dateRange contains too many elements")
            if len(init_dateRange) < 2:
                raise ValueError("dateRange contains too few elements")
        #assigned variables
        self._dependentDataKeys = init_dependentKeys
        self._independentDataKey = init_independentKey
        self._combine = init_combine
        self._region = init_region
        self._paths = init_pathsList
        self._eventsList = init_eventsList
        self._dateRange = init_dateRange
        
        #generated variables
        self._title = ''
        self._xLabel = ''
        self._yLabel = ''
        self._dataDict = {}
        self._minDate = sys.float_info.max
        self._maxDate = sys.float_info.min
        #space savers
        self._depLength = len(self._dependentDataKeys)
        self._pathsLength = len(self._paths)
        
        #init process
        self.initLabels()
        self.initData()
        if self._dateRange is None:
            self._dateRange = (self._minDate, self._maxDate)

        
    def initLabels(self):
        if self._depLength > 1 and self._pathsLength > 1:
            self._xLabel = constants.KEY_TO_LABEL(self._independentDataKey)
            self._yLabel = 'Number'
            self._title =\
                  'Coronavirus'\
                + ' Over '\
                + constants.KEY_TO_LABEL(self._independentDataKey)
        
        elif self._depLength > 1 and self._pathsLength == 1:
            self._xLabel = constants.KEY_TO_LABEL(self._independentDataKey)
            self._yLabel = 'Number'
            self._title =\
                  'Coronavirus'\
                + ' Over '\
                + constants.KEY_TO_LABEL(self._independentDataKey)\
                + ' In '\
                + Path2Name(self._paths[0])
        
        elif self._depLength == 1 and self._pathsLength > 1:
            self._xLabel = constants.KEY_TO_LABEL(self._independentDataKey)
            self._yLabel = constants.KEY_TO_LABEL(self._dependentDataKeys[0])
            self._title =\
                  'Number of '\
                + constants.KEY_TO_LABEL(self._dependentDataKeys[0])\
                + ' Over '\
                + constants.KEY_TO_LABEL(self._independentDataKey)
        
        elif self._depLength == 1 and self._pathsLength == 1:
            self._xLabel = constants.KEY_TO_LABEL(self._independentDataKey)
            self._yLabel = constants.KEY_TO_LABEL(self._dependentDataKeys[0])
            self._title =\
                  'Number of '\
                + constants.KEY_TO_LABEL(self._dependentDataKeys[0])\
                + ' Over '\
                + constants.KEY_TO_LABEL(self._independentDataKey)\
                + ' In '\
                + Path2Name(self._paths[0])
        
    def initData(self):
        for path in self._paths:
            curRegion = self._region
            #loop through all elements in path
            for i in path:
                curRegion = curRegion.getSubRegion(i)
            if self._dateRange is None:
                self._dataDict[Path2Name(path)] = curRegion.getData()
            else:
                self._dataDict[Path2Name(path)] = CovidData.data()
                for i in curRegion.getData():
                    if i[constants.DATE_KEY()] >= self._dateRange[0] and\
                       i[constants.DATE_KEY()] <= self._dateRange[1]:
                           self._dataDict[Path2Name(path)].\
                               addEntry(i[constants.TOTAL_CASES_KEY()],
                                        i[constants.TOTAL_DEATHS_KEY()],
                                        i[constants.DATE_KEY()])
            tempMin = min(curRegion.getData()[constants.DATE_KEY()])
            tempMax = max(curRegion.getData()[constants.DATE_KEY()])
            if tempMin < self._minDate:
                self._minDate = tempMin
            if tempMax > self._maxDate:
                self._maxDate = tempMax
     
    def __iter__(self):
        self._pos = 0
        return self
    
    def __next__(self):
        try:
            returnValue = self[self._pos]
            self._pos += 1
        except ValueError:
            raise StopIteration
        except IndexError:
            raise StopIteration
        else:
            return returnValue
    
    def getXLabel(self):
        return self._xLabel
    
    def getYLabel(self):
        return self._yLabel
    
    def getTitle(self):
        return self._title
    
    def getDateRange(self):
        return self._dateRange
    
    #TODO: add 'add' for combine
    def __getitem__(self, key):
        """Returns a dataDict"""
        if self._depLength == 0 or self._pathsLength == 0:
            print("Error: size of _paths or _dependentDataKeys is 0")
            raise ValueError
        if type(key) is tuple:
            pathPos = key[0]
            depPos = key[1]
        elif type(key) is int:
            pathPos = key//self._depLength
            depPos = key%self._depLength
        else:
            print("ERROR: key must be int or tuple")
            raise TypeError
        if pathPos >= self._pathsLength:
            raise IndexError
        returnDict = {}
        curData = self._dataDict[Path2Name(self._paths[pathPos])]
        if self._depLength > 1 and self._pathsLength > 1:
            returnDict[constants.LABEL_KEY()] = constants.KEY_TO_LABEL\
                (self._dependentDataKeys[depPos]) + ' in '\
                + Path2Name(self._paths[pathPos])
        elif self._depLength > 1 and self._pathsLength == 1:
            returnDict[constants.LABEL_KEY()] =\
                constants.KEY_TO_LABEL(self._dependentDataKeys[depPos])
        elif self._depLength == 1 and self._pathsLength > 1:
            returnDict[constants.LABEL_KEY()] =\
                Path2Name(self._paths[pathPos])
        elif self._depLength == 1 and self._pathsLength == 1:
            returnDict[constants.LABEL_KEY()] = ''
        if self._combine == 'add':
            pass #TODO:
        else:
            returnDict[constants.DEPENDENT_KEY()] = curData\
                [self._dependentDataKeys[depPos]]
            returnDict[constants.INDEPENDENT_KEY()] = curData\
                [self._independentDataKey]
            returnDict[constants.PATH_KEY()] = self._paths[pathPos]  
        
        #add events
        returnDict[constants.EVENTS_KEY()] = []
        for date in self._eventsList:
            for dataKey in self._dataDict:
                for depKey in self._dependentDataKeys:
                    index, exists = curData.findEntry(date)
                    if not exists:
                        if index == len(curData.getDates()) or\
                           index == 0 or\
                           index < self._dateRange[0] or\
                           index > self._dateRange[1]:
                            pass #don't add event if outside ranges
                        else:
                            x = ((curData[self._independentDataKey,index] +
                                 curData[self._independentDataKey,index+1])/2)
                            y = ((curData[depKey,index] +
                                  curData[depKey,index+1])/2)
                            exists = True
                    else: #if exist
                        x = curData[self._independentDataKey,index]
                        y = curData[depKey,index]
                    if exists:
                        returnDict[constants.EVENTS_KEY()].\
                            append([x,y,self._eventsList[date]])
        return returnDict

                
"""         
                if len(dependentVariables) > 1:
                    for dependentVariable in dependentVariables:
                        dependentData[constants.KEY_TO_LABEL(dependentVariable) +\
                                      ' in ' + Path2Name(path)] = regionDataDict[dependentVariable]
                        independentData[constants.KEY_TO_LABEL(dependentVariable) +\
                                      ' in ' + Path2Name(path)] = regionDataDict[independentVariable]
                else:
                    dependentData[constants.KEY_TO_LABEL(Path2Name(path))]\
                        = regionDataDict[dependentVariables[0]]
                    independentData[constants.KEY_TO_LABEL(Path2Name(path))]\
                        = regionDataDict[independentVariable]
        elif len(paths) == 1:
            for i in paths[0]:
                curRegion = curRegion.getSubRegion(i)
            regionData = curRegion.getData().getAll()
            for i in dependentVariables:
                dependentData[constants.KEY_TO_LABEL(i)] = regionData[i]
                independentData[constants.KEY_TO_LABEL(i)] = regionData[independentVariable]
"""