import traceback

import pandas as pd

from lib import bitflyer, message, repository
from lib.config import Bitflyer, HistoricalPrice


def get_historical_price() -> pd.DataFrame or None:
    try:
        limit = CHANNEL_BAR_NUM + 1
        historical_price = bitflyer.get_historical_price(limit=limit)
        if len(historical_price) != limit:
            return None

        df = historical_price["Volume"]
        sma = df.rolling(VOLUME_MA).mean()[:VOLUME_MA]
        historical_price["ema"] = pd.concat([sma, df[VOLUME_MA:]]).ewm(
            span=VOLUME_MA, adjust=False).mean()

        return historical_price
    except Exception:
        message.error(traceback.format_exc())
        return None


def save_entry(side):
    message.info(side, "entry")
    sql = "update entry set side='{side}'".format(side=side)
    repository.execute(database=DATABASE, sql=sql, write=False)


TIME_FRAME = HistoricalPrice.TIME_FRAME.value
CHANNEL_WIDTH = HistoricalPrice.CHANNEL_WIDTH.value
CHANNEL_BAR_NUM = TIME_FRAME * CHANNEL_WIDTH

VOLUME_MA = HistoricalPrice.VOLUME_MA.value
DIFF_RATIO = HistoricalPrice.DIFF_RATIO.value
BACK_MIN = HistoricalPrice.BACK_MIN.value

bitflyer = bitflyer.API(api_key=Bitflyer.Api.value.KEY.value,
                        api_secret=Bitflyer.Api.value.SECRET.value)

DATABASE = "tradingbot"

has_buy = False
has_sell = False
while True:
    hp = get_historical_price()
    if hp is None:
        continue

    i = len(hp) - 1
    v2_data = hp.iloc[i]

    i = len(hp) - 2
    v1_data = hp.iloc[i]

    has_signal = v2_data["ema"] / v1_data["ema"] > DIFF_RATIO

    if has_signal:
        i = len(hp) - (1 + BACK_MIN)
        fr_data = hp.iloc[i]
        to_data = v2_data

        if fr_data["Close"] > to_data["Close"] and not has_buy:
            save_entry(side="BUY")
            has_buy = True
            has_sell = False

        if fr_data["Close"] < to_data["Close"] and not has_sell:
            save_entry(side="SELL")
            has_buy = False
            has_sell = True
