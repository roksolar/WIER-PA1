import os
import images
import links
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
import urllib.robotparser
from urllib.parse import urlparse
import datetime

def get_images(driver):
    images = driver.find_elements_by_tag_name("img")
    filename = []
    content_type = []
    data = []
    accessed_time =[]

    for image in images:
        filename.append(image.get_attribute('src'))
        data.append(requests.get(image.get_attribute('src')).content)
        accessed_time.append(datetime.datetime.now())
        content_type.append(image.get_attribute('src').split(".")[-1])
        
    return [filename, content_type, data, accessed_time]
