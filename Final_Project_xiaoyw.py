    # -*- codin: utf-8 -*-
'''
Spyder Editor

PEP 8: Python
'''
import sys
listone=sys.path
listone.append('C:\\Users\\user\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages')
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

#------------------------------------------------------------------------------
@pysnooper.snoop()
#------------------------------------------------------------------------------
def read_stock_number_from_local():
        stock_number = pd.read_csv('C:\\Users\\user\\Desktop\\stock_number.csv')
        stock_number_list = []
        for index, row in stock_number.iterrows():
            if len(str(row[0])) == 6:
                number = str(row[0])
            if len(str(row[0])) == 5:
                number = '0' + str(row[0])
            if len(str(row[0])) == 4:
                number = '00' + str(row[0])
            if len(str(row[0])) == 3:
                number = '000' + str(row[0])
            if len(str(row[0])) == 2:
                number = '0000' + str(row[0])
            if len(str(row[0])) == 1:
                number = '00000' + str(row[0])
            stock_number_list.append(number)
        return stock_number
#------------------------------------------------------------------------------    
class Astock(object):
        '''
        # class: A stock trading platform,needs one param
        # It has backtesting,paper trading, and real trading
        # param: strategy_name:strategy_name
        '''
#------------------------------------------------------------------------------
        def __init__(self,strategy_name):
            self.strategy_name = strategy_name
            self.Dt = []
            self.Open = []
            self.High = []
            self.Low = []
            self.Close = []
            self.Volume = []
            self.Tick = []
            self.last_tick = None
            self.new_bar = False
            self.current_order = {} 
            # {'order1':{'open_price':1,'open_datetime':'2022-07-05'},
            #'order2':{'open_price':2,'open_datetine':'2022-07-06'}}}
            self.bar20 = []
            self.bar20.insert(0,None)
            self.history_order = {}
            self.order_number = 0
            self.bar_number = False
            self.last_tick_date = None
            self.day_open_list = []
            self.day_high_list = []
            self.day_low_list = []
            self.day_close_list = []
            self.day_data_list = []
            self.HH20 = 0
            self.HC20 = 0
            self.LC20 = 0
            self.LL20 = 0
            self.range = 0
            self.today_open = 0
            self.stock = None
            self.start_date = None
            self.end_date = None

#------------------------------------------------------------------------------    
        def get_self_variable(self,stock,start_date,end_date):
            
            self.stock = stock
            self.start_date = start_date
            self.end_date = end_date

#------------------------------------------------------------------------------
        def stock_PEPB(self):
            
            lg = bs.login()
            rs = bs.query_history_k_data_plus(self.stock,
            "date,code,close,peTTM,pbMRQ,psTTM,pcfNcfTTM",
            start_date=str(self.start_date), end_date=str(self.end_date), 
            frequency="d", adjustflag="3")      
            result_list = []
            while (rs.error_code == '0') & rs.next():
                result_list.append(rs.get_row_data())
                result = pd.DataFrame(result_list, columns=rs.fields) 
            result.to_csv('C:\\Users\\user\\Desktop\\PEPB-%s.csv'% (self.stock), encoding="gbk", index=False)
            bs.logout()

#-------------------------------------------------------------------------------
        def get_stock_PEPB(self):
        
            #if str(self.stock)[0]=="6":
            #    self.stock='sh.'+str(self.stock)
            #else:
            #    if str(self.stock)[0]=='8':
            #        self.stock='bj.'+str(self.stock)
            #    else:
            #        self.stock='sz.'+str(self.stock)
            self.stock_PEPB()
            stock_PEPB_data = pd.read_csv('C:\\Users\\user\\Desktop\\PEPB-%s.csv'% (self.stock))
            PE_list = []
            PB_list = []
            PS_list = []
            for index, row in stock_PEPB_data.iterrows():
                PE_list.append(float(row[3]))
                PB_list.append(float(row[4]))
                PS_list.append(float(row[5]))
            
            return PE_list,PB_list,PS_list

#-------------------------------------------------------------------------------
        def get_data_from_baostock(self,freq):
            '''
            # func: get data from baostock
            # param: stock,start_date,end_date,freq,adjustflag
            # return: df in DataFrame with Column names:
            # index, date, time, code, open, high, low, close, volume, amount, adjustflag
            '''
            lg = bs.login()
            if str(self.stock)[0]=="6":
                self.stock='sh.'+str(self.stock)
            else:
                if str(self.stock)[0]=='8':
                    self.stock='bj.'+str(self.stock)
                else: 
                    if str(self.stock)[0] in ['0','3']:
                        self.stock='sz.'+str(self.stock)
            if freq in ['d','w','m']:
                fields = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST"
            else:
                fields = "date,time,code,open,high,low,close,volume,amount,adjustflag"
            rs = bs.query_history_k_data_plus(self.stock,
            fields,
            start_date=str(self.start_date), end_date=str(self.end_date),
            frequency=str(freq), adjustflag='2')
            bs.logout()
            df = pd.DataFrame(rs.data)
            df.columns = fields.split(',')
            
            return df

#------------------------------------------------------------------------------
        def save_baostock_data_to_local(self,freq):
            '''
            # func: save baostock data to local
            # param: stock,start_date,end_date,freq
            # return: no
            # save an excel in 'C:\\Users\\user\\Desktop\\baostock-%s_%s.csv'% (stock,freq)
            '''
            K = self.get_data_from_baostock(freq)
            
            if freq in ['d','w','m']:
                K.to_csv('C:\\Users\\user\\Desktop\\baostock-%s_%s.csv'% (self.stock,freq))
            else:
                K['time']=[t[:-3] for t in K['time']]
                K['time']=pd.to_datetime(K['time'])
                
                K = K.loc[:,['time','open','high','low','close','amount','volume']]
                K.rename(columns={'time':'datetime'},inplace = True)
                K.set_index('datetime',drop=True,inplace=True)
            
                K.to_csv('C:\\Users\\user\\Desktop\\baostock-%s_%s.csv'% (self.stock,freq))

#------------------------------------------------------------------------------    
        def get_ticks_for_backtesting(self):
            '''
            # func: get ticks for backtesting
            # param: stock,freq
            # return: ticks in list with tuple, such as
            # [(datetime,last_price),(datetime,last_price)]
            '''
            tick_path = 'C:\\Users\\user\\Desktop\\baostock(ticks)-%s.csv'% self.stock
            bar_path = 'C:\\Users\\user\\Desktop\\baostock-%s_%s.csv'% (self.stock,'5')
            if os.path.exists(tick_path):
                ticks = pd.read_csv(tick_path,parse_dates=['datetime'],index_col='datetime')
                tick_list = []
                for index, row in ticks.iterrows():
                    tick_list.append((index,row[0]))
                ticks = np.array(tick_list)
            else:
                bar_5m = pd.read_csv(bar_path)
                ticks = []
                for index, row in bar_5m.iterrows():
                    if row['open'] < 30:
                        step = 0.01
                    elif row['open'] < 60:
                        step = 0.03
                    elif row['open'] < 90:
                        step = 0.05
                    else:
                        step = 0.1
                    # in case of np.append(30, 30.11, 0.03), (open, high, step)
                    # we will not have 30.11 as the highest price
                    # we might not catch high when step is more than 0.01
                    # that is why we need arr = np.append(arr,row['high'])
                    # & arr = np.append(arr,row['low']) & arr = np.append(arr,row['close'])
                    arr = np.arange(row['open'],row['high'],step) 
                    arr = np.append(arr,row['high']) 
                    arr = np.append(arr,np.arange(row['open']-step,row['low'],-step))
                    arr = np.append(arr,row['low'])
                    arr = np.append(arr,row['close']) 
                    i = 0
                    dt = parser.parse(row['datetime'])-timedelta(minutes=5)
                    for item in arr:
                        ticks.append([dt+timedelta(seconds=0.1*i),item])
                        i += 1
            
                tick_df = pd.DataFrame(ticks, columns=['datetime','price'])
                tick_df.to_csv(tick_path,index=0)
                print('ticks successs')
            return ticks

#------------------------------------------------------------------------------    
        def get_day_data_for_backtesting(self):
            '''
            # func: get day data, including date, open, high, low, close
            # param: stock, the number of stock
            # return: day_data, an object with tuple, such as [(date, open, high, low, close)]
            '''
            day_data_path = 'C:\\Users\\user\\Desktop\\baostock-%s_%s.csv'% (self.stock,'d')
            day_data_result_path = 'C:\\Users\\user\\Desktop\\baostock-%s_%s.csv'% (self.stock,'R')
            day_data = pd.read_csv(day_data_path,parse_dates=['date'],index_col='date')
            day_data_list = []
            for index, row in day_data.iterrows():
                day_data_list.append((index,row[2],row[3],row[4],row[5]))
            day_data = np.array(day_data_list)
            day_data_df = pd.DataFrame(day_data, columns=['date','open','high','low','close'])
            day_data_df.to_csv(day_data_result_path,index=0)
            print('day data success')
            return day_data

#------------------------------------------------------------------------------    
        def save_years_data_to_local(self):
            frames = []
            for year in range(int(self.start_date),int(self.end_date)+1):
                self.start_date = str(year) + '-01-01'
                self.end_date = str(year) + '-11-15'
                a = self.get_data_from_baostock('5')
                self.start_date = str(year) + '-11-16'
                self.end_date = str(year) + '-12-31'
                b = self.get_data_from_baostock('5')
                frames.append(a)
                frames.append(b)
            K = pd.concat(frames)
            K['time']=[t[:-3] for t in K['time']]
            K['time']=pd.to_datetime(K['time'])
            K = K.loc[:,['time','open','high','low','close','amount','volume']]
            K.rename(columns={'time':'datetime'},inplace = True)
            K.set_index('datetime',drop=True,inplace=True)
            K.to_csv('C:\\Users\\user\\Desktop\\baostock-%s_%s.csv'% (self.stock,'5'))

#------------------------------------------------------------------------------      
        def get_up_to_date_tick(self,symbol):
            '''
            # func: get up-to-date ticks from http://qt.qtimg.cn/ for paper trading or real trading
            # param: symbol,which is the number of one stock, such as '600036'
            # return: no
            # start this method after 9:25
            # tick info is organized in tuple, such as (trade_datetime,last_price)
            # tick info is saved in self.Tick
            '''
            prefix = 'sh' if symbol[0]=='6'else 'sz'
            page = requests.get('http://qt.gtimg.cn/q='+prefix+symbol)
            stock_info = page.text
            mt_info = stock_info.split('~')
            last = float(mt_info[3])
            trade_datetime = parser.parse(mt_info[30])
            self.Tick = (trade_datetime,last)

#------------------------------------------------------------------------------        
        def history_data(self):
            self.Dt = []
            self.Open = []
            self.High = []
            self.Low = []
            self.Close = []
            self.Volume = []

#------------------------------------------------------------------------------        
        def bar_generator(self):
            if self.Tick[0].minute%5==0 and self.Tick[0].minute !=self.last_tick:
                self.new_bar= True
                self.last_tick=self.Tick[0].minute
                self.Open.insert(0,self.Tick[1])
                self.High.insert(0,self.Tick[1])
                self.Low.insert(0,self.Tick[1])
                self.Close.insert(0,self.Tick[1])
                self.Dt.insert(0,self.Tick[0])
            else:
                self.High[0]=max(self.High[0],self.Tick[1])
                self.Low[0]=min(self.Low[0],self.Tick[1])
                self.Close[0]=self.Tick[1]
                self.Dt[0]=self.Tick[0]
                self.new_bar=False

#------------------------------------------------------------------------------           
        def buy(self,price,volume):
            '''
            # func: create a long order 
            # param: 1.price: buying price; 2.volume: buying volume
            # return: no
            '''
            self.order_number +=1
            key = 'order' + str(self.order_number)
            self.current_order[key]={'open_datetime':self.Dt[0],'open_price':price,'volume':volume}

#------------------------------------------------------------------------------     
        def sell(self,key,price):
            '''
            # func: close a long order
            # param: 1.key: long order's key; 2.price: selling price
            # return: no
            '''
            self.current_order[key]['close_price'] = price
            self.current_order[key]['close_datetime'] = self.Dt[0]
            volume = self.current_order[key]['volume']
            open_price = self.current_order[key]['open_price']
            self.current_order[key]['pnl']=(price - open_price)*volume-price*volume*1/1000-(price+open_price)*volume*3/10000
            self.history_order[key] = self.current_order.pop(key)

#------------------------------------------------------------------------------   
        def strategy_dual_thrust(self,principle):
            if self.new_bar:
                self.bar20.insert(1,sum(self.Close[1:21])/20)
            
            if len(self.current_order)==0:
                if self.Close[0] > (self.today_open + 0.2 * self.range):
                    D = 0
                    R = 0
                    for i in range(0,61):
                        if self.Close[i+1] <= self.Close[i]:
                            R = R + 1
                        if self.Close[i+1] >= self.Close[i]:
                            D = D + 1
                    if R < 40:
                        price = self.Close[0]+0.01
                        volume = int(int(principle)/self.Close[0]/100)*100
                        self.buy(price,volume)
            elif len(self.current_order) == 1:
                key = 'order' + str(self.order_number)
                if self.Close[0] >= 1.02 * self.current_order[key]['open_price'] or self.Close[0] <= 0.98 * self.current_order[key]['open_price']:
    
                    key = list(self.current_order.keys())[0]
                    if self.Dt[0].date() != self.current_order[key]['open_datetime'].date():
                        # T+0 constraints
                        price = self.Close[0]-0.01
                        self.sell(key,price)
                    else:
                        pass

#------------------------------------------------------------------------------
        def get_HH_HC_LC_LL(self,tick,day_data):
            '''
            # func: get days average line, like MA20
            # param: 1.tick: tick info in tuple, such as (datetime, price); 
            # 2.day_data: day_data in object with tuple, such as [(date, open, high, low, close)]
            # return: no
            '''
            if tick[0].date() != self.last_tick_date:
                for item in day_data:
                    if item[0].date() == tick[0].date():
                        self.today_open = float(item[1])
                        break
                    else:
                        self.day_open_list.insert(0,float(item[1]))
                        self.day_high_list.insert(0,float(item[2]))
                        self.day_low_list.insert(0,float(item[3]))
                        self.day_close_list.insert(0,float(item[4]))
                        self.HH20 = max(self.day_high_list[0:20])
                        self.HC20 = max(self.day_close_list[0:20])
                        self.LC20 = min(self.day_close_list[0:20])
                        self.LL20 = min(self.day_low_list[0:20])
                self.range = max((self.HH20-self.LC20),(self.HC20-self.LL20))
                self.last_tick_date = tick[0].date()
        
#------------------------------------------------------------------------------   
        def bar_generator_for_backtesting(self,tick):
            '''
            # func: bar generator for backtesting only, used to upgrade self.Open, self.High, etc.
            # param: tick: tick info in tuple, such as (datetime, price)
            # return: no
            '''
            if tick[0].minute%5==0 and tick[0].minute !=self.last_tick:
                # create new bar
                self.new_bar= True
                self.last_tick=tick[0].minute
                self.Open.insert(0,tick[1])
                self.High.insert(0,tick[1])
                self.Low.insert(0,tick[1])
                self.Close.insert(0,tick[1])
                self.Dt.insert(0,tick[0])
            else:
                #update current bar
                self.High[0]=max(self.High[0],tick[1])
                self.Low[0]=min(self.Low[0],tick[1])
                self.Close[0]=tick[1]
                self.Dt[0]=tick[0]
                self.new_bar=False
#------------------------------------------------------------------------------    
        def run_backtesting_dual_thrust(self,ticks,principle,day_data):
            '''
            # func: run backtesting
            # param: ticks in list with tuple, such as (datetime, price)
            # return: no
            # ticks will be used to generate bars
            # when the number of bars is big enough, run backtesting
            '''
            for tick in ticks:
                self.get_HH_HC_LC_LL(tick,day_data)
                self.bar_generator_for_backtesting(tick)
                if self.bar_number:
                    self.strategy_dual_thrust(principle)
                else:
                    if len(self.Open) >= 100 and len(self.day_close_list) >= 20:
                        self.bar_number = True
                        self.strategy_dual_thrust(principle)
#------------------------------------------------------------------------------
def tree_question(tree):
        if tree[1]:
            answer = input(tree[0])
            if answer in ["yes","yeah"]:
                tree_question(tree[1])
            elif answer in ["no"]:
                tree_question(tree[2])
        else:
            print(tree[0])
    
tree = ["Is the average PE larger than 5?",["Is the average PE larger than 20?",
                                                     ["Are you a risk lover?",["Its average PE is too large, which means it is likely to be a high-risky choice to invest.",None,None],
                                                      ["It is not a good choice for you.",None,None]],["Its average PE is suitable to invest.",None,None]],["It is likely to be a bad choice.",None,None]]
stock=input('Please enter the stock code:')
start_year=input('Please enter a start year:')
end_year=input('Please enter an end year:')
principle=input('Please enter the principal amount:')
ast = Astock('MA-BT')
ast.get_self_variable(str(stock),str(start_year),str(end_year))
if len(start_year) == 4:
        ast.save_years_data_to_local()
        ast.start_date = str(start_year+'-01-01')
        ast.end_date = str(end_year+'-12-31')
        ast.save_baostock_data_to_local('d')
else:
        ast.save_baostock_data_to_local('d')
        ast.save_baostock_data_to_local('5')
ticks = ast.get_ticks_for_backtesting()
day_data = ast.get_day_data_for_backtesting()
ast.run_backtesting_dual_thrust(ticks,int(principle),day_data)
ast.current_order
ast.history_order

PE,PB,PS = ast.get_stock_PEPB()
average_PE = sum(PE)/len(PE)
average_PB = sum(PB)/len(PB)
average_PS = sum(PS)/len(PS)

orders =  ast.history_order
win_orders = 0
loss_orders = 0
for key in orders.keys():
        if orders[key]['pnl'] >= 0:
            win_orders += 1
        else:
            loss_orders += 1

win_rate = win_orders / len(orders)
loss_rate = loss_orders / len(orders)

print('win_rate:%s'%win_rate)
print('loss_rate:%s'%loss_rate)
print('Average PE:%s'%average_PE)
print('Average PB:%s'%average_PB)
print('Average PS:%s'%average_PS)

orders_df = pd.DataFrame(orders).T
orders_df.loc[:,'pnl'].plot.bar()
print("total profit:%s"%(sum(orders_df.loc[:,'pnl'])))

bar5 = pd.read_csv('C:\\Users\\user\\Desktop\\baostock-%s_%s.csv'% (ast.stock,'5'),parse_dates=['datetime'])

bar5.loc[:,'datetime'] = [date2num(x) for x in bar5.loc[:,'datetime']]

fig,ax = plt.subplots()
candlestick_ohlc(
        ax,
        bar5.values,
        width = 0.2,
        colorup = 'r',
        colordown = 'green',
        alpha = 1.0
        )

for index,row in orders_df.iterrows():
            ax.plot([row['open_datetime'],row['close_datetime']],
                    [row['open_price'],row['close_price']],
                    color='darkblue',marker = 'o')

tree_question(tree)
