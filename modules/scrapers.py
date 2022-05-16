import time
import undetected_chromedriver as uc

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .utils import load_proxies


class VKScraper:
    def __init__(self, config=None):
        self.config = config
        self.proxies = load_proxies()
