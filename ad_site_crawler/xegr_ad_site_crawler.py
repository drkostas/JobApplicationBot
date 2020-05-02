import urllib.request, urllib.error, urllib.parse
from typing import List, Tuple, Union
import time
import re
import time
import logging
from unidecode import unidecode

from .abstract_ad_site_crawler import AbstractAdSiteCrawler

logger = logging.getLogger('XeGrAdSiteCrawler')


class XeGrAdSiteCrawler(AbstractAdSiteCrawler):
    __slots__ = ('_stop_words', '_ad_site_url', '_anchor_class_name')

    _stop_words: List[str]
    _ad_site_url: str
    _anchor_class_name: str
    _ignored_emails: List = ['email@paroxos.com']

    def __init__(self, stop_words: List, ad_site_url: str = "https://www.xe.gr", anchor_class_name='result-list-narrow-item'):
        """
        Tha basic constructor. Creates a new instance of AdSiteCrawler using the specified credentials

        :param stop_words:
        """

        logger.debug("Initializing with stop_words: %s" % stop_words)
        self._ad_site_url = ad_site_url
        self._stop_words = stop_words
        self._anchor_class_name = anchor_class_name
        super().__init__()

    def get_new_ads(self, lookup_url: str, ads_checked: List, crawl_interval: int = 15) -> Tuple[str, Union[None, str]]:
        """
        Retrieves each sub-link's html, searches and yields an email for each of them.

        :param lookup_url:
        :param ads_checked:
        """

        if self._ad_site_url not in lookup_url:
            raise AdSiteCrawlerError(
                "The lookup_url: %s is not supported. The domain should be: %s" % (lookup_url, self._ad_site_url))
        if lookup_url[:4] != 'http':
            logger.warning("The lookup_url doesn't contain http:// or https://! Adding https:// ..")
            lookup_url = 'https://' + lookup_url

        logger.debug("ads_checked: %s" % ads_checked)
        search_page_html = self._retrieve_html_from_url(lookup_url)
        # Search for links in the main page's html, retrieve their html and look for emails inside them
        for ad_link in self._find_links_in_html(html_data=search_page_html, anchor_class_name=self._anchor_class_name):
            logger.debug("Input ad_link: %s" % ad_link)
            ad_linked_parsed = urllib.parse.quote(ad_link)
            if ad_linked_parsed[:4] != 'http':
                full_sub_link = self._ad_site_url + ad_linked_parsed
            else:
                full_sub_link = ad_link
            logger.debug("Checking constructed full_sub_link: %s" % full_sub_link)
            # Wait before checking next link to avoid bot ban
            logger.debug("Sleeping for crawl_interval={crawl_interval} seconds..".format(crawl_interval=crawl_interval))
            time.sleep(crawl_interval)
            if full_sub_link in ads_checked:
                logger.debug("It is in ads_checked, skipping..")
                continue
            ad_page_html = self._retrieve_html_from_url(full_sub_link)
            print("Type stop words: ", type(self._stop_words[0]))
            print("Type ad_page_html: ", type(ad_page_html))
            if any(unidecode(word).lower() in unidecode(ad_page_html).lower() for word in self._stop_words):
                logger.debug("It contains one of the stop words, skipping..")
                continue
            # Add the link inside the check list in order to avoid duplicate ads
            ads_checked.append(full_sub_link)
            emails_in_ad_page = self._find_emails_in_html(html_data=ad_page_html)
            if len(emails_in_ad_page) == 0:
                logger.debug("Found no emails in the ad page, returning None..")
                yield full_sub_link, None
            else:
                logger.debug("Found emails in the ad page, returning %s.." % emails_in_ad_page[0])
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
        logger.debug("HTML retrieved:\n%s" % (html))
        return html

    @staticmethod
    def _find_links_in_html(html_data: str, anchor_class_name: str = 'result-list-narrow-item') -> str:
        """
        Searches for sub-link patterns in html and yields each link.

        :param html_data:
        """

        logger.debug("Using anchor class name=%s" % anchor_class_name)
        logger.debug("Searching for sub-links in html..")

        pattern = re.compile(r"(<a[^<]*class=['\"][\sa-zA-Z\-]*{anchor_class_name}[\sa-zA-Z\-]*['\"][^<]*>)"
                             .format(anchor_class_name=anchor_class_name))
        a_tag_captured = pattern.findall(html_data)
        logger.debug("Anchor captured: %s" % a_tag_captured)
        for i in a_tag_captured:
            href_raw = i[str(i).find('href'):]
            href = href_raw[:href_raw.find(' ')].strip()
            logger.debug("Href captured: %s, and sliced: %s" % (href, href[6:-1]))
            yield href[6:-1]

    @classmethod
    def _find_emails_in_html(cls, html_data: str) -> List:
        """
        Searches for email patterns in html and returns list of emails.

        :param html:
        """

        logger.debug("Searching for emails in html..")

        pattern = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+(?:com|gr)', re.MULTILINE)
        emails = pattern.findall(html_data)
        logger.debug("All emails found in html: %s" % emails)
        return [email for email in emails if email not in cls._ignored_emails]


class AdSiteCrawlerError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
