from enum import Enum


class Exchange(Enum):
    Binance = 1
    Huobi = 2
    Gemini = 3


class BaseDataAPI:

    def __init__(self, exchange: Exchange, api_key: str, secrete_key: str):
        self.api_key = api_key
        self.secrete_key = secrete_key
        self.exchange = exchange

    def set_exchange(self, exchange: Exchange):
        self.exchange = exchange
        return self

    def set_api_key(self, api_key: str):
        self.api_key = api_key
        return self

    def set_secrete_key(self, secret_key: str):
        self.secrete_key = secret_key
        return self

