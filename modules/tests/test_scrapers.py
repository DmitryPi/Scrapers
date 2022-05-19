import pytest
import undetected_chromedriver as webdriver

from unittest import TestCase

from ..utils import load_config, setup_uc_driver_options
from ..scrapers import Scraper, VKScraper


config = load_config()


class TestScraper(TestCase, Scraper):
    def setUp(self):
        Scraper.__init__(self)
        self.options = setup_uc_driver_options(
            headless=False,
        )

    @pytest.mark.slow
    def test_sel_find_css(self):
        """Locate yandex search field"""
        driver = webdriver.Chrome(self.options)
        driver.get('https://yandex.ru/')
        item = self.sel_find_css(driver, 'input.input__control')
        self.assertTrue(item)
        item = self.sel_find_css(driver, 'input.input__cossdfdfgntrol', wait=2)
        self.assertFalse(item)
        items = self.sel_find_css(driver, 'input.input__control', many=True)
        self.assertTrue(items)
        self.assertTrue(len(items))
        self.assertTrue(isinstance(items, list))

    def test_sel_save_cookies(self):
        pass

    def test_sel_load_cookies(self):
        pass


class TestVKScraper(TestCase, VKScraper):
    def setUp(self):
        VKScraper.__init__(self)

    @pytest.mark.slow
    def test_vk_get_page(self):
        self.vk_get_page(self.urls[0])
