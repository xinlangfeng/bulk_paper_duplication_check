import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys

def get_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('headless')    
    if getattr(sys, 'frozen', False):
        # chromedriver_path = os.path.join(sys._MEIPASS, "chromedriver.exe")
        chromedriver_path = os.path.join(sys._MEIPASS, "chromedriver.exe")
        driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
    else:
        driver = webdriver.Chrome(executable_path='chromedriver.exe', options=options)
    
    driver.set_window_size(1920, 1080)
    return driver

def get_cookies():
    driver = get_driver()
    driver.get('https://www.paperday.cn/paper/uploadText.html')
    time.sleep(20)
    cookies = driver.get_cookies()
    jsonCookie = json.dumps(cookies)
    with open('cookies.txt','w') as f:
        f.write(jsonCookie)

def duplication_check():
    driver = get_driver()
    driver.get('https://www.paperday.cn/paper/uploadText.html')    
    wait = WebDriverWait(driver, 3600)
    wait.until(EC.presence_of_element_located((By.ID, 'uploadPaper')))  

    for i, paper_path in enumerate(os.listdir('papers')):        
        paper_file = os.path.abspath(os.path.join('papers', paper_path))
        file_upload_input = wait.until(EC.presence_of_element_located((By.ID, 'uploadPaper')))
        file_upload_input.clear()
        #上传文档
        file_upload_input.send_keys(paper_file)
        time.sleep(10)
        wait.until(EC.presence_of_element_located((By.ID, 'submit_check_task')))
        driver.find_element(By.ID,'submit_check_task').click()
        wait.until(EC.presence_of_element_located((By.ID, 'recharge')))
        # 取消所有付费项
        driver.find_element(By.CSS_SELECTOR,'div.modal-type').click()
        driver.find_element(By.ID,'jqjcCheckInput').click()
        driver.find_element(By.ID,'correctCheckInput').click()
        driver.find_element(By.ID,'speedCheckInput').click()
        driver.find_element(By.XPATH,"//div[@class='web multversions xueshuversion on']").click()
        wait.until(EC.presence_of_element_located((By.ID, 'check')))        
        time.sleep(3)
        driver.find_element(By.ID,'check').click()
        # 等待检测完成
        wait.until(EC.text_to_be_present_in_element((By.XPATH, "//tbody[@class='paragraph']/tr[1]/td[3]/ul/li/span"), "检测完成"))
        time.sleep(3)
        # 获取查重率并重命名本地文件
        duplication_rate = driver.find_element(By.XPATH,"//tbody[@class='paragraph']/tr[1]/td[5]/ul/li").text        
        new_name = os.path.abspath(os.path.join('papers', duplication_rate + '@' + paper_path))
        os.rename(paper_file, new_name)
        #回到查重上传页
        driver.find_element(By.XPATH,"//a[@href='/paper/uploadText.html']").click()
    
    driver.quit()


duplication_check()