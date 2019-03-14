import psycopg2
import images

def write_url_to_database(links):
    #connect to database
    conn = psycopg2.connect("host='localhost' dbname='postgres' user='postgres' password='test'")
    cur = conn.cursor()
    for link in links:
        #checking for unique url is done with unique url key
        try:
            sql = "INSERT INTO crawldb.page(url) VALUES(%s)"
            cur.execute(sql, (link,))
        except:
            print("Something is wrong with database or url is in database")
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



