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
    # popup_close() REPLACED BY DRIVER.REFRESH()
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
    password = 'YOUR_PASSWORK'
    
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
