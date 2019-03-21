import os
import images
import links
import threading
import database
import crawler
from page import Page
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import datetime
import time
import robotexclusionrulesparser
import socket
from bs4 import BeautifulSoup
import urllib.robotparser
from urllib.parse import urlparse

#url1 = "http://www.upravneenote.gov.si"

max_workers = 10
# Log file
file = open("log.txt", "w")
# Get link from frontier
frontier = database.getN_frontiers(10)
# Timer
start = time.time()

while frontier != -1:
    i = 0
    for ele in frontier:
        if i>=10:
            break
        page = Page(*ele)
        w = threading.Thread(name='worker', target=crawler.crawl_webpage, args=(page, "Thread"+str(i), file, start,))
        w.start()
        i = i + 1
    w.join()
    frontier = database.getN_frontiers(10)
    end = time.time()
    print("Thread loop finished: "+str(end-start))


file.close()
