import time
import json
import undetected_chromedriver as webdriver

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .utils import load_config, load_proxies, setup_uc_driver_options


class Scraper:
    def __init__(self):
        pass

    def sel_find_css(self, driver, selector, many=False, wait=0):
        """Selenium find_element/s shortcut; Explicit wait for element wait=seconds"""
        find_call = driver.find_elements if many else driver.find_element
        if wait:
            wait *= 2  # check every .5s
            result = None
            for i in range(wait):
                try:
                    result = find_call(by=By.CSS_SELECTOR, value=selector)
                    if result:
                        return result
                except NoSuchElementException:
                    time.sleep(0.5)
        else:
            return find_call(by=By.CSS_SELECTOR, value=selector)


class VKScraper(Scraper):
    def __init__(self, config=None):
        Scraper.__init__(self)
        self.config = config if config else load_config()
        self.proxies = load_proxies()
        self.urls = json.loads(self.config['VK']['urls'])

    def vk_get_page(self, url):
        options = setup_uc_driver_options(headless=False)
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        'quick_login_button'

    def vk_login(self):
        pass

    def vk_lifecicle(self):
        """check login -> login/visit page -> get item data"""

    def run(self):
        pass
