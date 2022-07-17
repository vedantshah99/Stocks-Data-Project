from ast import expr_context
from lib2to3.pgen2 import driver
from xml.dom.minidom import Element
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

companies = []
counts = []
variances = []
failed = []

class Scrape():
    #driver setup
    def driverSetup(self):
        chrome_driver = 'C:\webdrivers\chromedriver.exe'
        profile_path = r'C:\Users\aayur\AppData\Roaming\Mozilla\Firefox\Profiles\tc9vu9fu.default'
        options=Options()
        options.set_preference('profile', profile_path)
        service = Service(r'C:\webdrivers\geckodriver.exe')

        self.driver = webdriver.Firefox(service=service, options=options)
        self.driver.get('https://www.sec.gov/edgar/search/#/q=covid&dateRange=custom&startdt=2017-06-26&enddt=2020-05-27')

    #calculate variance
    def variance(data):
        n = len(data)
        mean = sum(data) / n
        deviations = [(x - mean) ** 2 for x in data]
        variance = sum(deviations) / n
        return variance

    #find variance
    def findVar(self, ticker, startDate, endDate):
        #open yahoo finance
        self.driver.execute_script(f"window.open('https://finance.yahoo.com/quote/{ticker}/history?p={ticker}', 'new_window')")
        self.driver.switch_to.window(self.driver.window_handles[1])
        time.sleep(3)

        #choose dates button
        try:
            dates = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/div/div/div/span')))
            self.driver.execute_script("window.scrollTo(0, (document.body.scrollHeight)/2)")
            dates.click()
        except TimeoutException:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            print("Timeout Exception for: " + ticker)
            self.failed.append("Timeout Exception for: " + ticker)
            return 0
        except NoSuchElementException:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            print("Dates not found for: " + ticker)
            self.failed.append("Dates not found for: " + ticker)
            return 0
        time.sleep(3)

        #choosing the start and end dates
        try:
            initial = self.driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/div[1]/input')
            initial.send_keys(Keys.ENTER)
            startDateReader = self.driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/div[2]/input')
            ActionChains(self.driver).move_to_element(startDateReader).send_keys(startDate).perform()
            startDateReader.send_keys('02/02/2002')
            endDateReader = self.driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/div[2]/input')
            ActionChains(self.driver).move_to_element(endDateReader).send_keys(endDate).perform()
            time.sleep(2)
        except:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            print("Start & End Dates not found for: " + ticker)
            self.failed.append("Start & End Dates not found for: " + ticker)
            return 0

        #click on done button
        try:
            done = self.driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/div[3]/button[1]')
            ActionChains(self.driver).move_to_element(done).click().perform()
            time.sleep(2)
        except NoSuchElementException:
            self.driver.close()
            self.driver.switch_to.window(driver.window_handles[0])
            print("Done Button not found for: " + ticker)
            self.failed.append("Done Button not found for: " + ticker)
            return 0

        #click on apply button
        apply = self.driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/button')
        apply.click()
        time.sleep(2)

        #collecting data
        data = []
        i = 1
        while i < 10:
            xpath = '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr['+str(i)+']/td[5]/span'
            try:
                input = self.driver.find_element(By.XPATH, xpath).text
            except NoSuchElementException:
                i+=1
                continue
            data.append(float(input.replace(",","")))
            i+=1
        self.driver.close()
        self.driver.switch_to.window(driver.window_handles[0])

        return self.variance(data)

    def navigateSEC(self):
        searchbox = self.driver.find_element(by=By.ID, value='entity-short-form')
        searchbox.send_keys('covid')
        searchbox.send_keys(Keys.RETURN)

        button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'headingTwo2')))
        button.click()

        tenq = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div[2]/div[1]/div[2]/div[2]/div[2]/div/table/tbody/tr[2]/td/a')))
        tenq.click()
        time.sleep(2)

        self.docs = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "preview-file"))
        )

    def addData(self):
        #adding tickers and varainces to lists
        listOfCompanyNames = self.driver.find_elements(By.CLASS_NAME, "entity-name")
        for i in range(1,len(listOfCompanyNames)):
            print(i)
            fullCompanyName = listOfCompanyNames[i].text
            # find ticker symbol and pass it into findVar
            if fullCompanyName.find("(") >= 0:
                tick = fullCompanyName[fullCompanyName.find("(")+1:fullCompanyName.find(")")]
                tick = tick[tick.find(" ")+1:len(tick)]
                companies.append(tick)
                variances.append(self.findVar(tick, '03/13/2020', '05/27/2020'))
            else:
                self.docs.remove(self.docs[i])

    def addCovidCounts(self):
        #adding covid counts to list
        print("docs: " + str(len(self.docs)))
        print("companies: " + str(len(companies)))
        for i in range(len(self.docs)):
            #click on each 10Q form
            self.docs[i].click();
            time.sleep(2)

            #count number of times COVID was mentioned
            try:
                count = self.driver.find_element(By.CLASS_NAME, "find-counter").text
                count = count[5:len(count)]
                counts.append(int(count))
            except:
                close = self.driver.find_element(By.CLASS_NAME, "close")
                close.click()
                counts.append(-1)
                continue

            time.sleep(1)

            #close the preview
            close = self.driver.find_element(By.CLASS_NAME, "close")
            close.click()

def writeFailsToCSV(self):
    with open('fails.csv','w') as file:
            writer = csv.writer(file)
            for val in failed:
                writer.writerow(val)

def writeToCSV(self):
    with open('list.csv','w') as file:
        writer = csv.writer(file)
        writer.writerow(companies)
        writer.writerow(counts)
        writer.writerow(variances)

if __name__ == "__main__":
    scrape = Scrape()
    scrape.driverSetup()
    scrape.navigateSEC()
    scrape.addData()
    scrape.addCovidCounts()
    scrape.writeFailsToCSV()

    writeToCSV()
