import os
import images
import links
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
import urllib.robotparser
from urllib.parse import urlparse

def get_images(url1):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome('./chromedriver.exe', options=options)
    driver.get(url1)

    images = driver.find_elements_by_tag_name("img")
    a = []
    for image in images:
        print(image.get_attribute('src'))
        a.append(image.get_attribute('src'))

    driver.close()

    return a
