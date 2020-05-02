#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  1 14:10:15 2020

@author: matt
This section contains constants used, values are hardcoded into functions to
prevent any possible modification
"""



def URL():
    return 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
def COLUMNS(source = 'NYT-Counties'):
    if source == 'NYT-Counties':
        return {'DATES':0, 'COUNTY':1, 'STATE':2,
                'FIPS':3, 'CASES':4, 'DEATHS':5}

def KEY_TO_LABEL(key = None):
    """Returns a desired text label from a key"""
    KeyDict = {TOTAL_CASES_KEY():TOTAL_CASES_LABEL(),
            DATE_KEY():DATE_LABEL(),
            TOTAL_DEATHS_KEY():TOTAL_DEATHS_LABEL(),
            NEW_CASES_KEY():NEW_CASES_LABEL(),
            NEW_DEATHS_KEY():NEW_DEATHS_LABEL()}
    if key is None:
        return KeyDict
    else:
        return KeyDict[key]

#Keys used for addressing data

def TOTAL_CASES_KEY():
    """Returns the key for total cases"""
    return 'total cases'
def DATE_KEY():
    """Returns the key for date"""
    return 'date'
def TOTAL_DEATHS_KEY():
    """Returns the key for total deaths"""
    return 'total deaths'
def NEW_CASES_KEY():
    """Returns the key for new cases"""
    return 'new cases'
def NEW_DEATHS_KEY():
    """Returns the key for new deaths"""
    return 'new deaths'

#labels used displaying data

def TOTAL_CASES_LABEL():
    return 'Total Cases'
def DATE_LABEL():
    return 'Time'
def TOTAL_DEATHS_LABEL():
    return 'Total Deaths'
def NEW_CASES_LABEL():
    return 'New Cases'
def NEW_DEATHS_LABEL():
    return 'New Deaths'


def TIME_TYPES():
    """set of data types which are related to time"""
    return frozenset((DATE_KEY(),NEW_DEATHS_KEY(),NEW_CASES_KEY()))