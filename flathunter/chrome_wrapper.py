import re
import subprocess
from typing import List
from sys import platform
import undetected_chromedriver as uc

from flathunter.logging import logger
from flathunter.exceptions import ChromeNotFound

# Регулярное выражение для поиска версии Chromium
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
    chrome_options = uc.ChromeOptions()  # pylint: disable=no-member

    # Указываем путь к бинарнику Chromium для ARM
    chrome_options.binary_location = "/usr/bin/chromium-browser"

    if platform == "darwin":
        chrome_options.add_argument("--headless")
    if driver_arguments is not None:
        for driver_argument in driver_arguments:
            chrome_options.add_argument(driver_argument)

    # На ARM используем chromium, так что может не быть необходимости в проверке версии
    try:
        chrome_version = get_chrome_version()
        driver = uc.Chrome(version_main=chrome_version, options=chrome_options)  # pylint: disable=no-member
    except ChromeNotFound:
        # Если Chrome или Chromium не найден, используем по умолчанию Chromium
        driver = uc.Chrome(options=chrome_options)  # pylint: disable=no-member

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
