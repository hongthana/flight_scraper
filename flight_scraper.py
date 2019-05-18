#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Kayak Web Scraper based on Fàbio Neves
"If you like to travel, let Python help you scrape the best cheap flights!"
https://towardsdatascience.com/if-you-like-to-travel-let-python-help-you-scrape-the-best-fares-5a1f26213086

"""
from time import sleep, strftime
from random import randint
from selenium import webdriver
from email.mime.multipart import MIMEMultipart
import pandas as pd
import smtplib

# กรอกข้อมูลการเดินทาง
city_from = input('สนามบินต้นทาง : (เช่่น BKK) ')
city_to = input('สนามบินปลายทาง : (เช่น LHR) ')
date_start = input('วันที่ออกเดินทาง : (yyyy-mm-dd) ')
date_return = input('วันที่เดินทางกลับ : (yyyy-mm-dd) ')

# For debugging
#city_from = 'BKK'
#city_to = 'SIN'
#date_start = '2019-05-22'
#date_return = '2019-06-09'

# กำหนดให้โปรแกรมทำงานทุกๆ 4 ชั่วโมง จำนวน 4 ครั้ง
for n in range(0, 5):
    # รันฟังก์ชั่น open_kayak เพื่อเริ่มดึงราคา
    open_kayak(city_from, city_to, date_start, date_return)
    print('ดึงข้อมูลครั้งที่ {} สำเร็จเมื่อ @ {}'.format(n, strftime("%Y-%m-%d - %H:%M")))    
    # กำหนดให้รอ 4 ชั่วโมง
    sleep(60 * 60 * 4)
    print('ครบ 4 ชั่วโมงแล้ว')
    
# ดาวน์โหลด "chrome driver" ที่ http://chromedriver.chromium.org/
# ต้องดาวน์โหลด chromedriver ให้ตรงกับ Chrome ที่ใช้งานอยู่
    
# ไดเร็กทอรี่เก็บไฟล์ chromedriver.exe สำหรับ windows
# chromedriver_path = 'C:/{YOUR PATH HERE}/chromedriver_win32/chromedriver.exe'
    
# ไดเร็กทอรี่เก็บไฟล์ chromedriver สำหรับ mac
# chromedriver_path = '/{YOUR PATH HERE}/chromedriver'

# เปิด Chrome เบราว์เซอร์
driver = webdriver.Chrome(executable_path = chromedriver_path)
sleep(2)
