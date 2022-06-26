from xml.dom.minidom import Element
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from selenium.webdriver.common.action_chains import ActionChains
import time
from bs4 import BeautifulSoup
import requests
import csv

def variance(data):
    n = len(data)
    mean = sum(data) / n
    deviations = [(x - mean) ** 2 for x in data]
    variance = sum(deviations) / n
    return variance

chrome_driver = 'C:\webdrivers\chromedriver.exe'
profile_path = r'C:\Users\aayur\AppData\Roaming\Mozilla\Firefox\Profiles\tc9vu9fu.default'
options=Options()
options.set_preference('profile', profile_path)
service = Service(r'C:\webdrivers\geckodriver.exe')

#driver = Firefox(service=service, options=options)
finance_driver = webdriver.Firefox(service=service, options=options)

finance_driver.get('https://finance.yahoo.com/quote/INCY/history?p=INCY')

def findVar(ticker, startDate, endDate):
    #choose dates button
    time.sleep(3)
    dates = finance_driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/div/div/div/span')
    finance_driver.execute_script("window.scrollTo(0, (document.body.scrollHeight)/2)")
    dates.click()
    time.sleep(3)

    #choosing the start and end dates
    initial = finance_driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/div[1]/input')
    initial.send_keys(Keys.ENTER)
    startDateReader = finance_driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/div[2]/input')
    ActionChains(finance_driver).move_to_element(startDateReader).send_keys(startDate).perform()
    startDateReader.send_keys('02/02/2002')
    endDateReader = finance_driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/div[2]/input')
    ActionChains(finance_driver).move_to_element(endDateReader).send_keys(endDate).perform()
    time.sleep(2)
    #endDateReader.send_keys(endDate)

    #click on done button
    done = finance_driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/div[3]/button[1]')
    ActionChains(finance_driver).move_to_element(done).click().perform()
    time.sleep(2)

    #click on apply button
    apply = finance_driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/button')
    apply.click()
    time.sleep(2)

    #collecting data
    data = []
    i = 1
    while i < 10:
        xpath = '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr['+str(i)+']/td[5]/span'
        input = finance_driver.find_element(By.XPATH, xpath).text
        print(input)
        data.append(float(input))
        i+=1
    print(str(variance(data)))

findVar('INCY', '03/13/2020', '05/27/2020')
