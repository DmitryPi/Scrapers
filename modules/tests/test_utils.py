import re
import time
import undetected_chromedriver as uc

from unittest import TestCase
from selenium import webdriver

from ..utils import (
    load_config,
    load_proxies,
    proxy_build_rotate,
    setup_user_agent,
    setup_selenium_proxy,
    setup_selenium_driver_options,
)


class TestUtils(TestCase):
    def setUp(self):
        pass

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
        proxies = load_proxies()
        proxy1 = proxy_build_rotate(proxies)
        proxy2 = proxy_build_rotate(proxies)
        proxy3 = proxy_build_rotate(proxies, protocol='https')
        self.assertTrue(proxy1 != proxy2)
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

    def test_setup_selenium_proxy(self):
        proxies = load_proxies()
        proxy = proxy_build_rotate(proxies)
        capabilities = setup_selenium_proxy(proxy)
        self.assertTrue(isinstance(capabilities, dict))
        self.assertTrue(capabilities['browserName'] == 'chrome')
        self.assertTrue(capabilities['proxy']['httpProxy'] == proxy)

    def test_setup_selenium_driver_options(self, use_driver=False, test_url='https://google.com'):
        options = setup_selenium_driver_options(headless=False)
        self.assertTrue(options)
        if use_driver:
            driver = webdriver.Chrome(options=options)
            driver.get(test_url)
            # time.sleep(1)
            driver.quit()

        options1 = setup_selenium_driver_options(platform='test123')
        self.assertFalse(options1)
