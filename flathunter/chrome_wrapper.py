import re
import subprocess
from typing import List
from sys import platform
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from flathunter.logging import logger
from flathunter.exceptions import ChromeNotFound

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

def get_firefox_driver(driver_arguments=None):
    """Configure Firefox WebDriver"""
    logger.info('Initializing Firefox WebDriver for crawler...')
    firefox_options = FirefoxOptions()

    # Указываем опции для Firefox, такие как режим headless, если нужно
    if platform == "darwin":
        firefox_options.add_argument("--headless")
    if driver_arguments is not None:
        for driver_argument in driver_arguments:
            firefox_options.add_argument(driver_argument)

    # Указываем путь к Geckodriver
    firefox_service = FirefoxService(executable_path="/usr/bin/geckodriver")

    try:
        driver = webdriver.Firefox(service=firefox_service, options=firefox_options)
    except Exception as e:
        logger.error(f"Failed to start Firefox WebDriver: {e}")
        raise

    # Добавьте здесь дополнительные команды для Firefox, если это необходимо

    return driver
