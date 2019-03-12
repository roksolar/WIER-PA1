import urllib.robotparser
from urllib.parse import urlparse


def get_links(url1):
    # Parsing ROBOTS.TXT
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(url1 + "/robots.txt")
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

    # Preveri ali lahko dostopaš do neke strani
    # print(rp.can_fetch("*", "http://www.musi-cal.com/cgi-bin/search?city=San+Francisco"))

    # Branje s Selenium
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome('./chromedriver.exe', options=options)
    driver.get(url1)

    # Links s Selenium
    elems = driver.find_elements_by_xpath("//a[@href]")
    counter = 0
    for elem in elems:
        link = elem.get_attribute("href")
        # Pridobi domeno in dovoli, če vsebuje .gov.si in če robots dovoljuje
        baseURL = urlparse(link).netloc
        if ".gov.si" in baseURL and rp.can_fetch("*", link):
            print(link)
            counter += 1
        # if not gov.si then no frontjer for you
        # print(elem.get_attribute("href"))
    print(counter)
    driver.close()

    # Beautiful soup pridobivanje linkov. Ne doda predpone relativnim linkom
    # soup = BeautifulSoup(driver.page_source, 'html.parser')
    # for link in soup.findAll('a'):
    #             tet_2 = link.get('href')
    #             print(tet_2)

