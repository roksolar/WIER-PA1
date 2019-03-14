import os
import images
import links
import database

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
import urllib.robotparser
from urllib.parse import urlparse

#url1 = "http://www.upravneenote.gov.si"
url1 = "http://www.mizs.gov.si/"
links = links.get_links(url1)
database.write_url_to_database(links)

#from frontier... from current link get images
database.write_image_to_database(url1)

#images.get_images(url1)