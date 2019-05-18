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
