# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import CovidData
import constants
import copy
import numpy as np
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

    #setup the name of the place being plotted
    if len(paths) == 1:
        pathline = Path2Name(paths[0])
    else:
        pathline = 'multiple'
        
    #setup the yLabel
    yLabel = ''
    if len(dependentVariables) == 1:
        yLabel = constants.KEY_TO_LABEL(dependentVariables[0])
    else:
        yLabel = 'multiple'
    #setup the xLabel
    xLabel = constants.KEY_TO_LABEL(independentVariable)
    
    #setup the title    
    print(yLabel)
    print(xLabel)
    graphTitle = 'COVID-19, ' + yLabel + ' over ' + xLabel + ' in ' + pathline
    
    #setup data
    
    #This is the dict of regions contained in paths
    regions = {}
    
    for path in paths:
        curRegion = rootRegion
        regionName = Path2Name(path)
        #loop through all elements in path
        for i in path:
            curRegion = curRegion.getSubRegion(i)
        #add the region to the regions dict
        regions[regionName] = curRegion
    
    dependentData = {}
    independentData = {}
    if len(paths) > 1:
        if combine == 'seperate':
            for i in paths:
                regionDataDict = regions[Path2Name(i)].getData().getAll()
                if len(dependentVariables) > 1:
                    for j in dependentVariables:
                        dependentData[constants.KEY_TO_LABEL(j) +\
                                      ' in ' + Path2Name(i)] = regionDataDict[j]
                        independentData[constants.KEY_TO_LABEL(j) +\
                                      ' in ' + Path2Name(i)] = regionDataDict[independentVariable]
                else:
                    dependentData[constants.KEY_TO_LABEL(Path2Name(i))]\
                        = regionDataDict[dependentVariables[0]]
                    independentData[constants.KEY_TO_LABEL(Path2Name(i))]\
                        = regionDataDict[independentVariable]
        elif combine == 'add':
            totalData = CovidData.data()
            for i in paths:
                regionData = regions[Path2Name(i)].getData()
                totalData += regionData
            for i in dependentVariables:
                dependentData[constants.KEY_TO_LABEL(i)] = totalData.getAll()[i]
                independentData[constants.KEY_TO_LABEL(i)] = totalData.getAll()[independentVariable]
        elif combine == 'stack':
            if len(dependentVariables) > 1:
                pass #TODO: Error
            else:
                totalData = CovidData.data()
                for i in paths:
                    regionData = regions[Path2Name(i)].getData()
                    totalData += regionData
                    dependentData[Path2Name(i)] = totalData.getAll()[dependentVariables[0]]
                    independentData[Path2Name(i)] = totalData.getAll()[independentVariable]
    #paths is length 1
    else:
        regionData = regions[Path2Name(paths[0])].getData().getAll()
        for i in dependentVariables:
            dependentData[constants.KEY_TO_LABEL(i)] = regionData[i]
            independentData[constants.KEY_TO_LABEL(i)] = regionData[independentVariable]

    #plot
    fig, ax = plt.subplots()

    for i in dependentData:
        plt.plot(independentData[i], dependentData[i], '-', label = i)
    ax.set(xlabel=xLabel, ylabel=yLabel, title=graphTitle)
    if independentVariable in constants.TIME_TYPES():
        if independentVariable == constants.DATE_KEY():
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
            plt.gca().xaxis.set_major_locator(mdates.DayLocator())
            plt.gcf().autofmt_xdate()
        pass #TODO: add event markers here
        
    #set xticks
    allDates = set()
    for key in independentData:
        allDates = allDates | set(independentData[key])
    print(allDates)
    print(max(allDates))
    print(min(allDates))
    plt.xticks(np.arange(min(allDates),max(allDates)+1,
                         (max(allDates)-min(allDates))/constants.XTICKS()))
    plt.show()

