import requests
import datetime
import imghdr

def get_images(driver):
    images = driver.find_elements_by_tag_name("img")
    data_all = []
    filename = ""
    data = ""
    content_type = ""
    accessed_time = ""

    for image in images:

        filename = (image.get_attribute('src'))
        if image.get_attribute('src') is not None:

            if(image.get_attribute('src').startswith( 'data')):
                #data = (image.get_attribute('src').split(",")[1])
                #print(image.get_attribute('src').split(",")[1])
                print(imghdr.what("a", data))
                content_type = ("ERROR")
            else:

                data = requests.get(image.get_attribute('src')).content
                content_type = imghdr.what("a",data)

            accessed_time = (datetime.datetime.now())
            data_all.append([filename, content_type, data, accessed_time])

    return data_all