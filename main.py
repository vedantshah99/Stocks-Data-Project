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

#driver setup
chrome_driver = 'C:\webdrivers\chromedriver.exe'
profile_path = r'C:\Users\aayur\AppData\Roaming\Mozilla\Firefox\Profiles\tc9vu9fu.default'
options=Options()
options.set_preference('profile', profile_path)
service = Service(r'C:\webdrivers\geckodriver.exe')

#driver = Firefox(service=service, options=options)
driver = webdriver.Firefox(service=service, options=options)
driver.get('https://www.sec.gov/edgar/search/#/q=covid&dateRange=custom&startdt=2017-06-26&enddt=2020-05-27')

def variance(data):
    n = len(data)
    mean = sum(data) / n
    deviations = [(x - mean) ** 2 for x in data]
    variance = sum(deviations) / n
    return variance

def findVar(ticker, startDate, endDate):
    driver.execute_script("window.open('https://finance.yahoo.com/', 'new_window')")
    driver.switch_to.window(driver.window_handles[1])

    #closing pop-up and typing in company name
    time.sleep(3)
    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    time.sleep(3)
    print(ticker)
    searchBoxYahoo = driver.find_element(By.ID, "yfin-usr-qry")
    searchBoxYahoo.send_keys(ticker)
    searchBoxYahoo.send_keys(Keys.RETURN)
    time.sleep(4)

    #click on historical data
    histDataButton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="quote-nav"]/ul/li[6]')))
    histDataButton.click()
    #time.sleep(5)

    #choose dates button
    time.sleep(3)
    dates = driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/div/div/div/span')
    driver.execute_script("window.scrollTo(0, (document.body.scrollHeight)/2)")
    dates.click()
    time.sleep(3)


    #choosing the start and end dates
    initial = driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/div[1]/input')
    initial.send_keys(Keys.ENTER)
    startDateReader = driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/div[2]/input')
    ActionChains(driver).move_to_element(startDateReader).send_keys(startDate).perform()
    startDateReader.send_keys('02/02/2002')
    endDateReader = driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/div[2]/input')
    ActionChains(driver).move_to_element(endDateReader).send_keys(endDate).perform()
    time.sleep(2)
    #endDateReader.send_keys(endDate)

    #click on done button
    done = driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/div[3]/button[1]')
    ActionChains(driver).move_to_element(done).click().perform()
    time.sleep(2)

    #click on apply button
    apply = driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/button')
    apply.click()
    time.sleep(2)

    #collecting data
    data = []
    i = 1
    while i < 10:
        xpath = '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr['+str(i)+']/td[5]/span'
        input = driver.find_element(By.XPATH, xpath).text
        print(input)
        data.append(float(input))
        i+=1
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return variance(data)

searchbox = driver.find_element(by=By.ID, value='entity-short-form')
searchbox.send_keys('covid')
searchbox.send_keys(Keys.RETURN)

button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'headingTwo2')))
button.click()

tenq = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div[2]/div[1]/div[2]/div[2]/div[2]/div/table/tbody/tr[2]/td/a')))
tenq.click()
time.sleep(2)

docs = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "preview-file"))
)

#adding company names to list
companies = []
variances = []
temps = driver.find_elements(By.CLASS_NAME, "entity-name")
i =1
while i < 10:
    t = temps[i].text
    if t.find("(") >= 0:
        tick = t[t.find("(")+1:t.find(")")]
        tick = tick[tick.find(" ")+1:len(tick)]
        companies.append(tick)
        variances.append(findVar(tick, '03/13/2020', '05/27/2020'))
    else:
        print(t)
        docs.remove(docs[i])
    i+=1

#adding covid counts to list
i = 0
counts = []
while i < 10:
    #click on each 10Q form
    docs[i].click();
    time.sleep(2)

    #count number of times COVID was mentioned
    count = driver.find_element(By.CLASS_NAME, "find-counter").text
    count = count[5:len(count)]
          #print(companies[i] + ": " + count)
    counts.append(int(count))

    time.sleep(1)

    #close the preview
    close = driver.find_element(By.CLASS_NAME, "close")
    close.click()

    i = i+1

with open('list.csv','w') as file:
    writer = csv.writer(file)
    writer.writerow(companies)
    writer.writerow(counts)
    writer.writerow(variances)