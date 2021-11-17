from strategyManager import strategy
from events import tickEvent, signalEvent
from optionPrimitives import optionPrimitive, putVertical
from base import option
from riskManagement import riskManagement
from typing import Optional, Text, Tuple
import collections
import datetime
import decimal
import logging
import queue

# Class to compute moving average with a queue. Taken from https://zhenyu0519.github.io/2020/07/08/lc346/.
class MovingAverage:

  def __init__(self, size: int):
    self.queue = collections.deque()
    self.size = size

  def add(self, value: int):
    """Add value to the queue or replace current value."""
    if len(self.queue) == self.size:
      self.queue.popleft()
      self.queue.append(value)
    else:
      self.queue.append(value)

class PutVerticalOnDownMoveStrat(strategy.Strategy):
  """This class sets up the strategy which sells put verticals when there is a % down move in the underlying.
  This strategy currently assumes that we are using EOD data for the backtesting.

  Specific strategy attributes:
    percentageDownToTrigger: Percentage the underlying should move down in order to trigger the selling of the vertical.
                             Expressed as a decimal.
    numberDaysForMovingAverage: We could use only the previous day or the average down percentage over several days in
                                deciding when to trigger the selling of the vertical.
    optPutToBuyDelta:   Optimal delta for the put to buy.
    maxPutToBuyDelta:   Maximum delta for the put to buy.
    minPutToBuyDelta:   Minimum delta for the put to buy
    optPutToSellDelta:  Optimal delta for the put to sell.
    maxPutToSellDelta:  Maximum delta for the put to sell.
    minPutToSellDelta:  Minimum delta for the put to sell.

  General strategy attributes:
    startDateTime:  Date/time to start the backtest.
    underlyingTicker:  Which underlying to use for the strategy.
    orderQuantity:  Number of verticals to sell.
    riskManagement: Risk management strategy (how to manage the trade; e.g., close, roll, hold to expiration).

  Optional attributes:
    expCycle:  Specifies if we want to do monthly, weekly, quarterly, etc.
    optimalDTE:  Optimal number of days before expiration to put on strategy.
    minimumDTE:  Minimum number of days before expiration to put on strategy.
    minimumROC:  Minimal return on capital for overall trade as a decimal.
    minCredit:  Minimum credit to collect on overall trade.
    maxBidAsk:  Maximum price to allow between bid and ask prices of option (for any strike or put/call).
    maxCapitalToUsePerTrade: percent (as a decimal) of portfolio value we want to use per trade.
"""

  def __init__(self, eventQueue:queue.Queue, percentDownToTrigger: float, numberDaysForMovingAverage: int,
               optPutToBuyDelta: float, maxPutToBuyDelta: float, minPutToBuyDelta: float, optPutToSellDelta: float,
               maxPutToSellDelta: float, minPutToSellDelta: float, underlyingTicker: Text, orderQuantity: int,
               riskManagement: riskManagement.RiskManagement, expCycle: Optional[strategy.ExpirationTypes]=None,
               optimalDTE: Optional[int]=None, minimumDTE: Optional[int]=None, minimumROC: Optional[float]=None,
               minCredit: Optional[decimal.Decimal]=None, maxBidAsk: Optional[decimal.Decimal]=None,
               maxCapitalToUsePerTrade: Optional[decimal.Decimal]=None,
               startDateTime: Optional[datetime.datetime]=None):

    self.__eventQueue = eventQueue
    self.__percentDownToTrigger = percentDownToTrigger
    self.__numberDaysForMovingAverage = numberDaysForMovingAverage
    self.__optPutToBuyDelta = optPutToBuyDelta
    self.__maxPutToBuyDelta = maxPutToBuyDelta
    self.__minPutToBuyDelta = minPutToBuyDelta
    self.__optPutToSellDelta = optPutToSellDelta
    self.__maxPutToSellDelta = maxPutToSellDelta
    self.__minPutToSellDelta = minPutToSellDelta

    self.startDateTime=startDateTime
    self.buyOrSell=optionPrimitive.TransactionType.SELL
    self.underlyingTicker=underlyingTicker
    self.orderQuantity=orderQuantity
    self.riskManagement = riskManagement
    self.expCycle=expCycle
    self.optimalDTE=optimalDTE
    self.minimumDTE=minimumDTE
    self.minimumROC=minimumROC
    self.minCredit=minCredit
    self.maxBidAsk=maxBidAsk
    self.maxCapitalToUsePerTrade=maxCapitalToUsePerTrade

    # Set up moving average queue.
    self.__movingAverageFilter = MovingAverage(self.__numberDaysForMovingAverage)

  def __updateWithOptimalOption(self, currentOption: option.Option,
                                optimalOption: option.Option, maxPutDelta: float, optPutDelta: float,
                                minPutDelta: float) -> Tuple[bool, option.Option]:
    """Find the option that is closest to the requested parameters (delta, expiration).

    :param currentOption: current option from the option chain.
    :param optimalOption: current optimal option based on expiration and delta.
    :param maxPutDelta: maximum delta of the put option.
    :param optPutDelta: optimal delta of the put option.
    :param minPutDelta: minimum delta of the put option.
    :return: tuple of (updateOption: bool, optimalOpt: option.Option). updateOption bool is used to indicate if we
             should update the optimal option with the current option.
    """
    # noUpdateRule means we don't update the optimal option with the current option.
    noUpdateRule = (False, optimalOption)
    # TODO: Add support for expiration cycles other than monthly.
    if self.expCycle == strategy.ExpirationTypes.MONTHLY:
      if not self.isMonthlyExp(currentOption.expirationDateTime):
        return noUpdateRule
    else:
      return noUpdateRule

    if self.minimumDTE:
      if not self.hasMinimumDTE(currentOption.dateTime, currentOption.expirationDateTime):
        return noUpdateRule

    # Check that delta is between the minimum and maximum delta.
    if currentOption.delta < maxPutDelta or currentOption.delta > minPutDelta:
      return noUpdateRule

    # Check if bid / ask of option < maxBidAsk specific in strangle strategy.
    if self.maxBidAsk:
      if self.calcBidAskDiff(currentOption.bidPrice, currentOption.askPrice) > self.maxBidAsk:
        return noUpdateRule

    # Get current DTE in days.
    currentDTE = self.getNumDays(currentOption.dateTime, currentOption.expirationDateTime)
    optimalDTE = self.getNumDays(optimalOption.dateTime, optimalOption.expirationDateTime) if optimalOption else None
    requestedDTE = self.optimalDTE

    # Check if there is no current optimal DTE or an expiration closer to the requested expiration.
    newOptimalOption = optimalOption
    if optimalDTE is None or (abs(currentDTE - requestedDTE) < abs(optimalDTE - requestedDTE)):
      newOptimalOption = currentOption
    # Option has same DTE as optimalOpt; check deltas to choose best option.
    elif currentDTE == optimalDTE:
      currentDelta = currentOption.delta
      optimalDelta = optimalOption.delta
      if abs(currentDelta - optPutDelta) < abs(optimalDelta - optPutDelta):
        newOptimalOption = currentOption
    else:
      return (False, newOptimalOption)

    return (True, newOptimalOption)

  def checkForSignal(self, event: tickEvent, portfolioNetLiquidity: decimal.Decimal,
                     availableBuyingPower: decimal.Decimal) -> None:
    """Criteria that we need to check before generating a signal event.
    We go through each option in the option chain and find all of the options that meet the criteria.  If there are
    multiple options that meet the criteria, we choose the first one, but we could use some other type of rule.

    Attributes:
      event: Tick data we parse through to determine if we want to create a putVertical for the strategy.
      portfolioNetLiquidity: Net liquidity of portfolio.
      availableBuyingPower: Amount of buying power available to use.
    """
    # These variables will be used to keep track of the optimal options as we go through the option chain.
    optimalPutOptionToSell = None
    optimalPutOptionToBuy = None

    # Get the data from the tick event.
    eventData = event.getData()

    if not eventData:
      return

    if self.startDateTime is not None:
      if eventData[0].dateTime < self.startDateTime:
        return

    if self.__numberDaysForMovingAverage > 0:
      # Check if we have enough data in the queue to perform the strategy.
      if not len(self.__movingAverageFilter.queue) == self.__numberDaysForMovingAverage:
        self.__movingAverageFilter.add(eventData[0].underlyingPrice)
        return

      # Check if the current price has moved down by self.__percentDownToTrigger of the movingAverage price.
      averagePrice = sum(self.__movingAverageFilter.queue) / len(self.__movingAverageFilter.queue)
      currentPrice = eventData[0].underlyingPrice
      self.__movingAverageFilter.add(eventData[0].underlyingPrice)
      if ((currentPrice - averagePrice) / averagePrice) > self.__percentDownToTrigger:
        return

    # Process one option at a time from the option chain (objects of option class).
    for currentOption in eventData:
      if currentOption.optionType == option.OptionTypes.PUT:
        # Handle put to buy first.
        updateOption, putOptToBuy = self.__updateWithOptimalOption(currentOption, optimalPutOptionToBuy,
                                                                   self.__maxPutToBuyDelta, self.__optPutToBuyDelta,
                                                                   self.__minPutToBuyDelta)
        if updateOption:
          optimalPutOptionToBuy = putOptToBuy

        # Handle put to sell.
        updateOption, putOptToSell = self.__updateWithOptimalOption(currentOption, optimalPutOptionToSell,
                                                                    self.__maxPutToSellDelta, self.__optPutToSellDelta,
                                                                    self.__minPutToSellDelta)
        if updateOption:
          optimalPutOptionToSell = putOptToSell

    # Must check that both PUTs were found which are in the same expiration but do not have the same strike price.
    if (optimalPutOptionToBuy and optimalPutOptionToSell) and (
      optimalPutOptionToBuy.expirationDateTime == optimalPutOptionToSell.expirationDateTime) and not(
      optimalPutOptionToBuy.strikePrice == optimalPutOptionToSell.strikePrice):
      putVerticalObj = putVertical.PutVertical(self.orderQuantity, optimalPutOptionToBuy, optimalPutOptionToSell,
                                               self.buyOrSell)

      # There is a case in the input data where the delta values are incorrect, and this results the strike price
      # of the long put being greater than the strike price of the short put, and this results in negative buying
      # power. To handle this error case, we return if the buying power is zero or negative.
      buyingPowerUsed = putVerticalObj.getBuyingPower()
      if buyingPowerUsed <= 0:
        return

      # There is an error case in the input data where the options may will have zero credit / debit when put on.
      if optimalPutOptionToBuy.tradePrice <= 0 or optimalPutOptionToSell.tradePrice <= 0:
        logging.warning('Optimal put or optimal call had a zero tradePrice, which should not happen.')
        return

      if self.maxCapitalToUsePerTrade:
        portfolioToUsePerTrade = decimal.Decimal(self.maxCapitalToUsePerTrade)*portfolioNetLiquidity
        maxBuyingPowerPerTrade = min(availableBuyingPower, portfolioToUsePerTrade)
      else:
        maxBuyingPowerPerTrade = availableBuyingPower

      numContractsToAdd = int(maxBuyingPowerPerTrade / buyingPowerUsed)
      if numContractsToAdd < 1:
        return

      putVerticalObj.setNumContracts(numContractsToAdd)

      # Create signal event to put on put vertical strategy and add to queue.
      signalObj = [putVerticalObj, self.riskManagement]
      event = signalEvent.SignalEvent()
      event.createEvent(signalObj)
      self.__eventQueue.put(event)
    else:
      logging.info('Could not execute strategy for this option chain.')
