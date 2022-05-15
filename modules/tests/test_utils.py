import re

from unittest import TestCase

from ..utils import load_config, load_proxies


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
