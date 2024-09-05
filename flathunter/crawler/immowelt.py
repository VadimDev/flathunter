"""Expose crawler for ImmoWelt"""
import re
import datetime
import hashlib

from bs4 import BeautifulSoup, Tag

from flathunter.logging import logger
from flathunter.abstract_crawler import Crawler

class Immowelt(Crawler):
    """Implementation of Crawler interface for ImmoWelt"""

    URL_PATTERN = re.compile(r'https://www\.immowelt\.de')

    def __init__(self, config):
        super().__init__(config)
        self.config = config

    def get_expose_details(self, expose):
        """Loads additional details for an expose by processing the expose detail URL"""
        soup = self.get_page(expose['url'])
        date = datetime.datetime.now().strftime("%2d.%2m.%Y")
        expose['from'] = date

        immo_div = soup.find("app-estate-object-informations")
        if not isinstance(immo_div, Tag):
            return expose
        immo_div = soup.find("div", {"class": "equipment ng-star-inserted"})
        if not isinstance(immo_div, Tag):
            return expose

        details = immo_div.find_all("p")
        for detail in details:
            if detail.text.strip() == "Bezug":
                date = detail.findNext("p").text.strip()
                no_exact_date_given = re.match(
                    r'.*sofort.*|.*Nach Vereinbarung.*',
                    date,
                    re.MULTILINE|re.DOTALL|re.IGNORECASE
                )
                if no_exact_date_given:
                    date = datetime.datetime.now().strftime("%2d.%2m.%Y")
                break
        expose['from'] = date
        return expose

    BASE_URL = "https://www.immowelt.de"

    def extract_data(self, soup: BeautifulSoup):
        """Extracts all exposes from a provided Soup object"""
        entries = []
        # Находим все элементы с data-testid="serp-card-testid"
        soup_res = soup.find_all("div", {"data-testid": "serp-card-testid"})
        if not soup_res:
            return []

        # Перебираем все найденные объявления
        for card in soup_res:
            try:
                title_el = card.find("a", {"data-testid": "card-mfe-covering-link-testid"})
                raw_title = title_el.get("title", "").strip() if title_el else ""
            except AttributeError:
                raw_title = ""

            try:
                price = card.find("div", {"data-testid": "cardmfe-price-testid"}).text.strip()
            except AttributeError:
                price = ""

            try:
                size = card.find("div", {"data-testid": "cardmfe-keyfacts-testid"}).find_all("div")[2].text.strip()
            except (IndexError, AttributeError):
                size = ""

            try:
                rooms = card.find("div", {"data-testid": "cardmfe-keyfacts-testid"}).find_all("div")[
                    0].text.strip().replace(" Zi.", "")
            except (IndexError, AttributeError):
                rooms = ""

            try:
                relative_url = title_el.get("href") if title_el else ""
                url = self.BASE_URL + relative_url if relative_url else ""
            except AttributeError:
                url = ""

            try:
                picture = card.find("img")
                image = picture.get("src") if picture else None
            except AttributeError:
                image = None

            try:
                address = card.find("div", {"data-testid": "cardmfe-description-box-address"}).text.strip()
            except AttributeError:
                address = ""

            formatted_title = (
                f"{raw_title}\n"
            )

            processed_id = int(hashlib.sha256(url.encode('utf-8')).hexdigest(), 16) % 10 ** 16 if url else None

            details = {
                'id': processed_id,
                'image': image,
                'url': url,
                'title': formatted_title,
                'rooms': rooms,
                'price': price,
                'size': size,
                'address': address,
                'crawler': 'Immowelt'
            }
            entries.append(details)

        return entries