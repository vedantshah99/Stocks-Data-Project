from ast import expr_context
from xml.dom.minidom import Element #git is fire af
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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
import re


#driver setup
chrome_driver = 'C:\webdrivers\chromedriver.exe'
profile_path = r'C:\Users\aayur\AppData\Roaming\Mozilla\Firefox\Profiles\tc9vu9fu.default'
options=Options()
options.set_preference('profile', profile_path)
service = Service(r'C:\webdrivers\geckodriver.exe')
failed = []

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
    driver.execute_script(f"window.open('https://finance.yahoo.com/quote/{ticker}/history?p={ticker}', 'new_window')")
    
    driver.switch_to.window(driver.window_handles[1])

    #choose dates button
    time.sleep(3)
    try:
        dates = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/div/div/div/span')))
        driver.execute_script("window.scrollTo(0, (document.body.scrollHeight)/2)")
        dates.click()
    except TimeoutException:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        print("Timeout Exception for: " + ticker)
        failed.append("Timeout Exception for: " + ticker)
        return -1
    except NoSuchElementException:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        print("Dates not found for: " + ticker)
        failed.append("Dates not found for: " + ticker)
        return -1
    time.sleep(3)

    #choosing the start and end dates
    try:
        initial = driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/div[1]/input')
        initial.send_keys(Keys.ENTER)
        startDateReader = driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/div[2]/input')
        ActionChains(driver).move_to_element(startDateReader).send_keys(startDate).perform()
        startDateReader.send_keys('02/02/2002')
        endDateReader = driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/div[2]/input')
        ActionChains(driver).move_to_element(endDateReader).send_keys(endDate).perform()
        time.sleep(2)
    except:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        print("Start & End Dates not found for: " + ticker)
        failed.append("Start & End Dates not found for: " + ticker)
        return -1
    #endDateReader.send_keys(endDate)

    #click on done button
    try:
        done = driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/div[3]/button[1]')
        ActionChains(driver).move_to_element(done).click().perform()
        time.sleep(2)
    except NoSuchElementException:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        print("Done Button not found for: " + ticker)
        failed.append("Done Button not found for: " + ticker)
        return -1

    #click on apply button
    apply = driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/button')
    apply.click()
    time.sleep(2)

    #collecting data
    data = []
    i = 1
    while i < 10:
        xpath = '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr['+str(i)+']/td[5]/span'
        try:
            input = driver.find_element(By.XPATH, xpath).text
        except NoSuchElementException:
            i+=1
            continue
        data.append(float(input.replace(",","")))
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
listOfCompanyNames = driver.find_elements(By.CLASS_NAME, "entity-name")

for i in range(1,len(listOfCompanyNames)):
    print(i)
    fullCompanyName = listOfCompanyNames[i].text
    if fullCompanyName.find("(") >= 0:
        tick = fullCompanyName[fullCompanyName.find("(")+1:fullCompanyName.find(")")]
        tick = tick[tick.find(" ")+1:len(tick)]
        companies.append(tick)
        variances.append(findVar(tick, '03/13/2020', '05/27/2020'))
    else:
        companies.append("N/A")
        variances.append("N/A")
        print("Couldn't find ticker for: "+ fullCompanyName)
        #docs.remove(docs[i])
        failed.append("Couldn't find ticker for: "+ fullCompanyName)

with open('fails.csv','w', newline='') as file:
        writer = csv.writer(file)
        for val in failed:
            writer.writerow([val])

#adding covid counts to list
counts = []

for i in range(len(docs)):
    #click on each 10Q form
    docs[i].click();
    time.sleep(2)
    #count number of times COVID was mentioned
    try:
        count = driver.find_element(By.CLASS_NAME, "find-counter").text
        count = count[5:len(count)]
        counts.append(int(count))
    except:
        close = driver.find_element(By.CLASS_NAME, "close")
        close.click()
        counts.append(-1)
        continue

    time.sleep(1)

    #close the preview
    close = driver.find_element(By.CLASS_NAME, "close")
    close.click()

print("docs: " + str(len(docs)))
print("companies: " + str(len(companies)))
print("counts: " + str(len(counts)))
print("variances: " + str(len(variances)))

with open('list.csv','w', newline='') as file:
    writer = csv.writer(file)
    for i in range(len(companies)):
        if companies[i] != 'N/A' and counts[i] != -1 and variances[i] != -1:
            writer.writerow([str(companies[i])]+ [str(counts[i])] + [str(variances[i])])