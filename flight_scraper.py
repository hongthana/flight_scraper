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
    #start_scrape(city_from, city_to, date_start, date_return)
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

# รันฟังก์ชั่น open_kayak เพื่อเริ่มดึงราคา
open_kayak(city_from, city_to, date_start, date_return)

# "PAGE SCRAPE" function
def page_scrape():
    """
    ฟังก์ชั่นสำหรับดึงข้อมูลบนเว็บไซต์ Kayak
    """
    xpath_sections = '//*[@class="section duration"]'
    sections = driver.find_elements_by_xpath(xpath_sections)
    sections_list = [value.text for value in sections]
    # แยกระหว่างเที่ยวบินขาออก (o) และเที่ยวบินขาเข้า (i)
    section_out_list = sections_list[::2]
    section_in_list = sections_list[1::2]
    
    # if you run into a reCaptcha, you might want to do something about it
    # you will know there's a problem if the lists above are empty
    # this if statement lets you exit the bot or do something else
    # you can add a sleep here, to let you solve the captcha and continue scraping
    # i'm using a SystemExit because i want to test everything from the start
    if section_out_list == []:
        raise SystemExit   
    
    out_duration = []
    out_section_names = []
    for n in section_out_list:
        # แยกข้อมูลเวลากับสนามบินขาออก
        out_duration.append(''.join(n.split()[0:2]))
        out_section_names.append(''.join(n.split()[2:5]))
    
    in_duration = []
    in_section_names = []
    for n in section_in_list:
        # แยกข้อมูลเวลากับสนามบินขาเข้า
        in_duration.append(''.join(n.split()[0:2]))
        in_section_names.append(''.join(n.split()[2:5]))
    
    xpath_dates = '//div[@class="section date"]'
    dates = driver.find_elements_by_xpath(xpath_dates)
    dates_list = [value.text for value in dates]
    out_date_list = dates_list[::2]
    in_date_list = dates_list[1::2]
    
    # แยกข้อมูล Weekday จาก day
    out_day = [value.split()[0] for value in out_date_list]
    out_weekday = [value.split()[1] for value in out_date_list]
    in_day = [value.split()[0] for value in in_date_list]
    in_weekday = [value.split()[1] for value in in_date_list]
    
    # ดึงราคาตั๋วเครื่องบิน
    # xpath_prices = '//a[@class="booking-link"]/span[@class="price option-text"]' #ดึงราคาของ Kiwi.com มาด้วย ทำให้ error
    #xpath_prices = '//div[contains(@id,"price-bookingSection")]'
    xpath_prices = '//div[contains(@id,"price-bookingSection")]//span[@class="price option-text"]'
    prices = driver.find_elements_by_xpath(xpath_prices)
    # เอาสัญลักษณ์ค่าเงินบาท "฿" ออก โดยใช้ if เช็คว่ามีค่าอยู่ในตัวแปร price
    prices_list = [price.text.replace('฿ ', '').replace(',', '') for price in prices if price.text != '']
    # แปลง price_list ให้เป็น int
    prices_list = list(map(int, prices_list))
    
    # the stops are a big list with one leg on the even index and second leg on odd index
    xpath_stops = '//div[@class="section stops"]/div[1]'
    stops = driver.find_elements_by_xpath(xpath_stops)
    stops_list = [stop.text[0].replace('n','0') for stop in stops]
    out_stop_list = stops_list[::2]
    in_stop_list = stops_list[1::2]
    
    xpath_stops_cities = '//div[@class="section stops"]/div[2]'
    stops_cities = driver.find_elements_by_xpath(xpath_stops_cities)
    stops_cities_list = [stop.text for stop in stops_cities]
    out_stop_name_list = stops_cities_list[::2]
    in_stop_name_list = stops_cities_list[1::2]
    
    # ดึงชื่อสายการบิน เวลาเครื่องออก เวลาเครื่องลง สำหรับขาออกและขาเข้า
    xpath_schedule = '//div[@class="section times"]'
    schedules = driver.find_elements_by_xpath(xpath_schedule)
    hours_list = []
    airlines_list = []
    for schedule in schedules:
        hours_list.append(schedule.text.split('\n')[0])
        airlines_list.append(schedule.text.split('\n')[1])
    
    # แยกชื่อสายการบินและเวลา สำหรับขาออกและขาเข้า
    out_hours = hours_list[::2]
    out_airlines = airlines_list[1::2]
    in_hours = hours_list[::2]
    in_airlines = airlines_list[1::2]
        
    cols = (['Out Day', 'Out Weekday', 'Out Duration', 'Out Cities', 'Return Day', 
             'Return Weekday', 'Return Duration', 'Return Cities', 'Out Stops', 
             'Out Stop Cities', 'Return Stops', 'Return Stop Cities', 
             'Out Time', 'Out Airline', 'Return Time', 
             'Return Airline', 'Price'])
    
    # สร้าง dictionary สำหรับเก็บข้อมูลทั้งหมด
    flights_df = pd.DataFrame({'Out Day': out_day,
                               'Out Weekday': out_weekday,
                               'Out Duration': out_duration,
                               'Out Cities': out_section_names,
                               'Return Day': in_day,
                               'Return Weekday': in_weekday,
                               'Return Duration': in_duration,
                               'Return Cities': in_section_names,
                               'Out Stops': out_stop_list,
                               'Out Stop Cities': out_stop_name_list,
                               'Return Stops': in_stop_list,
                               'Return Stop Cities': in_stop_name_list,
                               'Out Time': out_hours,
                               'Out Airline': out_airlines,
                               'Return Time': in_hours,
                               'Return Airline': in_airlines,                           
                               'Price': prices_list})[cols]
    
    flights_df['timestamp'] = strftime("%Y-%m-%d-%H:%M") # so we can know when it was scraped
    return flights_df

# เปิดเว็บ Kayak และใส่ข้อมูลการเดินทางที่กำหนดไว้ด้านบน
# "Open Kayak" function
def open_kayak(city_from, city_to, date_start, date_return):
    """
    City codes follow IATA
    Date format as YYYY-MM-DD
    """
    # กำหนด url ของเว็บไซต์ Kayak
    kayak_address = ('https://www.kayak.co.th/flights/' + city_from + '-' 
                     + city_to + '/' + date_start + '-flexible/' + date_return
                     + '-flexible?sort=bestflight_a')
    # สั่งให้ Chrome เปิดเว็บไซต์ Kayak
    driver.get(kayak_address)
    # ดีเลย์ประมาณ 15-20 วินาที เพื่อให้โหลดข้อมูล
    print('ดีเลย์ 15 ถึง 20 วินาที .....')
    sleep(randint(15, 20))
    
    # ปิดหน้าต่าง popup ถ้าแสดงขึ้นมา
    driver.refresh()
    
    print('ดีเลย์ 50 ถึง 60 วินาที .....')
    sleep(randint(50, 60))
    print('+++ แสดงผลเพิ่มเติม +++')
    load_more()
    
    print('เริ่มดึงข้อมูลเที่ยวบิน เรียงตามลำดับดีที่สุด')
    df_flights_best = page_scrape()
    # เพิ่มคอลัมน์ "sort" และใส่ค่า "best" ใน df_flight_best
    df_flights_best['sort'] = 'best'
    # ดีเลย์ประมาณ 60-80 วินาที
    print('ดีเลย์ 60 ถึง 80 วินาที .....')
    sleep(randint(60, 80))
    
    # ดึงค่าโดยสารในตารางด้านบนสุด (ค่าโดยสารวันที่ยืดหยุ่น +-3 วัน)
    table = driver.find_elements_by_xpath('//*[contains(@id,"FlexMatrixCell")]')
    # ลบสัญลักษณ์ค่าเงินบาท ฿
    price_table = [price.text.replace('฿ ', '').replace(',', '') for price in table]
    # เปลี่ยนค่าใน price_table ให้เป็น int
    price_table = list(map(int, price_table))
    price_min = min(price_table)
    price_avg = sum(price_table)/len(price_table)
    
    print('เรียงตามราคาต่่ำที่สุด')
    cheapest = '//a[@data-code = "price"]'
    driver.find_element_by_xpath(cheapest).click()
    # ดีเลย์ประมาณ 60-90 วินาที
    print('ดีเลย์ 60 ถึง 90 วินาที .....')
    sleep(randint(60, 90))
    print('+++ แสดงผลเพิ่มเติม +++')
    load_more()
    
    print('เริ่มดึงข้อมูลเที่ยวบิน เรียงตามราคาต่่ำที่สุด')
    df_flights_cheap = page_scrape()
    df_flights_cheap['sort'] = 'cheap'
    # ดีเลย์ประมาณ 60-80 วินาที
    print('ดีเลย์ 60 ถึง 80 วินาที .....')
    sleep(randint(60, 80))
    
    print('เรียงตามเวลาเดินทางเร็วสุด')
    fastest = '//a[@data-code = "duration"]'
    driver.find_element_by_xpath(fastest).click()
    # ดีเลย์ประมาณ 60-00 วินาที
    print('ดีเลย์ 60 ถึง 90 วินาที .....')
    sleep(randint(60, 90))
    print('+++ แสดงผลเพิ่มเติม +++')
    load_more()
    
    print('เริ่มดึงข้อมูลเที่ยวบิน เรียงตามเวลาเดินทางเร็วสุด')
    df_flights_fast = page_scrape()
    df_flights_fast['sort'] = 'fast'
    print('ดีเลย์ 60 ถึง 80 วินาที .....')
    sleep(randint(60, 80))
    
    # บันทึกดาต้าเฟรมเป็นไฟล์ excel
    result_price = df_flights_best.append(df_flights_cheap).append(df_flights_fast)
    result_price.to_excel('airfair//{}_flights_{}-{}_from_{}_to_{}.xlsx'.format(strftime("%Y-%m-%d_%H%M"), 
                          city_from, city_to, date_start, date_return), index = False)
    print('บันทึกข้อมูลเป็น excel')
    
    # บันทึกคำแนะนำแนวโน้มราคาค่าโดยสาร
    xpath_advice = '//div[contains(@id,"advice")]'
    advice = driver.find_element_by_xpath(xpath_advice).text
    xpath_predict = '//span[@class="info-text"]'
    predict = driver.find_element_by_xpath(xpath_predict).text
    print(advice + '\n' + predict)
    
    # บางครั้งค่าในตัวแปร advice เป็นตัวสัญลักษณ์แปลกๆ ให้เปลี่ยนเป็น "ไม่มีข้อมูล"
    ignore = '¯\(°_O)/¯'
    if advice == ignore:
        advice = 'ไม่มีข้อมูล'
        
    # ส่งอีเมล์ไฟล์ excel ใช้ hotmail
    username = 'YOUR_EMAIL@hotmail.com'
    password = 'YOUR_PASSWORD'
    
    server = smtplib.SMTP('smtp.outlook.com', 587)
    server.ehlo()
    server.starttls()
    server.login(username, password)
    msg = ('Subject: Flight Scraper\n\nCheapest Flight: {}\nAverage Price: {}\n\nRecommendation: {}\n\nEnd of message'.format(price_min, price_avg, (advice + '\n' + predict)))
    message = MIMEMultipart()
    message['From'] = username
    message['to'] = username
    server.sendmail(username, username, msg)
    print('กำลังส่งอีเมล์')
