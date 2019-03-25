import urlcanon
from urllib.parse import urlparse
import regex as regex
import selenium
from bs4 import BeautifulSoup
from urllib.parse import urldefrag
import robotexclusionrulesparser

robots = robotexclusionrulesparser.RobotExclusionRulesParser()

def get_links(page, driver):
    #url1 = "http://localhost:8080/"
    #url1 = "http://www.e-prostor.gov.si"
    #url1 = "http://www.mizs.gov.si/"
    #url1 = "https://ucilnica.fri.uni-lj.si"
    links = []
    # Parsing ROBOTS.TXT
    if page.robots_content is not None:
        robots.parse(page.robots_content)

    #Sitemap
    links = parse_links(parse_sitemap(page.sitemap_content), links, robots)

    # Linki v js (gumbi) s Selenium
    js_code = driver.find_elements_by_xpath("//button[@onclick]")
    for code in js_code:
        match1 = regex.findall(r'location\.href\s*=\s*\"([^"]+)\"', code.get_attribute("onclick"))
        match2 = regex.findall(r'document\.location\s*=\s*\"([^"]+)\"', code.get_attribute("onclick"))
        links = parse_links(match1 + match2, links, robots)

    # Linki v js (koda) s Selenium
    js_code = driver.find_elements_by_xpath("//script")
    for code in js_code:
        match1 = regex.findall(r'location\.href\s*=\s*\"([^"]+)\"', code.get_attribute("innerText"))
        match2 = regex.findall(r'document\.location\s*=\s*\"([^"]+)\"', code.get_attribute("innerText"))
        links = parse_links(match1 + match2, links, robots)

    # a...href linki s Selenium
    elems = driver.find_elements_by_xpath("//a[@href]")
    urls = []
    for elem in elems:
        staleElement = True
        retries = 0
        while staleElement:
            retries+=1
            if retries > 100:
                break
            try:
                urls.append(elem.get_attribute("href"))
                staleElement = False

            except selenium.common.exceptions.StaleElementReferenceException as e:
                staleElement = True



    links = parse_links(urls, links, robots)

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
        # Remove www. to base URL
        #if baseURL.startswith("www."):
        #    baseURL = baseURL[4:]

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
        #if parsed_url.startswith('www.'):
        #    parsed_url = parsed_url[4:]
        #print("navaden       " + potential_link)
        #print("canon         " + parsed_url)

        #print("baseURL       " + baseURL)
        #print("\n")

        if ".gov.si" in baseURL and robots.is_allowed("*", parsed_url) and parsed_url not in links:
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


'''options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome('./chromedriver.exe', options=options)
driver.get("http://www.e-prostor.gov.si")
get_links(None, driver)'''