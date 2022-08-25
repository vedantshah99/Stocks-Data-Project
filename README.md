# Stocks-Data-Project
This project was built as a way to aquire data that would help us track the effects of COVID-19 on the performances of companies during its rise. It uses Selenium to automate the process of navigating and going through entries in a website, and copying data into a .csv that can be put into Pandas. 

Uses Selenium to navigate to https://www.sec.gov/edgar/search/#
  - automatically enters any word into the system and looks for published 10Q forms
  - goes through every company's 10Q form and saves the number of times the entered word was used in each document
Makes a list of every company's stock ticker
  - enters the each company's stock ticker into Yahoo Finance
  - goes to historical data and changes the start and end dates
  - collects the the closing prices of every week during the time interval and calculates the variances of the data
  - saves the variances into a list
Inputs the companies, word counts, and variances into a csv file
  - also makes a csv file that consists of all the failed data points
