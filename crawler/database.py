import psycopg2
import images

def write_url_to_database(links,page_index):
    #connect to database
    conn = psycopg2.connect("host='localhost' dbname='postgres' user='postgres' password='test'")
    cur = conn.cursor()
    for link in links:
        print(link)
        #checking for unique url is done with unique url key
        index = -1
        try:
            sql = "SELECT id FROM crawldb.site WHERE domain = %s"
            cur.execute(sql, (link[1],))
            index = cur.fetchone()[0]
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(e)
        print(index)
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
                print(e)

        #INSERT NEW PAGE WITH SITE_ID = INDEX
        try:
            print(index)
            sql = 'INSERT INTO crawldb.page(site_id, page_type_code, url) ' \
                  'VALUES(%s, %s, %s)'
            cur.execute(sql, (index, 'FRONTIER', link[0],))

            sql = "SELECT id FROM crawldb.page WHERE url = %s"
            cur.execute(sql, (link[0],))
            index = cur.fetchone()[0]

            sql = 'INSERT INTO crawldb.link(from_page,to_page) VALUES (%s,%s)'
            cur.execute(sql, (page_index, index,))
            print(index)
        except Exception as e:
            conn.rollback()
            print(e)
            print("testasdas")
    conn.commit()
    cur.close()

def update_page(page_type,html,http_status,accessed,url):
    conn = psycopg2.connect("host='localhost' dbname='postgres' user='postgres' password='test'")
    cur = conn.cursor()
    try:
        sql = "UPDATE crawldb.page SET page_type_code = %s,html_content=%s,http_status_code = %s,accessed_time = %s WHERE url=%s"
        cur.execute(sql, (page_type, html, http_status, accessed, url,))
        conn.commit()
    except Exception as e:
        print(e)
    conn.commit()
    cur.close()




def write_site_to_database(robots,sitemap,domain):
    #connect to database
    conn = psycopg2.connect("host='localhost' dbname='postgres' user='postgres' password='test'")
    cur = conn.cursor()
    try:
        sql = "UPDATE crawldb.site SET robots_content = %s,sitemap_content=%s WHERE domain=%s"
        print(sql)
        cur.execute(sql, (robots, sitemap, domain, ))
    except:
        print("Something is wrongt!")
    conn.commit()
    cur.close()

def write_page_data(page_id,data_type_code,data):

    conn = psycopg2.connect("host='localhost' dbname='postgres' user='postgres' password='test'")
    cur = conn.cursor()

    sql = 'INSERT INTO crawldb.page_data (page_id, data_type_code,data) ' \
          'VALUES (%s,%s,%s)'
    try:
        cur.execute(sql, (page_id, data_type_code,data,))
    except:
        print("Error while writing image to database")

    conn.commit()
    cur.close()

def write_image_to_database(url):
    conn = psycopg2.connect("host='localhost' dbname='postgres' user='postgres' password='test'")
    cur = conn.cursor()

    #get all images from url
    image_data = images.get_images(url)

    #insert all images to database
    for image in image_data:
        sql = 'INSERT INTO crawldb.image (page_id, filename) ' \
              'VALUES ((SELECT id from crawldb.page WHERE url=%s), %s)'
        try:
            print(sql, (image,url,))
            cur.execute(sql, (url,image,))
        except:
            print("Error while writing image to database")
    conn.commit()
    cur.close()


def getN_frontiers(n):
    conn = psycopg2.connect("host='localhost' dbname='postgres' user='postgres' password='test'")
    cur = conn.cursor()
    sql = '''SELECT page.id, page.site_id, page.page_type_code, page.url, page.html_content, page.http_status_code
, page.accessed_time, site.domain, site.robots_content, site.sitemap_content FROM crawldb.page page
    JOIN crawldb.site site ON (page.site_id = site.id)
    WHERE page_type_code = 'FRONTIER'
    ORDER BY page.id asc
    LIMIT %s'''
    try:
        cur.execute(sql,(n,))
        return cur.fetchall()
    except :
        print("Error while writing image to database")
        return -1

    conn.commit()
    cur.close()
