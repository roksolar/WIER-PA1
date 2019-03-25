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
import psycopg2

#url1 = "http://www.upravneenote.gov.si"

max_workers = 5
# Get link from frontier
connStart = psycopg2.connect("host='localhost' dbname='postgres' user='postgres' password='test'")
frontier = database.getN_frontiers(connStart, 5)
# Timer
start = time.time()

while frontier != -1:
    i = 0
    for ele in frontier:
        if i>=5:
            break
        page = Page(*ele)
        w = threading.Thread(name='worker', target=crawler.crawl_webpage, args=(page, "Thread"+str(i), start,))
        w.start()
        i = i + 1
    w.join()
    frontier = database.getN_frontiers(connStart, 16)
    end = time.time()
    #print("Thread loop finished: "+str(end-start))

connStart.close()
                