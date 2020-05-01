# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot(x,y,xType,yType, title):
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