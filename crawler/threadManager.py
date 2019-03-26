
import threading
import database
import crawler
from page import Page
import time
import psycopg2

#url1 = "http://www.upravneenote.gov.si"

max_workers = 10
# Get link from frontier
connStart = psycopg2.connect("host='localhost' dbname='postgres' user='postgres' password='test'")
frontier = database.getN_frontiers(connStart, 10)
# Timer
start = time.time()

while frontier != -1:
    i = 0
    for ele in frontier:
        if i>=10:
            break
        page = Page(*ele)
        w = threading.Thread(name='worker', target=crawler.crawl_webpage, args=(page, "Thread"+str(i), start,))
        w.start()
        i = i + 1
    w.join()
    frontier = database.getN_frontiers(connStart, 10)
    end = time.time()
    #print("Thread loop finished: "+str(end-start))

connStart.close()