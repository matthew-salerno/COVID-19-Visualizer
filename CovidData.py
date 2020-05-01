#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 19:51:46 2020

@author: matt
"""


import matplotlib.dates as dates
import urllib.request

#DEFINITIONS
URL = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
COLUMNS = {'DATES':0, 'COUNTY':1, 'STATE':2, 'FIPS':3, 'CASES':4, 'DEATHS':5}

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
            returnData.addEntry(i['total cases'], i['total deaths'], i['date'])
        for i in other:
            returnData.addEntry(i['total cases'], i['total deaths'], i['date'])
        return returnData
    
    def addEntry(self, cases,deaths,date, position = 0.5, level = 4.0):
        if len(self._Dates) == 0:
            self._TotalCases.append(cases)
            self._TotalDeaths.append(deaths)
            self._Dates.append(date)
            return
        index = round((len(self._Dates)-1)*position)
        if date == self._Dates[index]: #if date entry exists
            self._TotalCases[index] += cases
            self._TotalDeaths[index] += deaths
        elif date > self._Dates[index]: #if date is greater than position
            if index >= len(self._Dates)-1: #if outside list, append to end
                self._TotalCases.append(cases)
                self._TotalDeaths.append(deaths)
                self._Dates.append(date)
            elif date < self._Dates[index+1]: #if proper position is between current index and the next one
                self._TotalCases.insert(index+1,cases)
                self._TotalDeaths.insert(index+1,deaths)
                self._Dates.insert(index+1,date)
            else: #if inside list,change position and recurse
                position = position+1/level
                self.addEntry(cases,deaths,date,position, level*2)
        elif date < self._Dates[index]: #if date is less than position
            if index <= 0: #if outside list, insert at beginnning
                self._TotalCases.insert(0,cases)
                self._TotalDeaths.insert(0,deaths)
                self._Dates.insert(0,date)
            elif date > self._Dates[index-1]: #if proper position is between current index and the last one
                self._TotalCases.insert(index,cases)
                self._TotalDeaths.insert(index,deaths)
                self._Dates.insert(index,date)
            else: #if inside list,change position and recurse
                position = position-1/level
                self.addEntry(cases,deaths,date,position, level*2)
    
    def getAll(self, index = None):
        return {'total cases':self.getTotalCases(index), 'new cases':self.getNewCases(index),
                'total deaths':self.getTotalDeaths(index), 'new deaths':self.getNewDeaths(index),
                'date':self.getDates(index)}
                
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
    
    def getDelta(self, total, index = None):
        if index is not None:
            dateRange = [index-1,index]
            if index == 0: #if index is zero
                return float(total[0])
            if total[dateRange[1]] is not None:
                if total[dateRange[0]] is not None: #first and second dates have data
                    delta = float((total[dateRange[0]]-total[dateRange[1]])/(self._Dates[dateRange[0]]-self._Dates[dateRange[1]]))
                else: #first index date has data but second doesn't
                    if dateRange[1]+1 > len(self._Dates) - 1: #if going outside of the range
                        return #TODO: add error
                    else:
                        dateRange[1] += 1
            else: #first has no data, second is unknown
                if dateRange[0]-1 < 0: #if going outside of the range
                    return #TODO: add error
                else:
                    dateRange[0] -= 1
        
        else: #if getting the whole list
            delta = []
            for i in range(len(self._Dates)):
                delta.append(float(self.getDelta(total,i)))
        return delta
    
class region:
    def __init__(self, name = None):
        self._name = name #This is the name of the region, used for finding a path to a sub-region
        self._data = data() #This is data that does not belong to a sub-region
        self._subRegions = {} #This is a dictionary containing all the sub-regions
    
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
            subRegionData += self._subRegions[i].getData() #add up all subregions
        return subRegionData+self._data #return sum of subregions and self
    
    def addSubRegion(self, name):
        if type(name) == str:
            self._subRegions[name] = region(name)
        elif type(name) == region:
            self._subRegions[name.getName()] = name 
        
def USADataFromCSV(url = URL):
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
                USA.addEntry(int(line[COLUMNS['CASES']]),int(line[COLUMNS['DEATHS']]),dates.datestr2num(line[COLUMNS['DATES']]),[line[COLUMNS['COUNTY']],line[COLUMNS['STATE']]])
            except:
                pass
    return USA

