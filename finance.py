from xml.dom.minidom import Element
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from selenium.webdriver.common.action_chains import ActionChains
import time

def variance(data):
    n = len(data)
    mean = sum(data) / n
    deviations = [(x - mean) ** 2 for x in data]
    variance = sum(deviations) / n
    return variance

chrome_driver = 'C:\\Users\\aayur\\OneDrive\\Desktop\\Drivers\\chromedriver.exe'
finance_driver = webdriver.Chrome(chrome_driver)

finance_driver.get('https://finance.yahoo.com/')

def findVar(ticker, startDate, endDate):
    time.sleep(2)
    webdriver.ActionChains(finance_driver).send_keys(Keys.ESCAPE).perform()
    time.sleep(2)
    searchBoxYahoo = finance_driver.find_element(By.ID, "yfin-usr-qry")
    searchBoxYahoo.send_keys(ticker)
    searchBoxYahoo.send_keys(Keys.RETURN)
    time.sleep(4)

    #click on historical data
    histDataButton = finance_driver.find_element(By.XPATH, '//*[@id="quote-nav"]/ul/li[6]')
    histDataButton.click()
    time.sleep(3)

    #choose dates button
    dates = finance_driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/div/div/div/span')
    dates.click()
    time.sleep(3)

    #choosing the start and end dates
    startDateReader = finance_driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/div[1]/input')
    startDateReader.send_keys(startDate)
    endDateReader = finance_driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/div[2]/input')
    endDateReader.send_keys(endDate)

    #click on done button
    done = finance_driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/div[3]/button[1]')
    done.click()
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
