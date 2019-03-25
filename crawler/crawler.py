import links
import database
from page import Page
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import datetime
import time
import urllib.robotparser
import robotexclusionrulesparser
import psycopg2

# Robots parser
robots = robotexclusionrulesparser.RobotExclusionRulesParser()


def get_sitemap(robots_content):
    sitemap_content = ""
    robots.parse(robots_content)
    sitemaps = robots.sitemaps
    for sitemap in sitemaps:
        try:
            sitemap_content += requests.get(sitemap, timeout=10).text
        except requests.exceptions.Timeout as e:
            print(e)
    if sitemap_content == "":
        sitemap_content = None
    return sitemap_content

def get_10mb(url):
    r = requests.get(url, stream=True, timeout=10)
    data = None
    size = 0
    max_size = 10000000
    for chunk in r.iter_content(1024):
        size += len(chunk)
        if data is None:
            data = chunk
        else:
            data += chunk
        if size > max_size:
            return data

def crawl_webpage(page, thread_name, start):
    conn = psycopg2.connect("host='localhost' dbname='postgres' user='postgres' password='test'")
    #print(thread_name+" has started")
    #print(page)
    try:
        # 1. Check domain robots and sitemap
        if page.robots_content is None:
            # TIMEOUT 10s.
            try:
                page.robots_content = requests.get("http://" + page.domain + "/robots.txt", timeout=10).text #Tukj predpostavlam da te avtomatsko na https da če ni http
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                database.update_page(conn, "TIMEOUT", None, None, None, page.url)
                end = time.time()
                #print(end - start)
                return


            page.sitemap_content = get_sitemap(page.robots_content)
            #writing sitemap, robots and domain to site
            database.write_site_to_database(conn, page.robots_content,page.sitemap_content,page.domain)

        if page.robots_content is None:
            time.sleep(4)
        else:
            parser = urllib.robotparser.RobotFileParser(url="http://" + page.domain + "/robots.txt", )
            parser.read()
            delay = parser.crawl_delay("*")
            time.sleep(delay)

        # 2. Read page, write html, status code and accessed time
        try:
            response = requests.head("http://" + page.url, allow_redirects=True, timeout=10)# timeout=self.pageOpenTimeout, headers=customHeaders)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            database.update_page(conn, "TIMEOUT", None, None, None, page.url)
            end = time.time()
            #print(end - start)
            return
        page.http_status_code = response.status_code
        page.accessed_time = datetime.datetime.now()
        page.content_type = response.headers['content-type']

        # HTML
        if "text/html" in page.content_type:
            page.page_type_code = "HTML"
            # Selenium driver
            options = Options()
            options.add_argument("--headless")
            driver = webdriver.Chrome('./chromedriver.exe', options=options)
            driver.get("http://" + page.url)
            page.html_content = driver.page_source
            # Da dobiš robots iz strani, na katero si se rederictu
            page.redirected_to = driver.current_url
            # 3. Get links, write new pages & sites.
            database.write_url_to_database(conn, links.get_links(page, driver), page.page_id)
            try:
                database.write_image_to_database(conn, page.url, driver)
            except Exception as e:
                print(e)
            #update page
            database.update_page(conn, page.page_type_code, page.html_content, page.http_status_code, page.accessed_time, page.url)
            driver.close()

        # OTHER CONTENT TYPE
        else:
            page.page_type_code = "BINARY"
            page.html_content = None
            # PDF
            if "application/pdf" in page.content_type:
                page.binary_data = get_10mb("http://" + page.url)
                page.data_type = "PDF"
            # DOC
            elif "application/msword" in page.content_type:
                page.binary_data = get_10mb("http://" + page.url)
                page.data_type = "DOC"
            # DOCX
            elif "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in page.content_type:
                page.binary_data = get_10mb("http://" + page.url)
                page.data_type = "DOCX"
            # PPT
            elif "application/vnd.ms-powerpoint" in page.content_type:
                page.binary_data = get_10mb("http://" + page.url)
                page.data_type = "PPT"
            # PPTX
            elif "application/vnd.openxmlformats-officedocument.presentationml.presentation":
                page.binary_data = get_10mb("http://" + page.url)
                page.data_type = "PPTX"

            database.write_page_data(conn, page.page_id, page.data_type, page.binary_data)
            database.update_page(conn, page.page_type_code, page.html_content, page.http_status_code, page.accessed_time, page.url)
        end = time.time()
        #print(end - start)
        #print(thread_name + " has finished")
        conn.close()
    except Exception as e:
        database.update_page(conn, "TIMEOUT", None, None, None, page.url)
        end = time.time()
        print(page)
        print(e)
        #print(end - start)
        conn.close()
        return


