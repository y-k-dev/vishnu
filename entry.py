from lib import bitflyer, indicator, message, repository
from lib.config import MA, Bitflyer, TimeFrame


def get_historical_price(periods: int, tail: int, clean_db=False):
    data = bitflyer.get_historical_price(periods, tail, clean_db)

    data["Price"] = (data["Open"] +
                     data["High"] +
                     data["Low"] +
                     data["Close"]) / 4

    data = data.drop(columns="Open")
    data = data.drop(columns="High")
    data = data.drop(columns="Low")
    data = data.drop(columns="Close")
    return data


def get_ma_data(periods: int, ma: int, column_name: str, clean_db=False):
    data = get_historical_price(periods, ma * 2, clean_db)
    if len(data) < 2:
        return None

    data = indicator.add_ema(df=data, value=ma, column_name=column_name)
    data = data.drop(columns="Price")
    return data.iloc[len(data) - 2]


def save_entry(side):
    message.info(side, "entry")
    sql = "update entry set side='{side}'".format(side=side)
    repository.execute(database=DATABASE, sql=sql, write=False)


LONG_MA = MA.LONG.value
LONG_TIME_FRAME = TimeFrame.LONG.value

SHORT_MA = MA.SHORT.value
SHORT_TIME_FRAME = TimeFrame.SHORT.value

DATABASE = "tradingbot"

bitflyer = bitflyer.API(api_key=Bitflyer.Api.value.KEY.value,
                        api_secret=Bitflyer.Api.value.SECRET.value)


before_Date = None
has_buy = False
has_sell = False
while True:
    long_ma_data = get_ma_data(LONG_TIME_FRAME, LONG_MA, "long_ma", True)
    Date = long_ma_data["Date"]

    if before_Date == Date:
        continue

    short_ma_data = get_ma_data(SHORT_TIME_FRAME, SHORT_MA, "short_ma")

    short_ma = short_ma_data["short_ma"]
    long_ma = long_ma_data["long_ma"]

    should_buy = short_ma < long_ma and not has_buy
    should_sell = short_ma > long_ma and not has_sell

    if should_buy:
        save_entry(side="BUY")
        has_buy = True
        has_sell = False

    if should_sell:
        save_entry(side="SELL")
        has_buy = False
        has_sell = True

    before_Date = Date
