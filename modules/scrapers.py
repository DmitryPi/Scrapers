import pickle
import time
import random
import json
import os
import undetected_chromedriver as uc_webdriver

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.error import HTTPError

from .utils import (
    load_config,
    load_proxies,
    handle_error,
    setup_user_agent,
    setup_selenium_driver_options,
    setup_uc_driver_options,
    ProxyExtension,
)


class Scraper:
    def __init__(self):
        """WB Twitter Instagram bet365.com"""
        self.cookies_path = 'assets/{}cookies.pkl'
        self.proxies = load_proxies()
        self.driver = None

    def create_driver_instance(self, driver: str, headless=False, use_ua=False, use_proxy=False):
        """Create webdriver instance with designated params and set self.driver"""
        options = setup_uc_driver_options if driver == 'uc' else setup_selenium_driver_options
        driver = uc_webdriver if driver == 'uc' else webdriver
        proxy = random.choice(self.proxies)
        proxy_extension = ProxyExtension(*proxy) if use_proxy else None
        user_agent = setup_user_agent() if use_ua else ''
        options = options(
            headless=headless,
            user_agent=user_agent,
            proxy_extension=proxy_extension,
        )
        self.driver = driver.Chrome(options=options)

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
                return True
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
        self.urls = json.loads(self.config['VK']['urls'])

    def vk_get_group_post_data(self, author, date, text):
        post = {}
        post_author = author.text
        post_date = date.text
        post_text = text.text
        post.update({
            'post_author': post_author,
            'post_date': post_date,
            'post_text': post_text,
        })
        return post

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
        url = self.urls[0]
        try:
            self.create_driver_instance(
                'uc',
                headless=False,
                # use_ua=True,
                # use_proxy=True
            )
            self.driver.get(url)
            # self.vk_login(driver)
            # self.sel_scroll_down(driver, scrolls=5, delay=3)
            item_authors = self.sel_find_css(
                self.driver, '.post_author', many=True, wait=2)
            item_dates = self.sel_find_css(
                self.driver, '.post_date', many=True, wait=2)
            item_texts = self.sel_find_css(
                self.driver, '.wall_post_text', many=True, wait=2)
            for i, item in enumerate(item_dates):
                data = self.vk_get_group_post_data(item_authors[i], item_dates[i], item_texts[i])
                from pprint import pprint
                pprint(data)
        except HTTPError as e:
            print(url, '\n', e)
        except Exception as e:
            handle_error(e)


class WBScraper(Scraper):
    def __init__(self, config=None):
        Scraper.__init__(self)
        self.config = config if config else load_config()
        self.urls = json.loads(self.config['WB']['urls'])
        self.search_words = json.loads(self.config['WB']['search_words'])

    def wb_get_page(self, url):
        self.driver.get(url)

    def wb_search_items(self):
        if not self.driver:
            return
        search_input = self.sel_find_css(self.driver, 'input.search-catalog__input')
        for word in self.search_words:
            search_input.send_keys(word)
            # time.sleep(2)
            break

    def run(self):
        url = self.urls[0]
        try:
            self.create_driver_instance(
                'sel',
                headless=False,
                # use_ua=True,
                # use_proxy=True
            )
            self.wb_get_page(url)
            self.wb_search_items()
        except HTTPError as e:
            print(url, '\n', e)
        except Exception as e:
            handle_error(e)
