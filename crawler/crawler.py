import os
import images
import links
import database
from page import Page
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import datetime
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

page = Page(*(database.getN_frontiers(1)[0]))

# 1. Check domain robots and sitemap
if page.robots_content is None:
    page.robots_content = requests.get("http://" + page.domain + "/robots.txt").text #Tukj predpostavlam da te avtomatsko na https da če ni http
    page.sitemap_content = get_sitemap(page.robots_content)
    #writing sitemap, robots and domain to site
    database.write_site_to_database(page.robots_content,page.sitemap_content,page.domain)

# 2. Read page, write html, status code and accessed time
response = requests.head("http://" + page.url)# timeout=self.pageOpenTimeout, headers=customHeaders)
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

    # 3. Get links, write new pages & sites.
    database.write_url_to_database(links.get_links(page, driver))

    #update page
    database.update_page("HTML", page.html_content, page.http_status_code, page.accessed_time,page.url)

# OTHER CONTENT TYPE
else:
    page.page_type_code = "BINARY"
    page.html_content = None
    # TODO: samo pdf, doc, docx, ppt in pptx. kaj z ostalimi?
    page.binary_data = requests.get("http://" + page.url).content #Ne vem če je to to kar je treba shrant

#url1 = "http://www.mizs.gov.si/"
#links = links.get_links(url1)
#database.write_url_to_database(links)

#from frontier... from current link get images
#database.write_image_to_database(url1)

#images.get_images(url1)
