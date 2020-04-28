import urllib.request, urllib.error, urllib.parse
from typing import List, Dict, Tuple
import re
import logging
from unidecode import unidecode

from .abstract_ad_site_crawler import AbstractAdSiteCrawler

logger = logging.getLogger('XeGrAdSiteCrawler')


class XeGrAdSiteCrawler(AbstractAdSiteCrawler):
    __slots__ = ('_stop_words')

    _stop_words: List
    _ad_site_url: str = "http://www.xe.gr"

    def __init__(self, stop_words: List):
        """
        Tha basic constructor. Creates a new instance of AdSiteCrawler using the specified credentials

        :param stop_words:
        """

        self._stop_words = stop_words
        super().__init__()

    def get_new_ads(self, url_search_params: Dict, ads_checked: List) -> Dict:
        """
        Retrieves each sub-link's html, searches and yields an email for each of them.

        :param url_search_params:
        :param ads_checked:
        """

        encoded_search_params = urllib.parse.urlencode(url_search_params)
        search_page_url = "{ad_site_url}/search?{encoded_search_params}".format(ad_site_url=self._ad_site_url,
                                                                                encoded_search_params=encoded_search_params)

        search_page_html = self._retrieve_html_from_url(search_page_url)
        # Search for links in the main page's html, retrieve their html and look for emails inside them
        for ad_link in self._find_links_in_html(search_page_html):
            full_sub_link = self._ad_site_url + ad_link
            if full_sub_link in ads_checked:
                continue
            ad_page_html = self._retrieve_html_from_url(full_sub_link)
            if any(unidecode(word).lower() in unidecode(ad_page_html) for word in self._stop_words):
                continue
            # Add the link inside the check list in order to avoid duplicate ads
            ads_checked.append(full_sub_link)
            emails_in_ad_page = self._find_emails_in_html(html=ad_page_html)
            if len(emails_in_ad_page) == 0:
                yield full_sub_link, None
            else:
                yield full_sub_link, emails_in_ad_page[0]

    @staticmethod
    def _retrieve_html_from_url(url: str) -> str:
        """
        Retrieves full html from the specified url.

        :params url:
        """

        try:
            logger.debug("Retrieving html from url: %s .." % url)
            header = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0 Iceweasel/31.8.0'}
            req = urllib.request.Request(url, headers=header)
            html = urllib.request.urlopen(req).read()
        except Exception as e:
            logger.error(e)
            html = 'None'
        if type(html) is not str:
            html = html.decode('utf-8')
        return html

    @staticmethod
    def _find_links_in_html(html_data: str) -> str:
        """
        Searches for sub-link patterns in html and yields each link.

        :param html_data:
        """

        logger.debug("Searching for sub-links in html..")

        pattern = re.compile(r'(<a class=\"highlight\".*?>)')
        a_tag_captured = pattern.findall(html_data)
        for i in a_tag_captured:
            href_raw = i[str(i).find('href'):]
            href = href_raw[:href_raw.find(' ')]
            yield href[6:-1]

    @staticmethod
    def _find_emails_in_html(html: str) -> List:
        """
        Searches for email patterns in html and returns list of emails.

        :param html:
        """

        logger.debug("Searching for emails in html..")

        pattern = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+(?:com|gr)', re.MULTILINE)
        emails = pattern.findall(html)
        return emails
