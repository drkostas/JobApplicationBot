from abc import ABC, abstractmethod
from typing import List

class AbstractAdSiteCrawler(ABC):
    __slots__ = ('_stop_words',)

    _stop_words: List
    _ad_site_url: str

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """
        The basic constructor. Creates a new instance of AdSiteCrawler using the specified credentials
        """

        pass

    @abstractmethod
    def get_new_ads(self, *args, **kwargs):
        pass