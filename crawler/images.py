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
    data_all = []
    filename = ""
    data = ""
    content_type = ""
    accessed_time = ""

    for image in images:

        filename = (image.get_attribute('src'))
        if(image.get_attribute('src').startswith( 'data')):
            data = (image.get_attribute('src').split(",")[1])
            content_type = ("ERROR");
        else:
            data = requests.get(image.get_attribute('src')).content
            content_type = (image.get_attribute('src').split(".")[-1])

        accessed_time = (datetime.datetime.now())
        data_all.append([filename, content_type, data, accessed_time])

    return data_all