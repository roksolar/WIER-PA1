import datetime
import crawler


def get_images(driver):
    images = driver.find_elements_by_tag_name("img")
    data_all = []
    filename = ""
    data = ""
    content_type = ""
    accessed_time = ""

    for image in images:

        filename = (image.get_attribute('src'))
        print(filename)
        if filename is not None:
            if filename[:4] == "data":
                continue
            data = crawler.get_10mb(filename)
            content_type = filename.split(".")[-1]
            if len(content_type) > 4:
                content_type = "UNKNOWN"
            accessed_time = (datetime.datetime.now())
            data_all.append([filename, content_type, data, accessed_time])

    return data_all
