# si507_final_project
README: 
When running the program: 

First Step: Enter the stock code of Chinese A-stock, for example 000001 or 601111. 

Second Step: Enter a start year, for example 2020 or 2021.

Third Step: Enter a end year, which is later than the start year, for example 2021 or 2022.

Forth Step: Enter a number representing the principal money amount. This number can not be too small, preventing the amount from being too small to complete the simulated transaction. A number like 100000 or 1000000 is suitable.

Fifth Step: After completing login, logout and simulating. The program will show the average PB, average PB, average PS and total profit. There will be a tree method questioning. We can answer “yes” or “no” to get the investment advice.

Sixth Step: There will be two graphs shown.

Python Packs:

import sys

listone=sys.path

listone.append('C:\\Users\\user\\AppData\\Local\\Programs\\Python\\Python37\\Lib\\site-packages')

sys.path = listone

from mplfinance.original_flavor import candlestick_ohlc

from matplotlib.dates import date2num

import matplotlib.pyplot as plt

import requests

from dateutil import parser

from time import sleep

from datetime import datetime,time,timedelta 

import pandas as pd 

import os

import numpy as np 

import baostock as bs 

import pysnooper

Data Sources:
Origins: www.baostock.com
Format: CSV

How to access: 
use the function from baostock pack to get the PE, PB and time-series data. The code uses caching to store data as DataFrame form and then saves data as csv files to local.

Summary of data:
There are more than 20000 records available each year, a new record is generated every 5 minutes. I will mainly use five data in the record: datetime, open, high, low, close, which respectively represent the time node, opening price, highest price, lowest price and closing price of the stock price. Based on the above five data, simulate the change of the stock price in the selected time period.

How to interact with my program: Users choose and enter any existing Chinese A-stock stock code and any time span during the listing period of the stock.
Users can answer the questions based on the performance of their ideal stock, and let the program judge whether the stock is worth investing.

