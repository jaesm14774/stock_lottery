#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd 
import numpy as np 
import datetime
import re
import glob
import requests
from bs4 import BeautifulSoup
import time
import os
import random


# In[ ]:


header={
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    'referer': 'https://stockluckydraw.com/stock/StockInfo.php',
}


# In[ ]:


lottery_subscription_path=os.getcwd()+'/'


# In[ ]:


def collect_year():
    a=requests.get('https://stockluckydraw.com/stock/StockInfoOld.php',
                   headers=header,timeout=20)    
    soup=BeautifulSoup(a.text,'lxml') 
    
    r=[s.text.strip('年').strip() for s in soup.find('h1').find_all('a') if bool(re.search(string=s.text.strip(),
                                                                                        pattern='年$'))] 
    
    pd.DataFrame({'year':r}).to_csv(lottery_subscription_path+'past_record/record_year.txt',
                                   index=0,header=None)


# In[ ]:


def clean_sign(txt,sign):
    txt=re.sub(string=txt,pattern=sign,repl='')
    if txt == '':
        return np.nan
    else:
        return int(txt)

def deal_start_end_date(s):
    r=[]
    
    for i in re.finditer(string=s,pattern='\d{4}-\d{2}-\d{2}'):
        r.append(i.group(0))
        
    st=r[0]
    ed=r[1]
    
    return st,ed

def deal_stock_no_name(s):
    no=s.split('-')[0]
    name=s.split('-')[1].replace(no,'')
    
    return no,name


# In[ ]:


#history function
def collect_lottery_subscription(YEAR=None):
    if YEAR is None:
        a=requests.get('https://stockluckydraw.com/stock/StockInfoOld.php',
                       headers=header,timeout=20)
    else:
        a=requests.get(f'https://stockluckydraw.com/stock/StockInfoOld.php?YEAR={YEAR}',
                       headers=header,timeout=20)

    soup=BeautifulSoup(a.text,'lxml') 
    
    total_dat=[]

    for ta in soup.find_all('table',{'border':1,'width':'98%'})[1:]:
        col_name=[s.text.strip() for s in ta.find('tr').find_all('td')]
        row_data=[[(subpart.find('a').text.strip()+'-'+subpart.text.strip()) if subpart.find('a') is not None else subpart.text.strip() for subpart in part.find_all('td')] for part in ta.find_all('tr')[1:]]    

        total_dat.append(pd.DataFrame(row_data,columns=col_name))
        
    total_dat=pd.concat(total_dat)
    
    total_dat=total_dat.rename(columns={'承銷股數(千股)':'承銷股數(張)'})
    #string to int type
    for s in ['抽中獲利','申購筆數','申購股數','預扣費用','承銷股數(張)','總承銷金額(元)']:
        total_dat[s]=total_dat[s].apply(clean_sign,sign=',')
    
    #開始日期截止日期
    r=[deal_start_end_date(s) for s in total_dat['開始日期截止日期']]
    total_dat['開始日期']=[s[0] for s in r]
    total_dat['截止日期']=[s[1] for s in r]
    
    #股票代號股票名稱
    NO=[];NAME=[]
    for s in total_dat.股票代號股票名稱:
        no,name=deal_stock_no_name(s)
        
        NO.append(no)
        NAME.append(name)
    
    total_dat['證券代號']=NO
    total_dat['證券名稱']=NAME
    
    total_dat=total_dat.loc[:,['證券代號', '證券名稱','市場別', '抽中獲利', '獲利率', '中籤率',
                               '申購筆數', '申購價格', '參考價格', '申購股數', '開始日期',
                               '截止日期','預扣費用', '預扣款日', '抽籤日期', '還款日期', 
                               '撥券日期', '承銷股數(張)', '總承銷金額(元)', '主辦券商']]
    
    return total_dat


# In[ ]:


#new function
def collect_lottery_subscription_lastest():
    a=requests.get('https://stockluckydraw.com/StockInfoTable.htm',
                   headers=header,timeout=20)
    a.encoding='utf8'
    soup=BeautifulSoup(a.text,'lxml') 
    
    total_dat=[]

    for ta in soup.find_all('table',{'border':1,'width':'98%'}):
        col_name=[s.text.strip() for s in ta.find('tr').find_all('td')]
        row_data=[[(subpart.find('a').text.strip()+'-'+subpart.text.strip()) if subpart.find('a') is not None else subpart.text.strip() for subpart in part.find_all('td')] for part in ta.find_all('tr')[1:]]    

        total_dat.append(pd.DataFrame(row_data,columns=col_name))
        
    total_dat=pd.concat(total_dat)
    
    total_dat=total_dat.where(~total_dat.isnull(),'')
    
    #string to int type
    for s in ['抽中獲利','申購筆數','申購股數','預扣費用','承銷股數(張)','總承銷金額(元)']:
        
        total_dat[s]=total_dat[s].apply(clean_sign,sign=',')

    #股票代號股票名稱
    NO=[];NAME=[]
    for s in total_dat.股票代號股票名稱:
        no,name=deal_stock_no_name(s)
        
        NO.append(no)
        NAME.append(name)
    
    total_dat['證券代號']=NO
    total_dat['證券名稱']=NAME
    total_dat=total_dat.drop(['股票代號股票名稱'],axis=1)
    
    total_dat=total_dat.loc[:,['證券代號', '證券名稱','市場別', '抽中獲利', '獲利率', '中籤率', 
                               '申購筆數', '申購價格', '參考價格', '申購股數', '開始日期',
                               '截止日期','預扣費用', '預扣款日', '抽籤日期', '還款日期','撥券日期',
                               '承銷股數(張)', '總承銷金額(元)', '主辦券商']]
    
    return total_dat


# In[ ]:


#更新最新收集的歷史年份
collect_year()


# In[ ]:


if not os.path.isfile(lottery_subscription_path+'/past.csv'): #不存在過去的申購紀錄
    #past record
    Y=pd.read_csv(lottery_subscription_path+'/past_record/record_year.txt',header=None)[0].tolist()
    
    D=[]

    for yy in Y:
        D.append(collect_lottery_subscription(YEAR=yy))

    D=pd.concat(D)
    
    D=D[~D.duplicated(subset=['證券代號','開始日期','截止日期'])]

    D=D.sort_values(['抽籤日期'],ascending=False)   
    
    D.to_csv(lottery_subscription_path+'past.csv',encoding='utf_8_sig',index=0)


# In[ ]:


#舊資料
old=pd.read_csv(lottery_subscription_path+'past.csv',encoding='utf_8_sig',
               dtype={'證券代號':'str'})

#最新的歷史資料
d1=collect_lottery_subscription(YEAR=None)
d1=d1[~d1.duplicated(subset=['證券代號','開始日期','截止日期'])]
d1=d1.sort_values(['抽籤日期'],ascending=False)

#還未結束的資料(Line通知)
d2=collect_lottery_subscription_lastest()

d2=d2[~d2.duplicated(subset=['證券代號','開始日期','截止日期'])]
d2=d2.sort_values(['抽籤日期'],ascending=False)


# In[ ]:


#更新過去的歷史資料
d_old=pd.concat([d1,old])
d_old=d_old[~d_old.duplicated(subset=['證券代號','開始日期','截止日期'])].sort_values(['開始日期'],
                                                                          ascending=False)
d_old.to_csv(lottery_subscription_path+'past.csv',encoding='utf_8_sig',index=0)


# In[ ]:


#通知新資料
if os.path.isfile(lottery_subscription_path+'new.csv'):
    #讀取舊有新資料，判斷哪些股票尚未通知
    new=pd.read_csv(lottery_subscription_path+'new.csv',encoding='utf_8_sig',
                   dtype={'證券代號':'str'})
    d2.to_csv(lottery_subscription_path+'new.csv',encoding='utf_8_sig',index=0)
    
    #notify
    notify=d2[~((d2.證券代號+d2.開始日期).isin(new.證券代號+new.開始日期))]
else:
    d2.to_csv(lottery_subscription_path+'new.csv',encoding='utf_8_sig',index=0)
    
    notify=d2.copy()


# In[ ]:


notify=notify.loc[:,['證券代號', '證券名稱','市場別','抽中獲利','獲利率','中籤率',
       '申購股數', '開始日期', '截止日期', '預扣費用', '抽籤日期', '還款日期', '撥券日期',
       '承銷股數(張)'],]

notify=notify.reset_index(drop=True)


# In[ ]:


if notify.shape[0] == 0:
    raise RuntimeError('沒有新資料，完成~')


# In[ ]:


#Line notify
def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token, 
    }

    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", 
                      headers = headers, 
                      params = payload)
    return r.text

token='<your token>'

#Line 通知
for i in range(0,notify.shape[0]):
    #申購通知
    ['證券代號', '證券名稱','市場別','抽中獲利','獲利率','中籤率',
       '申購股數', '開始日期', '截止日期', '預扣費用', '抽籤日期', '還款日期', '撥券日期',
       '承銷股數(張)']
    
    notify=notify.where(~notify.isnull(),'')
    
    m1='\n日期:'+notify.開始日期.iloc[i]+'~'+notify.截止日期.iloc[i]+'\n市場別:'+    notify.市場別.iloc[i]+'\n證券代號:'+notify.證券代號.iloc[i]+'\n證券名稱:'+    notify.證券名稱.iloc[i]+'\n抽中獲利:'+str(notify.抽中獲利.iloc[i])+    '\n獲利率:'+str(notify.獲利率.iloc[i])+'\n中籤率:'+str(notify.中籤率.iloc[i])+'\n申購股數:'+    str(notify.申購股數.iloc[i])+'\n預扣費用:'+str(notify.預扣費用.iloc[i])+'\n抽籤日期:'+    notify.抽籤日期.iloc[i]+'\n還款日期:'+notify.還款日期.iloc[i]+'\n撥券日期:'+    notify.撥券日期.iloc[i]+'\n承銷股數(張):'+str(notify['承銷股數(張)'].iloc[i])+    '\n\n'
    
    L=len(m1) // 500
    if L == 0:
        lineNotifyMessage(token,'\n'+m1)
    else:
        for jj in range(0,L+1):
            if jj == L:
                lineNotifyMessage(token,'\n'+m1[(500*jj):])
            else:
                lineNotifyMessage(token,'\n'+m1[(500*jj):(500*(jj+1))])


# In[ ]:


print('All done!~')

