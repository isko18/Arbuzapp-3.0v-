import hashlib
import hmac
import random
import requests
from loguru import logger

from config import PROXY_EXISTS, PROXY

class ArbuzApp:
    def __init__(self, user_id, byte_key, telegram_init_data) -> None:
        self.byte_key = byte_key
        self.user_id = user_id
        self.base_url: str = 'https://arbuz.betty.games/api'
        self.headers: dict = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/79.0.3945.117 YaBrowser/79.0.3945.117 Safari/537.36',
            'x-telegram-init-data': telegram_init_data,
        }
        self.proxy: dict = self.get_proxy()

    def get_proxy(self) -> dict:
        if PROXY_EXISTS:
            return {'https': f'http://{PROXY}', 'http': f'http://{PROXY}'}
        return {'https': '', 'http': ''}

    def click(self, last_click) -> tuple[str, int, float, float, str]:
        my = f"{self.user_id}:{last_click}"
        message = my.encode()
        h = hmac.new(self.byte_key, message, hashlib.sha256).hexdigest()
        payload = {'count': random.randint(35, 35), 'hash': h}
        logger.info(f"Sending click request with headers: {self.headers} and payload: {payload}")
        try:
            response = requests.post(
                f'{self.base_url}/click/apply',
                headers=self.headers,
                json=payload,
                proxies=self.proxy,
                timeout=10
            )
            logger.info(f"Click response: {response.status_code} - {response.text}")
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            logger.debug(f"Response content: {response.content}")
            return None, None, None, None, None
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request exception occurred: {req_err}")
            return None, None, None, None, None

        json_data = response.json()
        return json_data.get("code"), json_data.get("count"), json_data.get("currentEnergy"), json_data.get("lastClickSeconds"), h

    def me_info(self) -> tuple[int, float, int, float]:
        logger.info(f"Sending me_info request with headers: {self.headers}")
        try:
            response = requests.get(f'{self.base_url}/users/me', headers=self.headers, proxies=self.proxy, timeout=10)
            logger.info(f"me_info response: {response.status_code} - {response.text}")
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            logger.debug(f"Response content: {response.content}")
            return 0, 0, 0, 0   
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request exception occurred: {req_err}")
            return 0, 0, 0, 0

        json_data = response.json()
        return json_data.get("clicks"), json_data.get("energyBoostSum"), json_data.get("energyLimit"), json_data.get("lastClickSeconds")
