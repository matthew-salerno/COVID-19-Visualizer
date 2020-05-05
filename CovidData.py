#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 19:51:46 2020

@author: matthew salerno
"""

#TODO: Add docstrings

import matplotlib.dates as dates
import urllib.request
import constants

#CLASSES
class data:
    def __init__(self):
        self._TotalCases = []
        self._TotalDeaths = []
        self._Dates = []
   
    def __iter__(self):
        self._pos = 0
        return self
    
    def __next__(self):
        if self._pos >= len(self._Dates):
            raise StopIteration
        else:
            self._pos += 1
            return self.getAll(self._pos-1)
        
        
    def __add__(self, other):
        returnData = data()
        for i in self:
            returnData.addEntry(i[constants.TOTAL_CASES_KEY()],
                                i[constants.TOTAL_DEATHS_KEY()],
                                i[constants.DATE_KEY()])
        for i in other:
            returnData.addEntry(i[constants.TOTAL_CASES_KEY()],
                                i[constants.TOTAL_DEATHS_KEY()],
                                i[constants.DATE_KEY()])
        return returnData
    
    def addEntry(self, cases,deaths,date):
        index, exists = self.findEntry(date)
        if exists:
            if self._TotalCases[index] is None:
                self._TotalCases = cases
            elif cases is not None:
                self._TotalCases[index] += cases
                
            if self._TotalDeaths[index] is None:
                self._TotalDeaths = deaths
            elif deaths is not None:
                self._TotalDeaths[index] += deaths
        else:
            self._TotalCases.insert(index,cases)
            self._TotalDeaths.insert(index,deaths)
            self._Dates.insert(index,date)
       
    def findEntry(self, date, position = 0.5, level = 4.0):
        """Returns a tuple where the first element is the index of the
        object, or where the object would be inserted, and the second element
        is a boolean which represents if the object already exists or not"""
        if len(self._Dates) == 0:
            return (0, False)
        index = round((len(self._Dates)-1)*position)
        #if date entry exists
        if date == self._Dates[index]:
            return (index, True)
        #if date is greater than position
        elif date > self._Dates[index]: 
            #if outside list, return end
            if index >= len(self._Dates)-1: 
                return (len(self._Dates), False)
            #if proper position is between current index and the next one
            elif date < self._Dates[index+1]: 
                return (index+1, False)
            #if inside list,change position and recurse
            else: 
                position = position+1/level
                return self.findEntry(date,position, level*2)
        #if date is less than position
        elif date < self._Dates[index]: 
            #if outside list, insert at beginnning
            if index <= 0: 
                return (0,False)
            #if proper position is between current index and the last one
            elif date > self._Dates[index-1]: 
                return (index, False)
            else: #if inside list,change position and recurse
                position = position-1/level
                return self.findEntry(date,position, level*2)
    
    
    def getAll(self, index = None):
        values = {}
        funcs = self._getFuncs()
        for i in funcs:
            values[i] = funcs[i](index)
        return values
    
    def _getFuncs(self):
        return {constants.TOTAL_CASES_KEY():self.getTotalCases,
                constants.NEW_CASES_KEY():self.getNewCases,
                constants.TOTAL_DEATHS_KEY():self.getTotalDeaths,
                constants.NEW_DEATHS_KEY():self.getNewDeaths,
                constants.DATE_KEY():self.getDates}
    
    def __getitem__(self, key):
        if type(key) is tuple:
            index = key[1]
            key = key[0]
        elif type(key) is str:
            index = None
        else:
            raise TypeError("key must be str or tuple, got" + str(type(key)))
        if key in self._getFuncs():
            return self._getFuncs()[key](index)
        else:
            raise IndexError
    
    def getTotalCases(self, index = None):
        if index is None:
            return self._TotalCases
        else:
            return self._TotalCases[index]

    def getTotalDeaths(self, index = None):
        if index is None:
            return self._TotalDeaths
        else:
            return self._TotalDeaths[index]
        
    def getDates(self, index = None):
        if index is None:
            return self._Dates
        else:
            return self._Dates[index]
    
    def getNewCases(self, index = None):
        return self.getDelta(self._TotalCases, index)
    
    def getNewDeaths(self, index = None):
        return self.getDelta(self._TotalDeaths, index)
    
    def getDelta(self, total, index = None, dateRange = None):
        if index is not None:
            if dateRange is None:
                dateRange = [index-1,index]
            if index == 0: #if index is zero
                if total[0] is None:
                    return None
                else:
                    return float(total[0])
            #first date has data
            if total[dateRange[1]] is not None:
                #first and second dates have data
                if total[dateRange[0]] is not None: 
                    return float((total[dateRange[0]]-total[dateRange[1]])/
                                  (self._Dates[dateRange[0]]-
                                   self._Dates[dateRange[1]]))
                #first index date has data but second doesn't
                else:
                    #if going outside of the range
                    if dateRange[1]+1 > len(self._Dates) - 1: 
                        return None
                    else:
                        dateRange[1] += 1
            #first has no data, second is unknown
            else:
                #if going outside of the range
                if dateRange[0]-1 < 0: 
                    return None
                else:
                    dateRange[0] -= 1
            #recurse
            return self.getDelta(total,index,dateRange)
        #if getting the whole list
        else: 
            if dateRange is None:
                dateRange = [0,len(self._Dates)]
            delta = []
            for i in range(dateRange[0], dateRange[1]):
                delta.append(float(self.getDelta(total,i)))
        return delta
    
class region:
    def __init__(self, name = None):
        #This is the name of the region,
        #used for finding the path to a sub-region
        self._name = name 
        #This is data that does not belong to a sub-region
        self._data = data() 
        #This is a dictionary containing all the sub-regions
        self._subRegions = {} 
    
    def addEntry(self, cases, deaths, date, path = []):
        if path:
            nextHop = path.pop()
            if nextHop not in self._subRegions:
                self.addSubRegion(nextHop)
            self._subRegions[nextHop].addEntry(cases, deaths, date, path)
        else:
            self._data.addEntry(cases, deaths, date)

    def getName(self):
        return self._name
    
    def getSubRegions(self):
        return list(self._subRegions)
    
    def getSubRegion(self, name):
        return self._subRegions[name]
    
    def getData(self):
        subRegionData = data()
        for i in self._subRegions:
            #add up all subregions
            subRegionData += self._subRegions[i].getData() 
        #return sum of subregions and self
        return subRegionData+self._data 
    
    def addSubRegion(self, name):
        if type(name) == str:
            self._subRegions[name] = region(name)
        elif type(name) == region:
            self._subRegions[name.getName()] = name 
        
def USADataFromCSV(url = constants.URL()):
    USA = region('USA')
    response = urllib.request.urlopen(url)
    line = response.readline()
    line = line.decode('utf-8')
    line = line.replace('\n','')
    line = line.split(',')
    while True:
        try:
            line = response.readline()
        except:
            break
        else:
            line = line.decode('utf-8')
            line = line.replace('\n','')
            line = line.split(',')
            if len(line) != 6:
                break
            try:
                USA.addEntry(int(line[constants.COLUMNS()['CASES']]),
                             int(line[constants.COLUMNS()['DEATHS']]),
                             dates.datestr2num\
                                 (line[constants.COLUMNS()['DATES']]),
                             [line[constants.COLUMNS()['COUNTY']],
                                 line[constants.COLUMNS()['STATE']]])
            except:
                pass
    return USA

