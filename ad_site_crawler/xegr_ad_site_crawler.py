import urllib.request, urllib.error, urllib.parse
from typing import List, Dict
import re
import logging
from unidecode import unidecode

from .abstract_ad_site_crawler import AbstractAdSiteCrawler

logger = logging.getLogger('XeGrAdSiteCrawler')

class XeGrAdSiteCrawler(AbstractAdSiteCrawler):
    def __init__(self, stop_words: List, url_search_params: Dict):
        self.stop_words = stop_words
        self.url_search_params = url_search_params
        super().__init__()

    def find_emails(self, data):
        # Filtering Url links
        pattern = re.compile('[\w\-][\w\-\.]+@[\w\-][\w\-\.]+(?:com|gr)', re.MULTILINE)
        captured = pattern.findall(data)
        return captured

    def get_ads_list(self, html_dumps):
        # Collecting Emails
        email_dict = dict()
        for link, data in html_dumps:
            emails_set = set(self.find_emails(data))
            if bool(emails_set):
                email = emails_set.pop()
                if email in email_dict.values():
                    email = "Exists"
            else:
                email = "No_Email"
            email_dict[link] = email
        return email_dict

    # Function For Extracting Html Link
    def link(self, html_data):
        # Filtering Url links
        logger.debug("[*] Extracting Html Links ...")

        pattern = re.compile(r'(<a class=\"highlight\".*?>)')
        a_tag_captured = pattern.findall(html_data)
        for i in a_tag_captured:
            href_raw = i[str(i).find('href'):]
            href = href_raw[:href_raw.find(' ')]
            yield href[6:-1]
        return

    # Function For Downloading Html
    def retrieve_html(self, url):
        try:
            logger.debug("[*] Downloading Html Codes ... ")
            header = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0 Iceweasel/31.8.0'}
            req = urllib.request.Request(url, headers=header)
            page = urllib.request.urlopen(req).read()
        except Exception as e:
            logger.error(e)
            page = 'None'
        if type(page) is not str:
            page = page.decode('utf-8')
        return page

    def crawl(self, ads_checked):
        params = urllib.parse.urlencode(self.url_search_params)
        page_link = "http://www.xe.gr/search?%s" % params
        html_dumps = list()
        for sub_url in self.link(self.retrieve_html(page_link)):
            sub_url = "http://www.xe.gr" + sub_url
            if sub_url not in ads_checked:
                html = self.retrieve_html(sub_url)

                if any(unidecode(word).lower() in unidecode(html) for word in self.stop_words):
                    continue
                html_dumps.append((sub_url, html))

        return html_dumps