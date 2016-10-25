# -*- coding: utf-8 -*-

import sys
import pandas as pd
import math
import json
from datetime import datetime
import time
import httplib
import urllib
import urlparse
 
def request(url, cookie=''):
    ret = urlparse.urlparse(url)    # Parse input URL
    if ret.scheme == 'http':
        conn = httplib.HTTPConnection(ret.netloc)
    elif ret.scheme == 'https':
        conn = httplib.HTTPSConnection(ret.netloc)
        
    url = ret.path
    if ret.query: url += '?' + ret.query
    if ret.fragment: url += '#' + ret.fragment
    if not url: url = '/'
    
    conn.request(method='GET', url=url , headers={'Cookie': cookie})
    return conn.getresponse()

def download():
    stock_se = pd.Series()
    from_se = pd.Series()
    to_se = pd.Series()
    from_w_se = pd.Series()
    to_w_se = pd.Series()
    cash_se = pd.Series()
    df = pd.DataFrame()
    for page in range(1,19):
        symbol = "ZH185989"
        url = "https://xueqiu.com/cubes/rebalancing/history.json?cube_symbol="+symbol+"&count=50&page="
        cookie = "s=1uwp11x35a; webp=1; bid=4f8ee7b806294638bf77397567a97853_ipkyso9i; Hm_lvt_63c1867417313f92f41e54d6ef61187d=1469718651; xq_a_token=cbabd3de1ca40b554e70013098d40313ab05b62d; xqat=cbabd3de1ca40b554e70013098d40313ab05b62d; xq_r_token=4ed48dc694c6e60e85387bbed320dbae7e39938b; xq_token_expire=Tue%20Nov%2015%202016%2019%3A19%3A32%20GMT%2B0800%20(CST); xq_is_login=1; u=6302670150; __utma=1.890576483.1465735988.1477198248.1477217644.99; __utmz=1.1472304532.38.3.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; snbim_minify=true; Hm_lvt_1db88642e346389874251b5a1eded6e3=1477136275,1477190256,1477235996,1477311018; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1477311831"
        data = request(url+str(page),cookie)
        jsonObj = json.loads(data.read())
        for rebalance in jsonObj["list"]:
            if rebalance["status"] == "success":
                items = rebalance["rebalancing_histories"]
                cash = rebalance["cash_value"]
                for item in items:
                    timeStp = item["updated_at"]
                    ltime=time.localtime(timeStp/1000.0) 
                    timeStr=time.strftime("%Y-%m-%d %H:%M:%S", ltime)
                    prev_value = item["prev_net_value"]
                    stock = item["stock_symbol"]
                    value = item["net_value"]
                    weight = item["weight"]
                    prev_weight = item["prev_weight_adjusted"]
                    cash_se[timeStr] = cash
                    # rebalance_type = ""
                    if prev_value is None and value > 0:
                        # rebalance_type = "BUY"
                        from_se[timeStr] = 0
                        from_w_se[timeStr] = 0
                    else:
                        from_se[timeStr] = prev_value
                        from_w_se[timeStr] = prev_weight

                    to_w_se[timeStr] = weight   
                    to_se[timeStr] = value
                    stock_se[timeStr] = stock
            else:
                print rebalance["status"]
    df["stock"] = stock_se
    df["from"] = from_se
    df["to"] = to_se
    df["from_w"] = from_w_se
    df["to_w"] = to_w_se
    df["cash"] = cash_se
    df.to_csv("data.csv")
    print df.head(20)

download()