import re
import subprocess
from typing import List
from sys import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

from flathunter.logging import logger
from flathunter.exceptions import ChromeNotFound

CHROME_VERSION_REGEXP = re.compile(r'.* (\d+\.\d+\.\d+\.\d+)( .*)?')
CHROME_BINARY_NAMES = ['chromium-browser', 'chromium']

def get_command_output(args) -> List[str]:
    """Run a command and return stdout"""
    try:
        with subprocess.Popen(args,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              universal_newlines=True) as process:
            if process.stdout is None:
                return []
            return process.stdout.readlines()
    except FileNotFoundError:
        return []

def get_chrome_version() -> int:
    """Determine the correct name for the chrome binary"""
    for binary_name in CHROME_BINARY_NAMES:
        try:
            version_output = get_command_output([binary_name, '--version'])
            if not version_output:
                continue
            match = CHROME_VERSION_REGEXP.match(version_output[0])
            if match is None:
                continue
            return int(match.group(1).split('.')[0])
        except FileNotFoundError:
            pass
    raise ChromeNotFound()

def get_chrome_driver(driver_arguments=None):
    """Configure Chrome WebDriver"""
    logger.info('Initializing Chrome WebDriver for crawler...')
    chrome_options = ChromeOptions()

    # Указываем путь к бинарнику Chromium для ARM
    chrome_options.binary_location = "/usr/bin/chromium-browser"

    if platform == "darwin":
        chrome_options.add_argument("--headless")
    if driver_arguments is not None:
        for driver_argument in driver_arguments:
            chrome_options.add_argument(driver_argument)

    # Настройка сервиса драйвера для Chromium на ARM
    chrome_service = ChromeService(executable_path="/usr/lib/chromium-browser/chromedriver")

    try:
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    except Exception as e:
        logger.error(f"Failed to start Chrome WebDriver: {e}")
        raise

    driver.execute_cdp_cmd(
        "Network.setUserAgentOverride",
        {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                         "AppleWebKit/537.36 (KHTML, like Gecko)"
                         "Chrome/120.0.0.0 Safari/537.36"
        },
    )

    driver.execute_cdp_cmd('Network.setBlockedURLs',
                           {"urls": ["https://api.geetest.com/get.*"]})
    driver.execute_cdp_cmd('Network.enable', {})
    return driver
