import psycopg2
import images
import hashlib
from sys import getsizeof

hash_set = set()

def get_hash_to_set(conn):
    a = get_hash(conn)
    for element in a:
        hash_set.add(element[0])

def write_url_to_database(conn, links, page_index):
    cur = conn.cursor()
    for link in links:
        #print(link)
        #checking for unique url is done with unique url key
        index = -1
        try:
            sql = "SELECT id FROM crawldb.site WHERE domain = %s"
            cur.execute(sql, (link[1],))
            index = cur.fetchone()[0]
            conn.commit()
        except Exception as e:
            conn.rollback()
            conn.commit()
            #print(e)
        #print(index)
        if index == -1:
            #should add new site
            try:
                sql = 'INSERT INTO crawldb.site(domain) VALUES (%s)'
                cur.execute(sql, (link[1], ))
                conn.commit()
                sql = "SELECT id FROM crawldb.site WHERE domain = %s"
                cur.execute(sql, (link[1],))
                index = cur.fetchone()[0]
                conn.commit()

            except Exception as e:
                conn.rollback()
                #print(e)
                conn.commit()
                cur.close()

        #INSERT NEW PAGE WITH SITE_ID = INDEX
        try:
            #print(index)
            sql = 'INSERT INTO crawldb.page(site_id, page_type_code, url) ' \
                  'VALUES(%s, %s, %s)'
            cur.execute(sql, (index, 'FRONTIER', link[0],))

            sql = "SELECT id FROM crawldb.page WHERE url = %s"
            cur.execute(sql, (link[0],))
            index = cur.fetchone()[0]

            sql = 'INSERT INTO crawldb.link(from_page,to_page) VALUES (%s,%s)'
            cur.execute(sql, (page_index, index,))
            conn.commit()
            cur.close()
            #print(index)
        except Exception as e:
            conn.rollback()
            conn.commit()
            cur.close()
            #print(e)
            #print("testasdas")

def update_page(conn,page_type,html,http_status,accessed,url, hash):
    #TODO: WHERE PAGE ID = ID
    cur = conn.cursor()
    try:
        sql = "UPDATE crawldb.page SET page_type_code = %s,html_content=%s,http_status_code = %s,accessed_time = %s,html_content_hash = %s WHERE url=%s"
        cur.execute(sql, (page_type, html, http_status, accessed, hash, url,))
        conn.commit()
        cur.close()
    except Exception as e:
        conn.rollback()
        print(e)
        conn.commit()
        cur.close()



def write_site_to_database(conn,robots,sitemap,domain):
    cur = conn.cursor()
    try:
        sql = "UPDATE crawldb.site SET robots_content = %s,sitemap_content=%s WHERE domain=%s"
        #print(sql)
        cur.execute(sql, (robots, sitemap, domain, ))
        conn.commit()
        cur.close()
    except Exception as e:
        conn.rollback()
        conn.commit()
        cur.close()
        #print(e)
        #print("Something is wrongt!")


def write_page_data(conn,page_id,data_type_code,data):
    cur = conn.cursor()

    sql = 'INSERT INTO crawldb.page_data (page_id, data_type_code,data) ' \
          'VALUES (%s,%s,%s)'
    try:
        cur.execute(sql, (page_id, data_type_code,data,))
        conn.commit()
        cur.close()
    except Exception as e:
        conn.rollback()
        conn.commit()
        cur.close()
        #print(e)
        #print("Error while writing image to database")



def write_image_to_database(conn,url, driver):


    #get all images from url
    image_data = images.get_images(driver)
    #insert all images to database
    for image in image_data:
        cur = conn.cursor()
        sql = 'INSERT INTO crawldb.image (page_id, filename,content_type,data,accessed_time) ' \
              'VALUES ((SELECT id from crawldb.page WHERE url=%s), %s, %s, %s , %s )'
        try:
            #print(sql, (image,url,))
            cur.execute(sql, (url, image[0], image[1], image[2], image[3], ))
            conn.commit()
            cur.close()
        except Exception as e:
            conn.rollback()
            print(e)
            conn.commit()
            cur.close()

def getN_frontiers(conn, n):
    cur = conn.cursor()
    sql = '''SELECT t.id, t.site_id, t.page_type_code, t.url, t.html_content, t.http_status_code
                    ,t.accessed_time,site.domain, site.robots_content, site.sitemap_content 
                    FROM (
                        SELECT DISTINCT ON (page.site_id) *
                        FROM crawldb.page 
                        where page.page_type_code='FRONTIER'
                        ORDER BY page.site_id, page.id ASC
                    ) t
            JOIN crawldb.site site ON (t.site_id = site.id)
            ORDER BY t.id ASC
            limit %s'''

    '''sql = SELECT page.id, page.site_id, page.page_type_code, page.url, page.html_content, page.http_status_code
, page.accessed_time, site.domain, site.robots_content, site.sitemap_content FROM crawldb.page page
    JOIN crawldb.site site ON (page.site_id = site.id)
    WHERE page_type_code = 'FRONTIER'
    ORDER BY page.id asc
    LIMIT %s'''
    try:
        cur.execute(sql, (n,))
        conn.commit()
        a = cur.fetchall()
        cur.close()
        return a
    except Exception as e:
        #print(e)
        #print("Error while writing image to database")
        conn.commit()
        cur.close()
        return -1

def get_hash(conn):
    cur = conn.cursor()
    sql = "SELECT html_content_hash FROM crawldb.page WHERE html_content_hash is not null"
    try:
        cur.execute(sql)
        conn.commit()
        a = cur.fetchall()
        cur.close()
        return a

    except Exception as e:
        conn.commit()
        cur.close()
        return -1

def set_html_content_to_html_content_hash(conn):
    cur = conn.cursor()
    sql = "SELECT id,html_content FROM crawldb.page WHERE http_status_code = '200' and page_type_code = 'HTML' and html_content_hash is null LIMIT 1000"
    try:
        cur.execute(sql)
        conn.commit()
        a = cur.fetchall()
        print("Hashing " + str(len(a)) + " pages!")
        for element in a:
            cur = conn.cursor()
            temp_hash = hashlib.md5((element[1]).encode()).hexdigest()
            try:
                sql = "UPDATE crawldb.page SET html_content_hash = %s WHERE id = %s"
                cur.execute(sql, (temp_hash, element[0], ))
                conn.commit()
                cur.close()
            except Exception as e:
                conn.rollback()
                print(e)
                conn.commit()
                cur.close()
        print("Hashed!")

    except Exception as e:
        conn.commit()
        cur.close()
        return -1
