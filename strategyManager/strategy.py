import abc
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
class Strategy(abc.ABC):
  """This class sets up the basics for every strategy that will be used; For example, if we want to do an iron condor
  or a strangle, there are certain parameters that must be defined.

  Attributes:
    startDateTime:  Date/time to start the backtest.
    # TODO(add risk management lookup code here so we know how to manage this strategy. The code we create here will
    need to go in the portfolio as well.
    buyOrSell:  Do we buy or sell the strategy? E.g. sell a strangle.
    underlyingTicker:  Which underlying to use for the strategy.
    orderQuantity:  Number of the strategy, e.g. number of strangles.
    expCycle:  Specifies if we want to do monthly, weekly, quarterly, etc.
    optimalDTE:  Optimal number of days before expiration to put on strategy.
    minimumDTE:  Minimum number of days before expiration to put on strategy.
    minimumROC:  Minimum return on capital for overall trade as a decimal.
    minCredit:  Minimum credit to collect on overall trade.
    maxBidAsk:  Maximum price to allow between bid and ask prices of option (for any strike or put/call).
    minBuyingPower:  Minimum investment we want for the strategy -- since prices vary greatly over a range like
                     1990 to 2017, we would like to have the same amount of money in the market at any given
                     time, so we increase the number of contracts to reach this minBuyingPower.
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
  minBuyingPower: Optional[decimal.Decimal] = None

  def __post_init__(self):
    if self.__class__ == Strategy:
      raise TypeError('Cannot instantiate abstract class.')

  @abc.abstractmethod
  def checkForSignal(self, event: tickEvent) -> None:
    pass
