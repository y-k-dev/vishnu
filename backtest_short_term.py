import statistics

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from lib import bitflyer, indicator, math
from lib import pandas_option as pd_op
from lib import repository
from lib.config import MA, Bitflyer, TimeFrame


def get_historical_price(periods: int):
    data = bitflyer.get_historical_price(periods=periods)

    data = data.drop(columns="Volume")
    data = data.drop(columns="QuoteVolume")

    data["Price"] = (data["Open"] +
                     data["High"] +
                     data["Low"] +
                     data["Close"]) / 4

    data = data.drop(columns="Open")
    data = data.drop(columns="High")
    data = data.drop(columns="Low")
    return data


def get_ma_data(periods: int, ma: int, column_name: str):
    data = get_historical_price(periods=periods)
    data = indicator.add_ema(df=data, value=ma, column_name=column_name)
    data = data.drop(columns="Price")
    return data


def save_entry(date, side, price):
    sql = "insert into backtest_entry values ('{date}','{side}',{price},0)"\
        .format(date=date, side=side, price=price)
    repository.execute(database=DATABASE, sql=sql, log=False)


asset = 1000000

LONG_MA = MA.LONG.value
LONG_TIME_FRAME = TimeFrame.LONG.value

SHORT_MA = MA.SHORT.value
SHORT_TIME_FRAME = TimeFrame.SHORT.value

DATABASE = "tradingbot"

pd_op.display_max_columns()
pd_op.display_round_down()

bitflyer = bitflyer.API(api_key=Bitflyer.Api.value.KEY.value,
                        api_secret=Bitflyer.Api.value.SECRET.value)

sql = "truncate backtest_entry"
repository.execute(database=DATABASE, sql=sql, write=False)

long_ma_data = get_ma_data(LONG_TIME_FRAME, LONG_MA, "long_ma")
long_ma_data = long_ma_data.drop(columns="Close")

short_ma_data = get_ma_data(SHORT_TIME_FRAME, SHORT_MA, "short_ma")

bo = pd.merge(long_ma_data, short_ma_data, on="Time", how='inner')

bo = bo.dropna(how="any")
bo["side"] = np.where(bo["short_ma"] < bo["long_ma"],
                      "BUY", "SELL")

delete_indexs = []
for i in range(len(bo)):
    if i == 0:
        continue

    past_side = bo["side"].iloc[i - 1]
    now_side = bo["side"].iloc[i]

    if past_side == now_side:
        delete_indexs.append(i)

for i in range(len(delete_indexs)):
    bo = bo.drop(delete_indexs[i])

bo = bo.reset_index(drop=True)

bo["Date"] = pd.to_datetime(bo["Time"].astype(int), unit="s", utc=True)
bo["Date"] = bo["Date"].dt.tz_convert('Asia/Tokyo')

bo = bo.drop(columns="Time")
bo = bo.drop(columns="short_ma")
bo = bo.drop(columns="long_ma")

bo = bo.sort_values("Date")

profits = []
asset_flow = []
elapsed_secs = []
for i in range(len(bo)):
    if i == 0:
        continue

    past_position = bo.iloc[i - 1]
    now_position = bo.iloc[i]

    if past_position["side"] == "BUY" and (
            now_position["side"] == "SELL" or now_position["side"] == "CLOSE"):

        amount = asset / past_position["Close"]
        profit = (amount * now_position["Close"]) - asset

        elapsed_sec = (
            now_position["Date"] -
            past_position["Date"]).seconds

        elapsed_secs.append(elapsed_sec)
        profits.append(profit)
        asset += profit

    if past_position["side"] == "SELL" and (
            now_position["side"] == "BUY" or now_position["side"] == "CLOSE"):

        amount = asset / past_position["Close"]
        profit = asset - (amount * now_position["Close"])

        elapsed_sec = (
            now_position["Date"] -
            past_position["Date"]).seconds

        elapsed_secs.append(elapsed_sec)
        profits.append(profit)
        asset += profit


wins = []
loses = []
for i in range(len(profits)):
    if profits[i] > 0:
        wins.append(profits[i])
    elif profits[i] < 0:
        loses.append(profits[i])

pf = None
if sum(loses) != 0:
    pf = abs(sum(wins) / sum(loses))
wp = None
if len(wins) + len(loses) != 0:
    wp = len(wins) / (len(wins) + len(loses)) * 100

print("----------------------------------------------")
print("SHORT_MA", SHORT_MA, "SHORT_TIME_FRAME", SHORT_TIME_FRAME)
print("LONG_MA", LONG_MA, "LONG_TIME_FRAME", LONG_TIME_FRAME)

print("profit", int(sum(profits)))
if pf:
    print("pf", math.round_down(pf, -2))
if wp:
    print("wp", math.round_down(wp, 0), "%")
if elapsed_secs:
    print("max elapsed_sec", max(elapsed_secs))
    print("med elapsed_sec", statistics.median(elapsed_secs))
print("trading cnt", len(profits))

profit_flow = []
p = 0
for i in range(len(profits)):
    profit_flow.append(p)
    p += profits[i]

fig = plt.figure(figsize=(48, 24), dpi=50)
ax1 = fig.add_subplot(1, 1, 1)
ax1.plot(list(range(len(profit_flow))), profit_flow)
plt.show()
