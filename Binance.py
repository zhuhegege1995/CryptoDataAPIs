import sys

from BaseDataAPI import BaseDataAPI, Exchange
from utils import TimeManager

import logging
import requests

import pandas as pd
import numpy as np

log = logging.getLogger("Binance-DataAPI-Logger")

"""Symbols"""

BTCUSDT = "BTCUSDT"

"""interval"""


class Interval:
    ONE_MINUTE = "1m",
    THREE_MINUTE = "3m",
    FIVE_MINUTE = "5m",
    FIFTEEN_MINUTE = "15m",
    THIRTY_MINUTE = "30m",
    ONE_HOUR = "1h",
    TWO_HOUR = "2h",
    FOUR_HOUR = "4h",
    SIX_HOUR = "6h",
    EIGHT_HOUR = "8h",
    TWELVE_HOUR = "12h",
    ONE_DAY = "1d",
    THREE_DAY = "3d",
    ONE_WEEK = "1w",
    ONE_MONTH = "1M"

    def __init__(self):
        pass


class Binance(BaseDataAPI):

    def __init__(self, api_key: str = None, secrete_key: str = None):
        super().__init__(Exchange.Binance, api_key, secrete_key)
        self.exchange_info = None
        self.depth = None
        self.recent_trades = None
        self.historical_trades = None
        self.candles = None

    def __str__(self):
        return "exchange: {}, api key: {}\n".format(self.exchange, self.api_key)

    def get_exchange_info(self):
        res = requests.get("https://api.binance.us/api/v3/exchangeInfo")
        if res.status_code == 404:
            log.error("The exchange information is not available, please try later")
            return None

        self.exchange_info = res.json()
        return self.exchange_info

    def get_rate_limits(self):
        if self.exchange_info is None:
            ret = self.get_exchange_info()
            if ret is None:
                return

        return pd.DataFrame(self.exchange_info['rateLimits'])

    def get_symbols_information(self):
        if self.exchange_info is None:
            ret = self.get_exchange_info()
            if ret is None:
                return

        return pd.DataFrame(self.exchange_info['symbols'])

    def get_market_depth_helper(self, symbol: str, limit: int):
        """Get real time market depth (order book).
        This method is NOT recommended to be called directly by users。 For using this function, please use
        method get_market_depth()
        Args:
            symbol:symbol of the asset, e.g. BTCUSD
            limit: a value in [5, 10, 20, 50, 100, 500, 1000, 5000].

        Returns:
            a json object containing the lastUpdateId of the order book, and two-dimensional arrays of ask & bid books
        """
        if symbol is None or limit is None:
            log.error("symbol and limit cannot be empty")
            return

        if limit not in [5, 10, 20, 50, 100, 500, 1000, 5000]:
            log.error("please use valid limit value: [5, 10, 20, 50, 100, 500, 1000, 5000]")
            return

        res = requests.get("https://api.binance.us/api/v3/depth", params={"symbol": symbol,
                                                                          "limit": limit})
        if res.status_code == 404:
            log.error("The depth information is not available, please try later")
            return None

        self.depth = res.json()
        return self.depth

    def get_market_depth(self, symbol: str, limit: int, mode: int = 0):
        """Get real time market depth (order book).
        Args:
            :param symbol:symbol of the asset, e.g. BTCUSD
            :param limit: a value in [5, 10, 20, 50, 100, 500, 1000, 5000].
            :param mode： 0 means returning a simplified order book, which is a little more efficient;
        Returns:
            a dictionary containing the order book information:
            {
                'lastUpdateId'
                'df_asks': dataframe of the ask book,
                'df_bids': dataframe of the bid book
            }
        """

        if self.depth is None:
            self.get_market_depth_helper(symbol, limit)

        try:
            df_bids = pd.DataFrame()
            df_asks = pd.DataFrame()
            if self.depth is not None:
                df_bids = pd.DataFrame(np.array(self.depth['bids']).astype('float64')) \
                    .rename(columns={0: 'Price', 1: 'volume'})

                df_asks = pd.DataFrame(np.array(self.depth['asks']).astype('float64')) \
                    .rename(columns={0: 'Price', 1: 'volume'}) \
                    .sort_values(by=['Price'], ascending=False)

            if mode == 1:
                df_bids.index = ["bid_" + str(s) for s in list(df_bids.index)]
                df_asks.index = ["ask_" + str(s) for s in list(df_asks.index)]

            return {'lastUpdateId': self.depth['lastUpdateId'],
                    'asks': df_asks,
                    'bids': df_bids}

        except ValueError as e:
            log.error("The market depth list for symbol {} is not available".format(symbol))
            return None

        except KeyError as e:
            log.error("The market depth list for symbol {} is not available".format(symbol))
            return None


    def get_recent_trades_helper(self, symbol: str, limit: int = 500):

        res = requests.get("https://api.binance.us/api/v3/trades", params={"symbol": symbol,
                                                                           "limit": limit})

        if res.status_code == 404:
            log.error("The recent trade list is not available, please try this later")
            return None

        self.recent_trades = res.json()

        return res.json()

    def get_recent_trades(self, symbol: str, limit: int = 500):

        res = self.get_recent_trades_helper(symbol, limit)

        try:
            if res is not None:
                return pd.DataFrame(res).set_index('id').astype({'price': 'float64',
                                                                 'qty': 'float64',
                                                                 'quoteQty': 'float64'})
        except ValueError as e:
            log.error("The recent trade list for symbol {} is not available".format(symbol))
            return None

        return None

    def get_historical_trades_helper(self, symbol: str, limit: int = 500, fromId: int = 0):

        if self.api_key is None:
            log.error("Please set api_key before calling get_historical_trades_helper()")
            return None

        headers = {"X-MBX-APIKEY": self.api_key}

        res = requests.get("https://api.binance.us/api/v3/historicalTrades", params={"symbol": symbol,
                                                                                     "limit": limit,
                                                                                     "fromId": fromId}, headers=headers)
        if res.status_code == 404:
            log.error("The historical trade list is not available, please try this later")
            return None

        self.historical_trades = res.json()

        return res.json()

    def get_historical_trades(self, symbol: str, limit: int = 500, fromId: int = 0):

        res = self.get_historical_trades_helper(symbol, limit, fromId)

        if res is not None:
            try:
                return pd.DataFrame(res).set_index('id').astype({'price': 'float64',
                                                                 'qty': 'float64',
                                                                 'quoteQty': 'float64'})
            except ValueError as e:
                log.error("The historical trade list for symbol {} is not available".format(symbol))
                return None

        return None

    def get_candles_helper(self, symbol: str = BTCUSDT, interval: str = Interval.ONE_MINUTE,
                           startTime: str = "2020-01-01 08:00:00",
                           endTime: str = "2020-01-02 08:00:00", limit: int = 100):

        res = requests.get("https://api.binance.us/api/v3/klines", params={"symbol": symbol,
                                                                           "interval": interval,
                                                                           "limit": limit,
                                                                           "startTime": TimeManager.str_to_milliseconds(
                                                                               startTime),
                                                                           "endTime": TimeManager.str_to_milliseconds(
                                                                               endTime)
                                                                           })
        if res.status_code == 404:
            log.error("The candles are not available now, please try later")
            return None

        self.candles = res.json()
        return self.candles

    def get_candles(self, symbol: str = BTCUSDT, interval: str = Interval.FIVE_MINUTE,
                    startTime: str = "2020-01-01 08:00:00",
                    endTime: str = "2020-01-02 08:00:00", limit: int = 100):

        res = self.get_candles_helper(symbol, interval, startTime, endTime, limit)

        if len(res) == 0:
            log.error("The candles are empty for the symbol{} ".format(symbol))
            return None

        if res is not None:
            try:
                return pd.DataFrame(res).set_axis(
                    ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'volume_dollar',
                     'transactions',
                     'buy_volume', 'buy_volume_dollar', 'ignore'], axis=1, inplace=False)
            except ValueError as e:
                log.error("The candle for symbol {} is not available".format(symbol))
                return None

        return None
