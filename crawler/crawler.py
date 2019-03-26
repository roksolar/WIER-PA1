import links
import database
from page import Page
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import datetime
import time
import robotexclusionrulesparser
import psycopg2

robots = robotexclusionrulesparser.RobotExclusionRulesParser()


def get_sitemap(robots_content):
    sitemap_content = ""
    robots.parse(robots_content)
    sitemaps = robots.sitemaps
    for sitemap in sitemaps:
        # Če bo timeout na sitemap dovoli nadaljevanje
        try:
            sitemap_content += requests.get(sitemap, timeout=10).text
        except requests.exceptions.Timeout as e:
            print(e)
    if sitemap_content == "":
        sitemap_content = None
    return sitemap_content

def get_10mb(url):
    # Če bo timeout na content bo status Timeout (Exception)
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
            r.close()
            return data
    r.close()
    return data

def crawl_webpage(page, thread_name, start):
    # Robots parser
    conn = psycopg2.connect("host='localhost' dbname='postgres' user='postgres' password='test'")
    try:
        # 1. Check domain robots and sitemap
        if page.robots_content is None:
            # TIMEOUT 10s.
            # Če bo timeout na robots potem je timeout na page. Exception
            r = requests.get("http://" + page.domain + "/robots.txt", timeout=10)
            if r.status_code == 200:
                page.robots_content = r.text
                page.sitemap_content = get_sitemap(page.robots_content)
                #writing sitemap, robots and domain to site
                database.write_site_to_database(conn, page.robots_content,page.sitemap_content,page.domain)

        if page.robots_content is None:
            time.sleep(4)
        else:
            delay = robots.get_crawl_delay("*")
            if delay == None:
                time.sleep(4)
            else:
                time.sleep(delay)

            #print(e)

        # 2. Read page, write html, status code and accessed time
        # Če bo timeout na head bo najbrž tudi na content. Exception
        try:
            # Če ne dovoli head request, poskusi še z get
            response = requests.head("http://" + page.url, allow_redirects=True, timeout=10)
            page.http_status_code = response.status_code
            page.accessed_time = datetime.datetime.now()
            page.content_type = response.headers['content-type']
        except Exception as e:
            print(page)
            print("Head request error. Trying with get...")
            print(e)
            response = requests.get("http://" + page.url, allow_redirects=True, timeout=10)
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
                print(page)
                print("slike")
                print(e)
            #update page
            database.update_page(conn, page.page_type_code, page.html_content, page.http_status_code, page.accessed_time, page.url)
            driver.quit()
            #driver.close()

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
        #print(thread_name + " has finished")
        conn.close()
    except Exception as e:
        # Opaženi: requests.exceptions.ConnectTimeout, requests.exceptions.SSLError, requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError)
        #timeout error na content, ssl error, timeout error na handshake, connection error
        database.update_page(conn, "TIMEOUT", None, None, None, page.url)
        try:
            #driver.close()
            driver.quit()
        except Exception as x:
            pass
        print(page)
        print(e)
        conn.close()
        return

