# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import CovidData
import constants

#TODO: remove
def plotOld(x,y,xType,yType, title):
    fig, ax = plt.subplots()
    if xType == 'date':
        plt.plot_date(x,y, '-')
        plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(mdates.SUNDAY))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
        plt.gcf().autofmt_xdate()
    else:
        plt.plot(x,y, '-')
    ax.set(xlabel=xType, ylabel=yType, title=title)
    plt.show()

#the sequel, to completely replace plot in the future    

def plot(rootRegion, paths, dateRange, events, combine,
          dependentVariables, independentVariable):
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
        lines, only works with multiple values when combine == 'add'
    """

    #setup the name of the place being plotted
    pathline = ''
    if len(paths) == 1:
        for i in range(len(paths[0])-1,-1,-1):
            pathline += ', ' + paths[0][i]
    else:
        pathline = 'multiple'
        
    #setup the yLabel
    yLabel = ''
    if len(dependentVariables) == 1:
        yLabel = constants.KEY_TO_LABEL(dependentVariables[0])
    else:
        yLabel = 'multiple'
    #setup the xLabel
    xLabel = constants.KEY_TO_LABEL(independentVariable())
    
    #setup the title    
    graphTitle = ('COVID-19, ' + yLabel + ' over ' + xLabel + ' in ' + pathline)
    
    #setup data
    #TODO: get correct data
    x = 0 #temp
    y = 0 #temp
    
    #plot
    fig, ax = plt.subplots()
    if independentVariable == constants.DATE_KEY():
        plt.plot_date(x,y, '-')
        plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(mdates.SUNDAY))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
        plt.gcf().autofmt_xdate()
    else:
        plt.plot(x,y, '-')
    ax.set(xlabel=xLabel, ylabel=yLabel, title=graphTitle)
    plt.show()
    