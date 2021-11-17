import dataclasses
import datetime
import decimal
import enum
from events import tickEvent
from optionPrimitives import optionPrimitive
from typing import Optional, Text

class ExpirationTypes(enum.Enum):
  MONTHLY = 0
  WEEKLY = 1
  QUARTERLY = 2

@dataclasses.dataclass
class Strategy:
  """This class sets up the basics for every strategy that will be used; For example, if we want to do an iron condor
  or a strangle, there are certain parameters that must be defined.

  Attributes:
    startDateTime:  Date/time to start the backtest.
    buyOrSell:  Do we buy or sell the strategy? E.g. sell a strangle.
    underlyingTicker:  Which underlying to use for the strategy.
    orderQuantity:  Number of the strategy, e.g. number of strangles.
    expCycle:  Specifies if we want to do monthly, weekly, quarterly, etc.
    optimalDTE:  Optimal number of days before expiration to put on strategy.
    minimumDTE:  Minimum number of days before expiration to put on strategy.
    minimumROC:  Minimum return on capital for overall trade as a decimal.
    minCredit:  Minimum credit to collect on overall trade.
    maxBidAsk:  Maximum price to allow between bid and ask prices of option (for any strike or put/call).
    maxCapitalToUsePerTrade: percent (as a decimal) of portfolio value we want to use per trade.
  """

  startDateTime: datetime.datetime
  buyOrSell: optionPrimitive.TransactionType
  underlyingTicker: Text
  orderQuantity: int
  expCycle: Optional[ExpirationTypes] = None
  optimalDTE: Optional[int] = None
  minimumDTE: Optional[int] = None
  minimumROC: Optional[float] = None
  minCredit: Optional[decimal.Decimal] = None
  maxBidAsk: Optional[decimal.Decimal] = None
  maxCapitalToUsePerTrade: Optional[decimal.Decimal] = None

  def __post_init__(self):
    if self.__class__ == Strategy:
      raise TypeError('Cannot instantiate class.')

  def calcBidAskDiff(self, bidPrice: decimal.Decimal, askPrice: decimal.Decimal):
    """ Calculate the absolute difference between the bid and ask price.
    If any of the arguments are <= 0, return a very large difference (100).
    :param bidPrice: price at which the option can be sold.
    :param askPrice: price at which the option can be bought.
    :return: Absolute difference;
    """
    return abs(bidPrice - askPrice)

  def isMonthlyExp(self, dateTime: datetime.datetime):
    """
    Check if the option expiration falls on the third Friday of the month, or if the third Friday is a holiday,
    check if the expiration falls on the Thursday that precedes it.
    :param dateTime: option expiration date in mm/dd/yy format.
    :return: True if it's a monthly option; False otherwise.
    """
    return (dateTime.weekday() == 4 and 14 < dateTime.day < 22)

  def hasMinimumDTE(self, curDateTime: datetime.datetime, expDateTime: datetime.datetime):
    """"
    Determine if the current expiration date of the option is >= self.minimumDTE days from the current date.
    :param curDateTime: current date in mm/dd/yy format.
    :param expDateTime: option expiration date in mm/dd/yy format.
    :return: True if difference between current date and dateTime is >= self.minimumDTE; else False.
    """
    return (expDateTime - curDateTime).days >= self.minimumDTE

  def getNumDays(self, curDateTime: datetime.datetime, expDateTime: datetime.datetime):
    """"
    Determine the number of days between the curDateTime and the expDateTime.
    :param curDateTime: current date in mm/dd/yy format.
    :param expDateTime: option expiration date in mm/dd/yy format.
    :return: Number of days between curDateTime and expDateTime.
    """
    return (expDateTime - curDateTime).days