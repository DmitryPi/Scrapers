import re

from unittest import TestCase

from ..utils import load_config, load_proxies, proxy_build_rotate


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
