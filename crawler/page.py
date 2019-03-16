class Page:
    content_type = None
    binary_data = None
    def __init__(self, page_id, site_id, page_type_code, url, html_content, http_status_code, accessed_time, domain, robots_content, sitemap_content):
        self.page_id = page_id
        self.site_id = site_id
        self.page_type_code = page_type_code
        self.url = url
        self.html_content = html_content
        self.http_status_code = http_status_code
        self.accessed_time = accessed_time
        self.domain = domain
        self.robots_content = robots_content
        self.sitemap_content = sitemap_content

    def __str__(self):
        return self.url