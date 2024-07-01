import streamlit as st
import time
import datetime
import pytz  # Import pytz for time zone support
import streamlit_antd_components as sac
import requests
import pandas as pd
from streamlit.components.v1 import html

#주식관련
#import requests
import bs4 as bs
import urllib3
import ast
import re
#======================var START=========================

# Define market timezones and hours
korean_tz = pytz.timezone("Asia/Seoul")
us_tz = pytz.timezone("America/New_York")
korean_market_open = datetime.time(9, 0, 0)  # 9:00 AM KST
korean_market_close = datetime.time(15, 30, 0)  # 3:30 PM KST
us_market_open = datetime.time(9, 30, 0)  # 9:30 AM ET
us_market_close = datetime.time(16, 0, 0)  # 4:00 PM ET
kor_market_open_flag = 0
#======================var END=========================

#===========Stock START=============
# 1. 종목 데이터 가져오기
def get_all_info(company_code):
    html = connect_finance_page(company_code)
    current_info = html.find("dl", {"class": "blind"})
    current_info = change_info_format(current_info.find_all("dd"))  # dict 형태로 변경
    return current_info

# 1-1. url 연결
def connect_finance_page(company_code):
    url = "https://finance.naver.com/item/main.nhn?code=" + company_code
    resp = requests.get(url)
    soup = bs.BeautifulSoup(resp.text, "html.parser")
    return soup

# 1-2. 종목 데이터 리스트 -> 사전 형태로 변경
def change_info_format(current_info):
    info_dictionary = {"Date": current_info[0].get_text()}
    current_info.remove(current_info[0])
    for item in current_info:
        text = item.get_text()
        # '종목명'에 해당하는 경우, 전체 문자열을 저장
        if '종목명' in text:
            info_dictionary['종목명'] = text.replace('종목명', '').strip()
        else:
            # 다른 항목들에 대해서는 원래 코드를 유지
            split_text = text.split()
            if len(split_text) > 1:
                info_dictionary[split_text[0]] = split_text[1]
    return info_dictionary

#주식 메인 표
def update_stock_data():
    # 주식 관련
    stock_data = []
    
    #global stock_array
    stock_input = "005930, 305720, 305540, 174360, 448330, 003620, 133690" #★★★★★★★★★★★★★종목입력★★★★★★★★★★★★★
    stock_input_tmp = stock_input.replace(" ", "")
    stock_array = stock_input_tmp.split(",") #string to Array
    stock_number = len(stock_array)    

    for code in stock_array:    
        stock_data.append(get_all_info(code))

    st_trade_name = []
    st_trade_price = []
    st_signed_change_price = []
    st_signed_change_rate = []
    st_up_down = []
    st_trade_time = []
    st_trade_time_status = []
    
    #현재가
    st_trade_name = [stock_data[i]['종목명'] for i in range(stock_number)]
    st_trade_price = [int(stock_data[i]['현재가'].replace(',', '')) for i in range(stock_number)]
    st_signed_change_price = [int(stock_data[i]['현재가'].replace(',', '')) - int(stock_data[i]['전일가'].replace(',', '')) for i in range(stock_number)]
    st_signed_change_rate = ["{:.2f}%".format((float(stock_data[i]['현재가'].replace(',', '')) - float(stock_data[i]['전일가'].replace(',', '')))/float(stock_data[i]['전일가'].replace(',', '')) * 100) for i in range(stock_number)]
    
    #for문 같이 씀
    for i in range(stock_number):
        #업 다운
        if st_signed_change_price[i] > 0:
            st_up_down_tmp = "▲"
        elif st_signed_change_price[i] < 0:
            st_up_down_tmp = "▽"
        else:
            st_up_down_tmp = "〓"
        st_up_down.append(st_up_down_tmp)
        
        #거래시간
        # stock_number 만큼 반복
        data = stock_data[i]['Date']
        # 정규 표현식을 사용하여 날짜와 시간, 상태 추출
        match = re.search(r'(\d{4})년 (\d{2})월 (\d{2})일 (\d{2})시 (\d{2})분 기준 (\S+)', data)
        if match:
            year, month, day, hour, minute, status = match.groups()
    
            # 날짜 객체 생성
            date_obj = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))
    
            # 날짜와 요일을 포맷팅
            var1 = date_obj.strftime('%Y-%m-%d(%a) %H:%M')
            var2 = status
    
            # 추출한 값을 리스트에 추가
            st_trade_time.append(var1)
            st_trade_time_status.append(var2)
            
    #Dataframe 뿌려주기(초기값)
    stock_df = pd.DataFrame({'Name': st_trade_name, 'Price': st_trade_price, 'Trd': st_up_down, '%': st_signed_change_rate, 'Change': st_signed_change_price, 'Tr. Time': st_trade_time, 'Status': st_trade_time_status})
    stock_df_sorted = stock_df.sort_values(by=['Price'], ascending=False)
    stock_dataframe.dataframe(stock_df_sorted, hide_index=True, use_container_width=True)

#===========Stock END=============

st.set_page_config(page_title="Demo 입니당")

while True:
    update_stock_data()
    time.sleep(1)
