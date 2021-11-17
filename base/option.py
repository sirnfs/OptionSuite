import abc
import dataclasses
import datetime
import decimal
import enum
from typing import Optional, Text

class OptionTypes(enum.Enum):
  PUT = 0
  CALL = 1

@dataclasses.dataclass
class Option(abc.ABC):
  """This class defines the basic type for the backtester or live trader -- an option.
    Other classes such as put or call are derived from this class.

    Attributes:
      underlyingTicker:  ticker symbol (e.g., SPY) of underlying.
      strikePrice:  strike price of option.
      expirationDateTime:  date/time at which option expires.
      underlyingPrice:  price of the underlying / stock which has option derivatives in dollars.
      optionSymbol:  code different than the underlying ticker used to denote option.
      bidPrice:  current bid price of option.
      askPrice:  current asking price of option.
      tradePrice:  price of option when trade was executed / put on.
      openInterest:  number of open option contracts.
      volume:  number of contracts traded.
      dateTime:  date / time of last updated option chain.
      tradeDateTime: data/time that option was added.
      delta:  greek for quantifying percent of stock we're long or short (-1 to 1).
      theta:  daily return in dollars if no movement in underlying price.
      gamma:  describes rate of change of delta (float).
      rho:  how much option price changes with change in interest rate (dollars).
      vega:  change in price of option for every 1% change in volatility.
      impliedVol:  implied volatility percentage.
      exchangeCode:  symbol used to denote which exchanged used or where quote came from.
      exercisePrice:  price to exercise option early.
      assignPrice:  price you must pay if other party exercises option.
      openCost:  cost to open the option trade.
      closeCost:  cost to close out the option trade.
     """
  underlyingTicker: Text
  strikePrice: decimal.Decimal
  expirationDateTime: datetime.datetime
  underlyingPrice: Optional[decimal.Decimal] = None
  optionSymbol: Optional[Text] = None
  bidPrice: Optional[decimal.Decimal] = None
  askPrice: Optional[decimal.Decimal] = None
  tradePrice: decimal.Decimal = None
  openInterest: Optional[int] = None
  volume: Optional[int] = None
  dateTime: Optional[datetime.datetime] = None
  tradeDateTime: Optional[datetime.datetime] = None
  delta: Optional[float] = None
  theta: Optional[float] = None
  gamma: Optional[float] = None
  rho: Optional[float] = None
  vega: Optional[float] = None
  impliedVol: Optional[float] = None
  exchangeCode: Optional[Text] = None
  exercisePrice: Optional[decimal.Decimal] = None
  assignPrice: Optional[decimal.Decimal] = None
  openCost: Optional[decimal.Decimal] = None
  closeCost: Optional[decimal.Decimal] = None

  def __post_init__(self):
    if self.__class__ == Option:
      raise TypeError('Cannot instantiate abstract class.')

  def calcOptionPriceDiff(self) -> decimal.Decimal:
    """Calculate the difference in price of the put/call when the trade was placed versus its current value.
      Specifically, diff = original price - current price.  The current price used is actually the mid price, or
      the average of the bid price and ask price.
      :return: price difference (original price - current price).
    """
    midPrice = (self.bidPrice + self.askPrice) / decimal.Decimal(2.0)
    return (self.tradePrice - midPrice) * 100

  def getNumDaysLeft(self) -> int:
    """Determine the number of days between the current date/time and expiration date / time.
      :return: number of days between curDateTime and expDateTime.
    """
    return (self.expirationDateTime - self.dateTime).days

  def getMidPrice(self) -> decimal.Decimal:
    """Calculate the mid price for the option."""
    return (self.bidPrice + self.askPrice) / decimal.Decimal(2.0)

  def updateOption(self, updatedOption: 'Option') -> None:
    """Update the relevant values of the original option with those of the new option; e.g., update price, delta.
      :param updatedOption: new option from the latest tick.
      :raises ValueError: option cannot be updated.
    """
    # Check that we are dealing with the same option.
    if self.underlyingTicker == updatedOption.underlyingTicker and self.strikePrice == updatedOption.strikePrice and (
      self.expirationDateTime == updatedOption.expirationDateTime):
      self.underlyingPrice = updatedOption.underlyingPrice
      self.bidPrice = updatedOption.bidPrice
      self.askPrice = updatedOption.askPrice
      self.openInterest = updatedOption.openInterest
      self.volume = updatedOption.volume
      self.dateTime = updatedOption.dateTime
      self.delta = updatedOption.delta
      self.theta = updatedOption.theta
      self.gamma = updatedOption.gamma
      self.rho = updatedOption.rho
      self.vega = updatedOption.vega
      self.impliedVol = updatedOption.impliedVol
    else:
      raise ValueError('Cannot update option; this option appears to be from a different option chain.')
