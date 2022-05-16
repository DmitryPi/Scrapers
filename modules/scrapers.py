import time
import undetected_chromedriver as uc

from .utils import load_proxies


class VKScraper:
    def __init__(self, config=None):
        self.config = config
        self.proxies = load_proxies()
