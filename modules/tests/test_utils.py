import pytest
import re
import time
import random
import undetected_chromedriver as uc

from unittest import TestCase
from selenium import webdriver

from ..utils import (
    load_config,
    load_proxies,
    proxy_build_rotate,
    setup_user_agent,
    setup_selenium_driver_options,
    setup_uc_driver_options,
    ProxyExtension,
)


class TestUtils(TestCase):
    def setUp(self):
        self.proxies = load_proxies()
        self.blocked_urls = [
            'https://www.facebook.com/',
        ]

    def test_load_config(self):
        sections = ['MAIN', 'DB', 'SENTRY']
        config = load_config()
        self.assertTrue(config)
        config_sections = config.sections()
        for section in sections:
            self.assertTrue(section in config_sections)

    def test_load_proxies(self):
        proxies = load_proxies()
        self.assertTrue(isinstance(proxies, list))
        self.assertTrue(len(proxies))
        for proxy in proxies:
            self.assertTrue(isinstance(proxy, list))
            self.assertTrue(len(proxy) == 4)
            self.assertTrue(re.match(r'^\d+[.]\d+[.]\d+[.]\d+$', proxy[0]))
            self.assertTrue(re.match(r'^\d+$', proxy[1]))

    def test_proxy_build_rotate(self):
        proxy1 = proxy_build_rotate(self.proxies)
        proxy2 = proxy_build_rotate(self.proxies)
        proxy3 = proxy_build_rotate(self.proxies, protocol='https')
        match1 = re.match(r'^[a-z0-9]+[:][a-z0-9]+[@]\d+[.]\d+[.]\d+[.]\d+[:]\d+$', proxy1)
        match2 = re.match(r'^[a-z0-9]+[:][a-z0-9]+[@]\d+[.]\d+[.]\d+[.]\d+[:]\d+$', proxy2)
        match3 = re.match(r'^https://[a-z0-9]+[:][a-z0-9]+[@]\d+[.]\d+[.]\d+[.]\d+[:]\d+$', proxy3)
        matches = [match1, match2, match3]
        for match in matches:
            self.assertTrue(match)

    def test_setup_user_agent(self):
        user_agent1 = setup_user_agent()
        user_agent2 = setup_user_agent()
        self.assertTrue(user_agent1 != user_agent2)
        self.assertTrue(isinstance(user_agent1, str))
        self.assertTrue(isinstance(user_agent2, str))

    @pytest.mark.slow
    def test_setup_selenium_driver_options(self, test_url='https://google.com/'):
        options = setup_selenium_driver_options(headless=False)
        self.assertTrue(options)
        self.assertTrue('selenium' in options.__class__.__module__)
        driver = webdriver.Chrome(options=options)
        driver.get(test_url)
        time.sleep(1)
        driver.quit()

        options1 = setup_selenium_driver_options(platform='test123')
        self.assertFalse(options1)

    @pytest.mark.slow
    def test_setup_uc_driver_options(self, test_url='https://google.com/'):
        options = setup_uc_driver_options(headless=False)
        self.assertTrue(options)
        self.assertTrue('undetected_chromedriver' in options.__class__.__module__)
        driver = uc.Chrome(options=options)
        driver.get(test_url)
        time.sleep(1)
        driver.close()

    @pytest.mark.slow
    def test_use_selenium_with_proxy(self):
        """use_driver=True to test proxy with selenium"""
        proxy = random.choice(self.proxies)
        proxy_extension = ProxyExtension(*proxy)
        options = setup_selenium_driver_options(
            headless=False,
            # user_agent=setup_user_agent(),
            proxy_extension=proxy_extension)
        driver = webdriver.Chrome(options=options)
        driver.get(self.blocked_urls[0])
        time.sleep(2)
        driver.quit()

    @pytest.mark.slow
    def test_use_uc_with_proxy(self):
        """use_driver=True to test ProxyExtension with undetected_chromedriver"""
        proxy = random.choice(self.proxies)
        proxy_extension = ProxyExtension(*proxy)
        options = setup_uc_driver_options(
            headless=False,
            # user_agent=setup_user_agent(),
            proxy_extension=proxy_extension)
        driver = uc.Chrome(options=options)
        driver.get(self.blocked_urls[0])
        time.sleep(2)
        driver.quit()
