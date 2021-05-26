import pandas as pd

from Binance import Binance, Interval
from matplotlib import pyplot as plt

client = Binance()

client.set_api_key("Kww6z7iBthmfxqloZkf2BJeRX6IpNkWniy0hJWc7nAgrLSz7W7zEtd2WGbCVRZ76")

df = client.get_market_depth("DOGEUSD", 50, 1)
print(df)
print(client.get_recent_trades_helper("BTCUSDT", 500))
print(client.get_recent_trades("BTCUSDT", 500))
print(client.get_recent_trades("BTCUSDT", 500).dtypes)

print(client.get_historical_trades_helper("BTCUSDT", fromId=1000))
print(client.get_historical_trades("BTCUSDT", 500, fromId=1000))
print(client.get_historical_trades("BTCUSDT", 500, fromId=1000).dtypes)

# print(client.get_candles())
print(client.get_candles(symbol="BTCUSDT", limit=50))
print(client.get_candles(symbol="DOGEUSDT", interval=Interval.ONE_MINUTE, startTime="2021-05-25 08:00:00",
                         endTime="2021-05-25 10:00:00"))
