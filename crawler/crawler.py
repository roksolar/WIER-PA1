import os
import images
import links
import database
from page import Page
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
import urllib.robotparser
from urllib.parse import urlparse

#url1 = "http://www.upravneenote.gov.si"

#chech first page in crawldb.page which is FRONTIER


page = Page(*(database.getN_frontiers(1)[0]))
# 1. Check domain robots and sitemap
# 2. Read page, write html, status code and accessed time
# 3. Get links, write new pages & sites.

#url1 = "http://www.mizs.gov.si/"
#links = links.get_links(url1)
#database.write_url_to_database(links)

#from frontier... from current link get images
#database.write_image_to_database(url1)

#images.get_images(url1)
