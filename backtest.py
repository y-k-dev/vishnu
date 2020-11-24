import numpy as np
import pandas as pd

from lib import pandas_option as pd_op
from lib import repository


def save_entry(date, side, price):
    sql = "insert into backtest_entry values('{date}','{side}',{price},0)" \
        .format(date=date, side=side, price=price)
    repository.execute(database=database, sql=sql, log=False)


volume_ma = 10
diff_ratio = 2
back_min = 5

print("----------------------------------------------")
print("volume_ma", volume_ma, "diff_ratio", diff_ratio, "back_min", back_min)

asset = 1000000

database = "tradingbot"

sql = "truncate backtest_entry"
repository.execute(database=database, sql=sql, log=False)

pd_op.display_max_columns()
pd_op.display_round_down()

sql = """
        select
            b2.Date as date,
            b3.Close as fr_Price,
            b2.Close as to_Price,
            b1.Volume as v1,
            b2.Volume as v2,
            b1.Date as bb1,
            b2.Date as bb2,
            b3.Date as bb3
        from
            bitflyer_btc_ohlc_1M b1
            inner join
                bitflyer_btc_ohlc_1M b2
                on (b1.Date + interval 1 minute) = b2.Date
            inner join
                bitflyer_btc_ohlc_1M b3
                on (b3.Date + interval {back_min} minute) = b2.Date
        order by
            Date
        """.format(back_min=back_min)
be = repository.read_sql(database=database, sql=sql)

df = be["v1"]
sma = df.rolling(volume_ma).mean()[:volume_ma]
be["v1_ma"] = pd.concat([sma, df[volume_ma:]]).ewm(
    span=volume_ma, adjust=False).mean()

df = be["v2"]
sma = df.rolling(volume_ma).mean()[:volume_ma]
be["v2_ma"] = pd.concat([sma, df[volume_ma:]]).ewm(
    span=volume_ma, adjust=False).mean()

be["signal"] = np.where(be["v2_ma"] / be["v1_ma"] > diff_ratio,
                        "signal", None)

be = be.drop(columns="v1_ma")
be = be.drop(columns="v2_ma")
be = be.drop(columns="v1")
be = be.drop(columns="v2")
be = be.dropna(how="any")
be = be.drop(columns="signal")

be["side"] = np.where(be["fr_Price"] > be["to_Price"],
                      "BUY", "SELL")
be = be.drop(columns="fr_Price")

be = be.rename(columns={"to_Price": "price"})

be = be.reset_index(drop=True)

be = be.sort_values("date")

has_buy = False
has_sell = False
for i in range(len(be)):
    data = be.iloc[i]
    date = data["date"]
    side = data["side"]
    price = data["price"]

    entry_buy = side == "BUY" and not has_buy
    entry_sell = side == "SELL" and not has_sell

    if entry_buy:
        save_entry(date, side, price)
        has_buy = True
        has_sell = False

    if entry_sell:
        save_entry(date, side, price)
        has_buy = False
        has_sell = True
