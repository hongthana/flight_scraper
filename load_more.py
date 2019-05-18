def load_more():
    """
    ฟังก์ชั่นใช้สำหรับโหลดผลลัพธ์เพิ่มเติม
    """
    try:
        more_results = '//a[@class="moreButton"]'
        driver.find_element_by_xpath(more_results).click()
        print('ดีเลย์ 45 ถึง 60 วินาที .....')
        sleep(randint(45, 60))
    except:
        pass
