from xml.dom.minidom import Element
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from selenium.webdriver.common.action_chains import ActionChains
import time

strng = ['AMERICAN BIO MEDICA CORP (ABMC)', 'APPLIED DNA SCIENCES INC (APDN, APPDW)']

for string in strng:
    print(string)
    tick = string[string.find("(")+1:string.find(")")]
    tick = tick[tick.find(" ")+1:len(tick)]
    print(tick)