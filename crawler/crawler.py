import os
import images
import links
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
import urllib.robotparser
from urllib.parse import urlparse

#url1 = "http://www.upravneenote.gov.si"
url1 = "http://www.mizs.gov.si"
links.get_links(url1)
images.get_images(url1)