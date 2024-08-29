import abc
import decimal
import enum
from base import option
from typing import Iterable


class TransactionType(enum.Enum):
    BUY = 0
    SELL = 1


class TradeDirection(enum.Enum):
    LONG = 0
    SHORT = 1


class OptionPrimitive(abc.ABC):
    """This class is a generic type for any primitive that can be made using a PUT or CALL option and/or stock,
      e.g., iron condor or strangle.
    """

    @abc.abstractmethod
    def getBuyingPower(self) -> decimal.Decimal:
        """Used to calculate the buying power needed for the option primitive."""
        pass

    @abc.abstractmethod
    def getDelta(self) -> float:
        """Used to get the total delta for the option primitive."""
        pass

    @abc.abstractmethod
    def getVega(self) -> float:
        """Used to get the total vega for the option primitive."""
        pass

    @abc.abstractmethod
    def getTheta(self) -> float:
        """Used to get the total theta for the option primitive."""
        pass

    @abc.abstractmethod
    def getGamma(self) -> float:
        """Used to get the total gamma for the option primitive."""
        pass

    @abc.abstractmethod
    def calcProfitLoss(self) -> decimal.Decimal:
        """Calculate the profit and loss for the option primitive based on option values when the trade was placed and
           new option values.

           :return: Profit / loss (positive decimal for profit, negative decimal for loss).
        """
        pass

    @abc.abstractmethod
    def calcProfitLossPercentage(self) -> float:
        """Calculate the profit and loss for the option primitive based on option values when the trade was placed and
           new option values.

           :return: Profit / loss as a percentage of the initial option prices. Returns negative percentage for a loss.
        """
        pass

    @abc.abstractmethod
    def updateValues(self, tickData: Iterable[option.Option]) -> bool:
        """Based on the latest pricing data, update the option values.

          :param tickData: option chain with pricing information.
          :return True if we were able to update values, false otherwise.
        """
        pass

    def calcBidAskDiff(self, bidPrice: decimal.Decimal, askPrice: decimal.Decimal) -> decimal.Decimal:
        """Calculate the absolute difference between the bid and ask price.

          :param bidPrice: price at which the option can be sold.
          :param askPrice: price at which the option can be bought.
          :return: Absolute difference;
        """
        return abs(bidPrice - askPrice)
