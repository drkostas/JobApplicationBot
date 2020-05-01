import unittest
import os
import logging
import http.server
import socketserver
import urllib.parse
from typing import Tuple, List, Dict
import threading

from ad_site_crawler.xegr_ad_site_crawler import XeGrAdSiteCrawler

logger = logging.getLogger('TestXeGrAdSiteCrawler')


class TestXeGrAdSiteCrawler(unittest.TestCase):
    __slots__ = (
        'encoded_search_params', 'httpd',
        'html_sub_links', 'html_file_with_links_path',
        'html_file_with_email_path_1', 'html_file_with_email_path_2',
        'html_file_with_email_path_3', 'html_file_with_email_path_4')

    stop_words: List = ['Senior']
    search_params: Dict = {"q1": 1, "q2": 2}
    encoded_search_params: str
    httpd: socketserver.TCPServer
    html_sub_links: List
    html_file_with_links_path: str
    html_file_with_email_path_1: str
    html_file_with_email_path_2: str
    PORT: int = 8111
    test_data_path: str = os.path.join('test_data', 'test_xegr_ad_site_crawler')

    def test__find_emails_in_html(self):
        ad_site_crawler = XeGrAdSiteCrawler(stop_words=[])
        # Load the html file
        logger.info("Loading html file..")
        with open(self.html_file_with_email_path_2, 'r') as html_f:
            html_file = html_f.read()
        # Search for emails in the loaded html
        logger.info("Calling _find_emails_in_html()..")
        returned_emails = ad_site_crawler._find_emails_in_html(html_data=html_file)
        # Check if the correct email was loaded
        expected_emails = ['efi.koulourianou@gmail.com', 'efi.koulourianou@gmail.com']
        self.assertListEqual(expected_emails, returned_emails)

    def test__find_links_in_html(self):
        ad_site_crawler = XeGrAdSiteCrawler(stop_words=[])
        # Load the html file
        logger.info("Loading html file..")
        with open(self.html_file_with_links_path, 'r') as html_f:
            html_file = html_f.read()
        # Search for links in the loaded html
        logger.info("Calling _find_links_in_html()..")
        returned_links = list(ad_site_crawler._find_links_in_html(html_data=html_file))
        # Check if the correct email was loaded
        expected_links = self.html_sub_links
        self.assertListEqual(expected_links, [urllib.parse.quote(link) for link in returned_links])

    def test__retrieve_html_from_url_search_page(self):
        ad_site_crawler = XeGrAdSiteCrawler(stop_words=[])
        # Load the html file
        logger.info("Loading html file..")
        with open(self.html_file_with_links_path, 'r') as html_f:
            html_file_links = html_f.read()
        # Retrieve the html from the local server
        logger.info("Calling _retrieve_html_from_url()..")
        returned_html_links = ad_site_crawler._retrieve_html_from_url(
            'http://localhost:{port}'
            '/search?{encoded_search_params}'.format(port=self.PORT,
                                                     encoded_search_params=self.encoded_search_params))
        # Check if the correct html was loaded
        self.assertEqual(html_file_links, returned_html_links)

    def test__retrieve_html_from_url_sub_page(self):
        ad_site_crawler = XeGrAdSiteCrawler(stop_words=[])
        # Load the html file
        logger.info("Loading html file..")
        with open(self.html_file_with_email_path_1, 'r') as html_f:
            html_file_email_1 = html_f.read()
        # Retrieve the html from the local server
        logger.info("Calling _retrieve_html_from_url()..")
        returned_html_links = ad_site_crawler._retrieve_html_from_url(
            'http://localhost:{port}'
            '{email_page}'.format(port=self.PORT,
                                  email_page=self.html_sub_links[0]))
        # Check if the correct html was loaded
        self.assertEqual(html_file_email_1, returned_html_links)

    def test_get_new_ads(self):
        ad_site_crawler = XeGrAdSiteCrawler(stop_words=self.stop_words,
                                            ad_site_url='http://localhost:{port}'.format(port=self.PORT))
        # Retrieve the html from the local server
        logger.info("Calling get_new_ads()..")
        returned_ads = list(ad_site_crawler.get_new_ads(url_search_params=self.search_params,
                                                        ads_checked=['http://localhost:{port}'.format(port=self.PORT) +
                                                                     self.html_sub_links[1]]))
        # Check if the correct html was loaded
        expected_ads = [('http://localhost:{port}{sublink}'.format(port=self.PORT,
                                                                   sublink=self.html_sub_links[2]),
                         None),
                        ('http://localhost:{port}{sublink}'.format(port=self.PORT,
                                                                   sublink=self.html_sub_links[3]),
                         'epharmacy137@gmail.com'),
                        ]
        self.assertListEqual(sorted(expected_ads, key=lambda x: x[0]),
                             sorted(returned_ads, key=lambda x: x[0]))

    @classmethod
    def init_local_server(cls, port: int = 8111) -> socketserver.TCPServer:
        class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/search?{encoded_search_params}'.format(
                        encoded_search_params=cls.encoded_search_params):
                    self.path = cls.html_file_with_links_path
                elif self.path == cls.html_sub_links[0]:
                    self.path = cls.html_file_with_email_path_1
                elif self.path == cls.html_sub_links[1]:
                    self.path = cls.html_file_with_email_path_2
                elif self.path == cls.html_sub_links[2]:
                    self.path = cls.html_file_with_email_path_3
                elif self.path == cls.html_sub_links[3]:
                    self.path = cls.html_file_with_email_path_4
                    logger.info("Local server requested path: %s" % self.path)
                return http.server.SimpleHTTPRequestHandler.do_GET(self)

        return socketserver.TCPServer(("", port), MyHttpRequestHandler)

    @staticmethod
    def _setup_log() -> None:
        # noinspection PyArgumentList
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            handlers=[logging.StreamHandler()
                                      ]
                            )

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    @classmethod
    def setUpClass(cls):
        cls._setup_log()
        cls.encoded_search_params = urllib.parse.urlencode(cls.search_params)
        cls.html_file_with_links_path = os.path.join(cls.test_data_path, 'file_with_links.html')
        cls.html_file_with_email_path_1 = os.path.join(cls.test_data_path, 'file_with_email_1.html')
        cls.html_file_with_email_path_2 = os.path.join(cls.test_data_path, 'file_with_email_2.html')
        cls.html_file_with_email_path_3 = os.path.join(cls.test_data_path, 'file_with_email_3.html')
        cls.html_file_with_email_path_4 = os.path.join(cls.test_data_path, 'file_with_email_4.html')
        cls.html_sub_links = [urllib.parse.quote(link) for link in
                              ['/jobs/programmatistes-mhxanikoi-h-y|ad-96230841.html',
                               '/jobs/programmatistes-mhxanikoi-h-y|ad-659824116.html',
                               '/jobs/programmatistes-mhxanikoi-h-y|ad-94456892.html',
                               '/jobs/programmatistes-mhxanikoi-h-y|ad-579027979.html']]
        # Server the html file from local server
        logger.info("Serving html file to local server. Base: http://localhost:{port}/search?{encoded_search_params}"
                    .format(port=cls.PORT, encoded_search_params=cls.encoded_search_params))
        cls.httpd = cls.init_local_server(port=cls.PORT)
        server_thread = threading.Thread(target=cls.httpd.serve_forever)
        server_thread.start()

    @classmethod
    def tearDownClass(cls):
        # try:
        #     import time
        #     while True:
        #         time.sleep(5)
        # except KeyboardInterrupt:
        #     logger.info("Shutting down server..")
        cls.httpd.shutdown()
        cls.httpd.server_close()


if __name__ == '__main__':
    unittest.main()
