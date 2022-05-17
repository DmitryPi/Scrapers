from unittest import TestCase

from ..utils import load_config
from ..scrapers import VKScraper


config = load_config()


class TestVKScraper(TestCase):
    def setUp(self):
        self.scraper = VKScraper()

    def test_vk(self):
        pass
