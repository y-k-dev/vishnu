import statistics

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from lib import indicator, math
from lib import pandas_option as pd_op
from lib import repository
from lib.config import MA


def get_short_ma_data():
    sql = """
            select
                s.Date,
                s.Close,
                (s.Open + s.High + s.Low + s.Close) / 4 as Price
            from
                bitflyer_btc_ohlc_1M s
            order by
                Date
            """
    data = repository.read_sql(database="tradingbot", sql=sql)

    data = indicator.add_ema(df=data, value=SHORT_MA, column_name="short_ma")
    data = data.drop(columns="Price")
    return data


def get_long_ma_data():
    sql = """
            select
                s.Date,
                (s.Open + s.High + s.Low + s.Close) / 4 as Price
            from
                bitflyer_btc_ohlc_15M s
            order by
                Date
            """
    data = repository.read_sql(database="tradingbot", sql=sql)

    data = indicator.add_ema(df=data, value=LONG_MA, column_name="long_ma")
    data = data.drop(columns="Price")
    return data


def save_entry(date, side, price):
    sql = "insert into backtest_entry values ('{date}','{side}',{price},0)"\
        .format(date=date, side=side, price=price)
    repository.execute(database=DATABASE, sql=sql, log=False)


LONG_MA = MA.LONG.value
SHORT_MA = MA.SHORT.value

asset = 1000000

DATABASE = "tradingbot"

pd_op.display_max_columns()
pd_op.display_round_down()

sql = "truncate backtest_entry"
repository.execute(database=DATABASE, sql=sql, write=False)

long_ma_data = get_long_ma_data()
short_ma_data = get_short_ma_data()

bo = pd.merge(long_ma_data, short_ma_data, on="Date", how='inner')

bo = bo.dropna(how="any")
bo["side"] = np.where(bo["short_ma"] < bo["long_ma"],
                      "BUY", "SELL")

bo = bo.drop(columns="short_ma")
bo = bo.drop(columns="long_ma")

bo = bo.sort_values("Date")

has_buy = False
has_sell = False
for i in range(len(bo)):
    data = bo.iloc[i]

    date = data["Date"]
    side = data["side"]
    price = data["Close"]

    if side == "BUY" and not has_buy:
        save_entry(date, side, price)
        has_buy = True
        has_sell = False

    if side == "SELL" and not has_sell:
        save_entry(date, side, price)
        has_buy = False
        has_sell = True

sql = """
        select
            *
        from
            backtest_entry
        order by
            date
        """

be = repository.read_sql(database="tradingbot", sql=sql)

start_time = be.loc[0]["date"]
finish_time = be.loc[len(be) - 1]["date"]

profits = []
asset_flow = []
elapsed_secs = []
for i in range(len(be)):
    if i == 0:
        continue

    past_position = be.iloc[i - 1]
    now_position = be.iloc[i]

    if past_position["side"] == "BUY" and (
            now_position["side"] == "SELL" or now_position["side"] == "CLOSE"):

        amount = asset / past_position["price"]
        profit = (amount * now_position["price"]) - asset

        elapsed_sec = (
            now_position["date"] -
            past_position["date"]).seconds

        print(now_position["date"])
        elapsed_secs.append(elapsed_sec)
        profits.append(profit)
        asset += profit

    if past_position["side"] == "SELL" and (
            now_position["side"] == "BUY" or now_position["side"] == "CLOSE"):

        amount = asset / past_position["price"]
        profit = asset - (amount * now_position["price"])

        elapsed_sec = (
            now_position["date"] -
            past_position["date"]).seconds

        print(now_position["date"])
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
print("SHORT_MA", SHORT_MA, "LONG_MA", LONG_MA)

print(str(start_time).split(".")[0],
      "〜", str(finish_time).split(".")[0])
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
