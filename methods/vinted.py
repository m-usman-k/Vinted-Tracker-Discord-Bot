import requests
from requests.exceptions import HTTPError

from typing import List, Dict
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qsl


class Item:
    def __init__(self, data , total_entries):
        self.raw_data = data
        self.total_entries = total_entries
        self.id = data["id"]
        self.title = data["title"]
        self.brand_title = data["brand_title"]
        try:
            self.size_title = data["size_title"]
        except:
            self.size_title = data["size_title"]
        self.currency = data["price"]["currency_code"]
        self.price = data["price"]["amount"]
        self.photo = data["photo"]["url"]
        self.url = data["url"]
        self.created_at_ts = datetime.fromtimestamp(
            data["photo"]["high_resolution"]["timestamp"], tz=timezone.utc
        )
        self.raw_timestamp = data["photo"]["high_resolution"]["timestamp"]

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(('id', self.id))

    def isNewItem(self, minutes=3):
        delta = datetime.now(timezone.utc) - self.created_at_ts
        return delta.total_seconds() < minutes * 60

class Requester:
    def __init__(self):

        self.HEADER = {
            "User-Agent": "PostmanRuntime/7.28.4",  # random.choice(USER_AGENTS),
            "Host": "www.vinted.fr",
        }
        self.VINTED_AUTH_URL = "https://www.vinted.fr/"
        self.MAX_RETRIES = 3
        self.session = requests.Session()
        self.session.headers.update(self.HEADER)

    def setLocale(self, locale):
        self.VINTED_AUTH_URL = f"https://{locale}/"
        self.HEADER = {
            "User-Agent": "PostmanRuntime/7.28.4",  # random.choice(USER_AGENTS),
            "Host": f"{locale}",
        }
        self.session.headers.update(self.HEADER)

    def get(self, url, params=None):
        """
        Perform a http get request.
        :param url: str
        :param params: dict, optional
        :return: dict
            Json format
        """
        tried = 0
        while tried < self.MAX_RETRIES:
            tried += 1
            with self.session.get(url, params=params) as response:

                if response.status_code == 401 and tried < self.MAX_RETRIES:
                    print(f"Cookies invalid retrying {tried}/{self.MAX_RETRIES}")
                    self.setCookies()

                elif response.status_code == 200 or tried == self.MAX_RETRIES:
                    return response

        return HTTPError

    def post(self, url, params=None):
        response = self.session.post(url, params)
        response.raise_for_status()
        return response

    def setCookies(self):
        self.session.cookies.clear_session_cookies()

        try:

            self.session.head(self.VINTED_AUTH_URL)
            print("Cookies set!")

        except Exception as e:
            print(
                f"There was an error fetching cookies for vinted\n Error : {e}"
            )


class Urls:
    VINTED_API_URL = f"/api/v2"
    VINTED_PRODUCTS_ENDPOINT = "catalog/items"

class Items:
    def search(self, url, nbrItems: int = 20, page: int =1, time: int = None, json: bool = False) -> List[Item]:
        locale = urlparse(url).netloc
        requester.setLocale(locale)

        params = self.parseUrl(url, nbrItems, page, time)
        url = f"https://{locale}{Urls.VINTED_API_URL}/{Urls.VINTED_PRODUCTS_ENDPOINT}"

        try:
            response = requester.get(url=url, params=params)
            response.raise_for_status()
            everything = response.json()
            items = everything["items"]
            if not json:
                return [Item(_item , everything["pagination"]["total_entries"]) for _item in items]
            else:
                return items

        except HTTPError as err:
            raise err


    def parseUrl(self, url, nbrItems=20, page=1, time=None) -> Dict:
        querys = parse_qsl(urlparse(url).query)

        params = {
            "search_text": "+".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "search_text"])
            ),
            "catalog_ids": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "catalog[]"])
            ),
            "color_ids": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "color_ids[]"])
            ),
            "brand_ids": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "brand_ids[]"])
            ),
            "size_ids": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "size_ids[]"])
            ),
            "material_ids": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "material_ids[]"])
            ),
            "status_ids": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "status[]"])
            ),
            "country_ids": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "country_ids[]"])
            ),
            "city_ids": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "city_ids[]"])
            ),
            "is_for_swap": ",".join(
                map(str, [1 for tpl in querys if tpl[0] == "disposal[]"])
            ),
            "currency": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "currency"])
            ),
            "price_to": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "price_to"])
            ),
            "price_from": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "price_from"])
            ),
            "page": page,
            "per_page": nbrItems,
            "order": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "order"])
            ),
            "time": time
        }

        return params
    
class Vinted:
    def __init__(self):
        self.items = Items()


requester = Requester()