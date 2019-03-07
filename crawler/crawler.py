import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests

url1 = "http://podatki.gov.si"


response = requests.get(url1)
print('status code:', response.status_code)
print('url:', response.url)
print('content:', response.text)






'''
options = Options()
options.add_argument("--headless")

driver = webdriver.Chrome('./chromedriver.exe', options=options)
driver.get("http://fri.uni-lj.si")

for n in driver.find_elements_by_class_name('news-container-title'):
    if len(n.text) > 0:
        print(n.text)

driver.close()
'''