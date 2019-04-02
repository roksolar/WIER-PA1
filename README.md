# WIER-PA1

Simple web crawler assignment for Web information extraction and retrieval course 
of University of Ljubljana, Faculty of Computer and Information Science. Crawler is crawling
only gov.si sites and stores all images and links which are found in page.


Requiered python libraries:
selenium
requests
datetime
time
robotexclusionrulesparser
hashlib
network
matplotlib.pyplot
psycopg2
scipy
threading
urlcanon
urllib.parse
regex
bs4

How to use it?
-	You should install postgreSQL and import schema for database which is contained 
	in this project. It is required to set username to postgres and password test. This
	can be modified in crawler/threadManager.py, line 13 and line 31.
-	Console : python threadManager.py N
	Parameter N is for choosing number of threads.
