from abc import ABC, abstractmethod


class AbstractAdSiteCrawler(ABC):
    __slots__ = ('_handler',)

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """
        Tha basic constructor. Creates a new instance of AdSiteCrawler using the specified credentials
        """

        pass