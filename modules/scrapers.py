import time
import json
import undetected_chromedriver as webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .utils import load_config, load_proxies, setup_uc_driver_options


class VKScraper:
    def __init__(self, config=None):
        self.config = config if config else load_config()
        self.proxies = load_proxies()
        self.urls = json.loads(self.config['VK']['urls'])
        print(self.urls)

    def vk_login(self):
        options = setup_uc_driver_options(headless=False)
        driver = webdriver.Chrome(options=options)
        for url in self.urls:
            driver.get(url)
        driver.quit()

    def vk_lifecicle(self):
        """check login -> login/visit page -> get item data"""

    def run(self):
        pass
