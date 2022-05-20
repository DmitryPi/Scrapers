import pickle
import time
import json
import os
import undetected_chromedriver as webdriver

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .utils import load_config, load_proxies, handle_error, setup_uc_driver_options


class Scraper:
    def __init__(self):
        """WB VK Twitter"""
        self.cookies_path = 'assets/{}cookies.pkl'

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

    def sel_wait_until(self, driver, selector, wait=5):
        """Selenium wait.until shortcut"""
        wait = WebDriverWait(driver, wait)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

    def sel_save_cookies(self, driver, prefix=''):
        cookies = driver.get_cookies()
        pickle.dump(cookies, open(self.cookies_path.format(prefix), 'wb'))

    def sel_load_cookies(self, driver, prefix=''):
        try:
            cookies_path = self.cookies_path.format(prefix)
            if os.path.exists(cookies_path):
                cookies = pickle.load(open(cookies_path, "rb"))
                for cookie in cookies:
                    driver.add_cookie(cookie)
                driver.refresh()
        except Exception as e:
            handle_error(e)

    def sel_scroll_down(self, driver, height=0, scrolls=1, delay=0):
        """Scroll down to {height} or 'scroll' amount of times"""
        if not height:
            last_height = driver.execute_script("return document.body.scrollHeight")
            for i in range(scrolls):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(delay)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    print('Reached the end of page')
                    break
                last_height = new_height
        else:
            driver.execute_script('window.scrollTo(0, {})'.format(height))


class VKScraper(Scraper):
    def __init__(self, config=None):
        Scraper.__init__(self)
        self.config = config if config else load_config()
        self.proxies = load_proxies()
        self.urls = json.loads(self.config['VK']['urls'])

    def vk_get_group_post_item(self, driver):
        pass

    def vk_login(self, driver):
        """TODO: Solve VK load_cookies relogin returns 429 error"""
        # find login btn
        login_btn = self.sel_find_css(driver, 'button.quick_login_button', wait=2)
        login_btn.click()
        # find login input field - send keys
        log_input = self.sel_find_css(driver, 'input[name="login"]', wait=5)
        log_input.send_keys(self.config['VK']['login'])
        time.sleep(.5)
        self.sel_find_css(driver, '.vkc__EnterLogin__button button').click()
        # find password input field - send keys
        pass_input = self.sel_find_css(driver, 'input[name="password"]', wait=5)
        pass_input.send_keys(self.config['VK']['password'])
        time.sleep(.5)
        self.sel_find_css(driver, '.vkc__EnterPasswordNoUserInfo__buttonWrap button').click()
        # check if we're logged in
        profile = self.sel_find_css(driver, '.TopNavBtn__profileLink', wait=5)
        if profile:
            print('We have successfully logged in!')
            self.sel_save_cookies(driver, prefix='vk_')

    def run(self):
        try:
            url = self.urls[0]
            options = setup_uc_driver_options(headless=False)
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            self.vk_login(driver)
            self.sel_scroll_down(driver, scrolls=5, delay=3)
        except Exception as e:
            handle_error(e)


class WBScraper(Scraper):
    def __init__(self, config=None):
        Scraper.__init__(self)
        self.window = (1800, 1000)
        self.config = config if config else load_config()
        self.urls = json.loads(self.config['WB']['urls'])

    def run(self):
        pass
