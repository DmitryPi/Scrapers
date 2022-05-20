import configparser
import codecs
import logging
import os
import random
import shutil
import tempfile
import undetected_chromedriver as uc

from selenium import webdriver
from fake_useragent import UserAgent


def build_config(config_name='config.ini') -> None:
    """Build default config section key/values"""
    config = configparser.ConfigParser()
    config.update({
        'MAIN': {
            'debug': True,
        },
        'DB': {
            'table': 'scrapers'
        },
        'SENTRY': {
            'dsn': '',
            'log_level': 20
        },
    })
    with open(config_name, 'w') as f:
        print('- Creating new config')
        config.write(f)


def load_config(config_fp='config.ini'):
    """load config from `config_fp`; build default if not found"""
    config = configparser.ConfigParser()
    try:
        config.read_file(codecs.open(config_fp, 'r', 'utf8'))
    except FileNotFoundError:
        print('- Config not found')
        build_config()
        config.read_file(codecs.open(config_fp, 'r', 'utf8'))
    return config


def handle_error(error, to_file=False, to_file_path='error_log.txt'):
    """Handle error by writing to file/sending to sentry/raising"""
    if to_file:
        with open(to_file_path, 'a', encoding='utf-8') as f:
            f.write(error + '\n')
    else:
        raise error


def load_proxies(filename='proxies.txt'):
    """Load proxies from local file"""
    proxies = []
    try:
        with open(filename, 'r') as file:
            proxies_raw = file.readlines()
            for line in proxies_raw:
                proxies.append(line.strip().split(':'))
        return proxies
    except FileNotFoundError:
        logging.warning(f'Proxy file: {filename} not found')
        return proxies
    except Exception as e:
        handle_error(e)


def proxy_build_rotate(proxies: list, protocol='') -> str:
    """Build http/https proxy for list of proxies"""
    proxy = random.choice(proxies)
    if protocol:
        proxy = f'{protocol}://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}'
    else:
        proxy = f'{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}'
    print('- Proxy: ', proxy)
    return proxy


def setup_user_agent() -> str:
    """Generate user_agent string"""
    user_agent = UserAgent()
    return user_agent.random


def setup_selenium_driver_options(
        headless=True, disable_gpu=True, silent=True, wh=(1800, 1000),
        user_agent='', proxy_extension=None, platform='chrome') -> bytes:
    """Setup driver option for chrome; Can be used by selenium"""
    try:
        if platform == 'chrome':
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument('headless')
            if disable_gpu:
                options.add_argument('disable-gpu')
            options.add_argument(f'window-size={wh[0]},{wh[1]}')
            options.add_argument('log-level=3')
            options.add_argument('lang=en-US')
            if silent:
                options.add_argument('silent')
            if user_agent:
                options.add_argument(f'--user-agent={user_agent}')
            if proxy_extension:
                options.add_argument(f"--load-extension={proxy_extension.directory}")
            return options
        else:
            logging.warning('Unknown kwarg `platform={}` passed in {}'.format(
                platform,
                setup_selenium_driver_options.__name__,
            ))
    except Exception as e:
        handle_error(e)


def setup_uc_driver_options(
        headless=True, disable_gpu=True, wh=(1800, 1000),
        user_agent='', proxy_extension=None) -> bytes:
    """Driver options for undetected_chromedriver; only Chrome"""
    try:
        options = uc.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        if disable_gpu:
            options.add_argument('--disable-gpu')
        options.add_argument(f'--window-size={wh[0]},{wh[1]}')
        options.add_argument('--log-level=3')
        options.add_argument('--lang=en-US')
        options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
        if user_agent:
            options.add_argument(f'--user-agent={user_agent}')
        if proxy_extension:
            options.add_argument(f"--load-extension={proxy_extension.directory}")
        return options
    except Exception as e:
        handle_error(e)


class ProxyExtension:
    """Enables proxies in Selenium & undetected_chromedriver"""
    manifest_json = """{
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {"scripts": ["background.js"]},
        "minimum_chrome_version": "76.0.0"
    }"""

    background_js = """
        var config = {
            mode: "fixed_servers",
            rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: %d
                },
                bypassList: ["localhost"]
            }
        };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            { urls: ["<all_urls>"] },
            ['blocking']
        );
    """

    def __init__(self, host, port, user, password):
        self._dir = os.path.normpath(tempfile.mkdtemp())

        manifest_file = os.path.join(self._dir, "manifest.json")
        with open(manifest_file, mode="w") as f:
            f.write(self.manifest_json)

        background_js = self.background_js % (host, int(port), user, password)
        background_file = os.path.join(self._dir, "background.js")
        with open(background_file, mode="w") as f:
            f.write(background_js)

    @property
    def directory(self):
        return self._dir

    def __del__(self):
        shutil.rmtree(self._dir)
