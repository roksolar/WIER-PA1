import re
import urllib.robotparser
from urllib.parse import urlparse, urljoin, urlsplit
import requests
import regex as regex
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from url_normalize import url_normalize
from urllib.parse import urldefrag
def get_links(url1):
    #url1 = "http://localhost:8080/"
    url1 = "http://www.e-prostor.gov.si"
    # Parsing ROBOTS.TXT
    robots_url = urlparse(url1).scheme + "://" + urlparse(url1).netloc + "/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    rrate = rp.request_rate("*")

    # http://fortheloveofseo.com/blog/seo-basics/tutorial-robots-txt-your-guide-for-the-search-engines/
    # Request-rate = Koliko strani na koliko sekund lahko obiščeš
    if rrate is not None:
        print(str(rrate.requests) + " request per " + str(rrate.seconds) + " seconds")
    cdelay = rp.crawl_delay("*")
    # Crawl-delay = Koliko časa moraš počakat med requesti
    if cdelay is not None:
        print("Crawl delay: " + str(cdelay))

    #Sitemap
    parse_sitemap(robots_url)

    # Branje s Selenium
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome('./chromedriver.exe', options=options)
    driver.get(url1)

    links = []

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
    for elem in elems:
        link = elem.get_attribute("href")
        # Pridobi domeno in dovoli, če vsebuje .gov.si in če robots dovoljuje

        links = parse_links([link], links, rp)

    driver.close()
    print(links)
    # Beautiful soup pridobivanje linkov. Ne doda predpone relativnim linkom
    # soup = BeautifulSoup(driver.page_source, 'html.parser')
    # for link in soup.findAll('a'):
    #             tet_2 = link.get('href')
    #             print(tet_2)

def parse_links(potential_links, links, robots):
    for potential_link in potential_links:
        #print("navaden     " + potential_link)
        #print(urlparse(potential_link))
        #a = urlparse(potential_link)
        #r1 = urlsplit(potential_link)
        #r2 = urlsplit(r1.geturl())
        #print("kanoniziran " + urldefrag(a.hostname + )[0])
        #print("\n")
        # TODO: REMOVE PORT NUMBBER.
        # TODO: HTTPS/HTTP??
        link = urldefrag(potential_link)[0]
        baseURL = urlparse(link).netloc
        if ".gov.si" in baseURL and robots.can_fetch("*", link) and link not in links:
            links.append(link)
    return links

def parse_sitemap(robots_url):
    line = None
    response = requests.get(robots_url)
    for line in response.text.split("\n"):
        if line.lower().startswith("sitemap"):
            line = line.replace("sitemap:", "").replace("Sitemap:", "")
            print(line)
            break
    #TODO: GE LINKS FROM XML
    response = requests.get(line)
    print(response.text)
    return line
