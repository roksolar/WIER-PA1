import threading
import database
import crawler
from page import Page
import time
import psycopg2
import hashlib
import sys

#url1 = "http://www.upravneenote.gov.si"

max_workers = int(sys.argv[1])
# Get link from frontier
connStart = psycopg2.connect("host='localhost' dbname='postgres' user='postgres' password='test'")
frontier = database.getN_frontiers(connStart, max_workers)
#for ele in frontier:
#    print(ele[3])
#print("-----------------")
#for i in range(30):
#    database.set_html_content_to_html_content_hash(connStart)

#get start hash
start = time.time()
database.get_hash_to_set(connStart)
end = time.time()
print("Hashing finished: "+str(end-start) + " there are "+str(len(database.hash_set)) + " different html pages in database")


#make connections
connections = []
for i in range(max_workers):
    connections.append(psycopg2.connect("host='localhost' dbname='postgres' user='postgres' password='test'"))

# Timer
start = time.time()


while frontier != -1 and len(frontier) != 0:
    i = 0
    threads = []
    for ele in frontier:
        if i>=max_workers:
            break
        page = Page(*ele)
        w = threading.Thread(name='worker', target=crawler.crawl_webpage, args=(page, "Thread"+str(i), start, connections[i],))
        w.start()
        threads.append(w)
        i = i + 1
    for e in threads:
        e.join()
    frontier = database.getN_frontiers(connStart, max_workers)
    #for ele in frontier:
    #    print(ele[3])
    #print("-----------------")
    end = time.time()
    #print("Thread loop finished: "+str(end-start))

connStart.close()
for i in range(max_workers):
    connections[i].close()
