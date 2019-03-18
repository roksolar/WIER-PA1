import os
import images
import links
import database
from page import Page
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import datetime
import time
from bs4 import BeautifulSoup
import urllib.robotparser
from urllib.parse import urlparse

#url1 = "http://www.upravneenote.gov.si"



def get_sitemap(robots_content):
    sitemap_url = None
    sitemap = None
    for line in robots_content.split("\n"):
        if line.lower().startswith("sitemap"):
            sitemap_url = line.replace("sitemap:", "").replace("Sitemap:", "")
            break
    if sitemap_url is not None:
        sitemap = requests.get(sitemap_url).text
    return sitemap

#chech first page in crawldb.page which is FRONTIER
file = open("log.txt", "w")
frontier = database.getN_frontiers(1)
start = time.time()
while frontier != -1:
    page = Page(*(frontier[0]))
    file.write(page.url + "\n")
    print(page)
    # 1. Check domain robots and sitemap
    if page.robots_content is None:
        # TIMEOUT 10s. TODO: Max size. Timeout še drugje?
        # DODAN PAGE TYPE CODE "TIMEOUT"
        try:
            page.robots_content = requests.get("http://" + page.domain + "/robots.txt", timeout=10).text #Tukj predpostavlam da te avtomatsko na https da če ni http
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            # Poskusi še z www.url
            #try:
            #    page.robots_content = requests.get("http://www." + page.domain + "/robots.txt", timeout=10).text
            #    page.url = "www."+page.url
            #except:
            database.update_page("TIMEOUT", None, None, None, page.url)
            frontier = database.getN_frontiers(1)
            end = time.time()
            print(end - start)
            continue
        page.sitemap_content = get_sitemap(page.robots_content)
        #writing sitemap, robots and domain to site
        database.write_site_to_database(page.robots_content,page.sitemap_content,page.domain)

    # 2. Read page, write html, status code and accessed time
    # TODO: Kako je z redirecti? A lahko slediš in na koncu zapišeš končen status code, ohranjaš pa originalen link?
    response = requests.head("http://" + page.url, allow_redirects=True)# timeout=self.pageOpenTimeout, headers=customHeaders)
    page.http_status_code = response.status_code
    page.accessed_time = datetime.datetime.now()
    page.content_type = response.headers['content-type']

    # HTML
    if "text/html" in page.content_type:
        page.page_type_code = "HTML"
        # Branje s Selenium
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome('./chromedriver.exe', options=options)
        driver.get("http://" + page.url)
        page.html_content = driver.page_source
        # Da dobiš robots iz strani, na katero si se rederictu
        page.redirected_to = driver.current_url
        # 3. Get links, write new pages & sites.
        database.write_url_to_database(links.get_links(page, driver), page.page_id)

        #update page
        database.update_page(page.page_type_code, page.html_content, page.http_status_code, page.accessed_time, page.url)

    # OTHER CONTENT TYPE
    else:
        page.page_type_code = "BINARY"
        page.html_content = None
        # PDF
        if "application/pdf" in page.content_type:
            page.binary_data = requests.get("http://" + page.url).content #Ne vem če je to to kar je treba shrant
            page.data_type = "PDF"
        # DOC
        elif "application/msword" in page.content_type:
            page.binary_data = requests.get("http://" + page.url).content
            page.data_type = "DOC"
        # DOCX
        elif "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in page.content_type:
            page.binary_data = requests.get("http://" + page.url).content
            page.data_type = "DOCX"
        # PPT
        elif "application/vnd.ms-powerpoint" in page.content_type:
            page.binary_data = requests.get("http://" + page.url).content
            page.data_type = "PPT"
        # PPTX
        elif "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            page.binary_data = requests.get("http://" + page.url).content
            page.data_type = "PPTX"

        database.write_page_data(page.page_id, page.data_type, page.binary_data)
        database.update_page(page.page_type_code, page.html_content, page.http_status_code, page.accessed_time, page.url)
    frontier = database.getN_frontiers(1)
    end = time.time()
    print(end-start)


file.close()
#url1 = "http://www.mizs.gov.si/"
#links = links.get_links(url1)
#database.write_url_to_database(links)

#from frontier... from current link get images
#database.write_image_to_database(url1)

#images.get_images(url1)
