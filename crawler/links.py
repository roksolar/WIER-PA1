import re
import urllib.robotparser
import urlcanon
from urllib.parse import urlparse, urljoin, urlsplit
import requests
import regex as regex
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urldefrag


def get_links(page, driver):
    #url1 = "http://localhost:8080/"
    #url1 = "http://www.e-prostor.gov.si"
    #url1 = "http://www.mizs.gov.si/"
    #url1 = "https://ucilnica.fri.uni-lj.si"
    links = []
    # Parsing ROBOTS.TXT
    url1 = page.redirected_to
    robots_url = urlparse(url1).scheme + "://" + urlparse(url1).netloc + "/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    #rrate = rp.request_rate("*")

    # http://fortheloveofseo.com/blog/seo-basics/tutorial-robots-txt-your-guide-for-the-search-engines/
    # Request-rate = Koliko strani na koliko sekund lahko obiščeš
    #if rrate is not None:
    #    print(str(rrate.requests) + " request per " + str(rrate.seconds) + " seconds")
    #cdelay = rp.crawl_delay("*")
    # Crawl-delay = Koliko časa moraš počakat med requesti
    #if cdelay is not None:
    #    print("Crawl delay: " + str(cdelay))

    #Sitemap
    links = parse_links(parse_sitemap(page.sitemap_content), links, rp)

    # Linki v js (gumbi) s Selenium
    js_code = driver.find_elements_by_xpath("//button[@onclick]")
    for code in js_code:
        match1 = regex.findall(r'location\.href\s*=\s*\"([^"]+)\"', code.get_attribute("onclick"))
        match2 = regex.findall(r'document\.location\s*=\s*\"([^"]+)\"', code.get_attribute("onclick"))
        links = parse_links(match1 + match2, links, rp)

    # Linki v js (koda) s Selenium
    js_code = driver.find_elements_by_xpath("//script")
    for code in js_code:
        match1 = regex.findall(r'location\.href\s*=\s*\"([^"]+)\"', code.get_attribute("innerText"))
        match2 = regex.findall(r'document\.location\s*=\s*\"([^"]+)\"', code.get_attribute("innerText"))
        links = parse_links(match1 + match2, links, rp)

    # a...href linki s Selenium
    elems = driver.find_elements_by_xpath("//a[@href]")
    urls = []
    for elem in elems:
        urls.append(elem.get_attribute("href"))
    links = parse_links(urls, links, rp)

    driver.close()
    #print(len(links))
    # Beautiful soup pridobivanje linkov. Ne doda predpone relativnim linkom
    # soup = BeautifulSoup(driver.page_source, 'html.parser')
    # for link in soup.findAll('a'):
    #             tet_2 = link.get('href')
    #             print(tet_2)
    return links

def parse_links(potential_links, links, robots):
    for potential_link in potential_links:
        #avascript:void(0); pa to.
        if "javascript:" in potential_link.lower():
           continue

        #Odstrani #...
        link = urldefrag(potential_link)[0]

        #ta še porte odstrani
        parsed_url = urlcanon.parse_url(link)
        urlcanon.whatwg(parsed_url)
        parsed_url = str(parsed_url)

        # Base URL
        baseURL = str(urlparse(parsed_url).netloc)
        # Add www. to base URL
        if baseURL.startswith("www."):
            baseURL = baseURL[4:]

        # Remove trailing slash. To ne vem če je prov
        if parsed_url.endswith('/'):
            parsed_url = parsed_url[:-1]
        # Remove /index.html
        if parsed_url.endswith('/index.html'):
            parsed_url = parsed_url[:-11]
        # Remove /index.php
        if parsed_url.endswith('/index.php'):
            parsed_url = parsed_url[:-10]
        # Remove http://
        if parsed_url.startswith('http://'):
            parsed_url = parsed_url[7:]
        # Remove https://
        if parsed_url.startswith('https://'):
            parsed_url = parsed_url[8:]
        if parsed_url.startswith('www.'):
            parsed_url = parsed_url[4:]
        #print("navaden       " + potential_link)
        #print("canon         " + parsed_url)

        #print("baseURL       " + baseURL)
        #print("\n")

        if ".gov.si" in baseURL and robots.can_fetch("*", parsed_url) and parsed_url not in links:
            links.append((parsed_url,baseURL))
    return links

def parse_sitemap(sitemap_content):
    links = []
    if sitemap_content is not None:
        #Get links from sitemap XML
        urls = BeautifulSoup(sitemap_content, 'html.parser').find_all("url")
        for url in urls:
            links.append(url.find("loc").text)
    return links

