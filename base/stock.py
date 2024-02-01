import dataclasses
import datetime
import decimal
from typing import Optional, Text

@dataclasses.dataclass
class Stock:
  """This class defines one the basic types for the backtester or live trader -- a stock.
    Attributes:
      underlyingPrice:  price of the underlying / stock which has option derivatives in dollars.
      underlyingTicker:  ticker symbol (e.g., SPY) of underlying.
      bidPrice:  current bid price of option.
      askPrice:  current asking price of option.
      tradePrice:  price of stock when order was executed.
      settlmentPrice: current settlement price of stock
      openInterest:  number of open option contracts.
      volume:  number of contracts traded.
      dateTime:  data / time of quote received; would also be data / time bought / sold.
      exchangeCode:  symbol used to denote which exchanged used or where quote came from.
      openCost:  cost to open the option trade.
      closeCost:  cost to close out the option trade.
     """
  underlyingPrice: decimal.Decimal
  underlyingTicker: Text
  bidPrice: Optional[decimal.Decimal] = None
  askPrice: Optional[decimal.Decimal] = None
  tradePrice: decimal.Decimal = None
  settlementPrice: decimal.Decimal = None
  openInterest: Optional[int] = 0
  volume: Optional[int] = 0
  dateTime: Optional[datetime.datetime] = None
  exchangeCode: Optional[Text] = None
  openCost: Optional[decimal.Decimal] = None
  closeCost: Optional[decimal.Decimal] = None