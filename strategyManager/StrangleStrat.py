from strategyManager import strategy
from events import tickEvent, signalEvent
from optionPrimitives import optionPrimitive, strangle
from base import option
from riskManagement import riskManagement
from typing import Optional, Text, Tuple
import datetime
import decimal
import queue

class StrangleStrat(strategy.Strategy):
  """This class sets up strangle strategy, which involves buying or selling strangles.

  Strangle specific attributes:
    optCallDelta:  Optimal delta for call.
    maxCallDelta:  Max delta for call.
    optPutDelta:  Optimal delta for put.
    maxPutDelta:  Max delta for put.

  General strategy attributes:
    startDateTime:  Date/time to start the live trading or backtest.
    buyOrSell:  Do we buy a strangle or sell a strangle.
    underlyingTicker:  Which underlying to use for the strategy.
    orderQuantity:  Number of strangles.
    riskManagement: Risk management strategy (how to manage the trade; e.g., close, roll, hold to expiration).

  Optional attributes:
    expCycle:  Specifies if we want to do monthly, weekly, quarterly, etc.
    optimalDTE:  Optimal number of days before expiration to put on strategy.
    minimumDTE:  Minimum number of days before expiration to put on strategy.
    minimumROC:  Minimal return on capital for overall trade as a decimal.
    minCredit:  Minimum credit to collect on overall trade.
    maxBidAsk:  Maximum price to allow between bid and ask prices of option (for any strike or put/call).
    minBuyingPower:  Minimum investment we want for the strategy -- since prices vary greatly over a range like
                     1990 to 2017, we would like to have the same amount of money in the market at any given
                     time, so we increase the number of contracts to reach this minBuyingPower.
"""

  def __init__(self, eventQueue:queue.Queue, optCallDelta: float, maxCallDelta: float, optPutDelta: float,
               maxPutDelta: float, startDateTime: datetime.datetime, buyOrSell: optionPrimitive.TransactionType,
               underlyingTicker: Text, orderQuantity: int, riskManagement: riskManagement.RiskManagement,
               expCycle: Optional[strategy.ExpirationTypes]=None, optimalDTE: Optional[int]=None,
               minimumDTE: Optional[int]=None, minimumROC: Optional[float]=None,
               minCredit: Optional[decimal.Decimal]=None, maxBidAsk: Optional[decimal.Decimal]=None,
               minBuyingPower: Optional[decimal.Decimal]=None):

    self.__eventQueue = eventQueue
    self.__optCallDelta = optCallDelta
    self.__maxCallDelta = maxCallDelta
    self.__optPutDelta = optPutDelta
    self.__maxPutDelta = maxPutDelta

    self.startDateTime=startDateTime
    self.buyOrSell=buyOrSell
    self.underlyingTicker=underlyingTicker
    self.orderQuantity=orderQuantity
    self.riskManagement = riskManagement
    self.expCycle=expCycle
    self.optimalDTE=optimalDTE
    self.minimumDTE=minimumDTE
    self.minimumROC=minimumROC
    self.minCredit=minCredit
    self.maxBidAsk=maxBidAsk
    self.minBuyingPower=minBuyingPower

  def __updateWithOptimalOption(self, currentOption: option.Option,
                                optimalOption: option.Option) -> Tuple[bool, option.Option]:
    """Find the option that is closest to the requested parameters (delta, expiration).

    :param currentOption: current option from the option chain.
    :param optimalOption: current optimal option based on expiration and delta.
    :return: tuple of (updateOption: bool, optimalOpt: option.Option). updateOption bool is used to indicate if we
             should update the optimal option with the current option.
    """
    # noUpdateRule means we don't update the optimal option with the current option.
    noUpdateRule = (False, optimalOption)
    # TODO: Add support for expiration cycles other than monthly.
    if self.expCycle == strategy.ExpirationTypes.MONTHLY:
      if not self.__isMonthlyExp(currentOption.expirationDateTime):
        return noUpdateRule
    else:
      return noUpdateRule

    if self.minimumDTE:
      if not self.__hasMinimumDTE(currentOption.dateTime, currentOption.expirationDateTime):
        return noUpdateRule

    # Check that delta is less or equal to max delta specified.
    if currentOption.optionType == option.OptionTypes.CALL:
      if currentOption.delta >= self.__maxCallDelta:
        return noUpdateRule
    else:
      # PUT option.
      if currentOption.delta <= self.__maxPutDelta:
        return noUpdateRule

    # Check if bid / ask of option < maxBidAsk specific in strangle strategy.
    if self.maxBidAsk:
      if self.__calcBidAskDiff(currentOption.bidPrice, currentOption.askPrice) > self.maxBidAsk:
        return noUpdateRule

    # Get current DTE in days.
    currentDTE = self.__getNumDays(currentOption.dateTime, currentOption.expirationDateTime)
    optimalDTE = self.__getNumDays(optimalOption.dateTime, optimalOption.expirationDateTime) if optimalOption else None
    requestedDTE = self.optimalDTE

    # Check if there is no current optimal DTE or an expiration closer to the requested expiration.
    newOptimalOption = optimalOption
    if optimalDTE is None or (abs(currentDTE - requestedDTE) < abs(optimalDTE - requestedDTE)):
      newOptimalOption = currentOption
    # Option has same DTE as optimalOpt; check deltas to choose best option.
    elif currentDTE == optimalDTE:
      currentDelta = currentOption.delta
      optimalDelta = optimalOption.delta
      if currentOption.optionType == option.OptionTypes.CALL:
        requestedDelta = self.__optCallDelta
      else:
        requestedDelta = self.__optPutDelta

      if abs(currentDelta - requestedDelta) < abs(optimalDelta - requestedDelta):
        newOptimalOption = currentOption
    else:
      return (False, newOptimalOption)

    return (True, newOptimalOption)

  def checkForSignal(self, event: tickEvent) -> None:
    """Criteria that we need to check before generating a signal event.
    We go through each option in the option chain and find all of the options that meet the criteria.  If there are
    multiple options that meet the criteria, we choose the first one, but we could use some other type of rule.

    Attributes:
      event - Tick data we parse through to determine if we want to create a strangle for the strategy.
    """
    # These variables will be used to keep track of the optimal options as we go through the option chain.
    optimalCallOpt = None
    optimalPutOpt = None

    # Get the data from the tick event.
    eventData = event.getData()

    # Process one option at a time from the option chain (objects of option class).
    for currentOption in eventData:
      if currentOption.optionType == option.OptionTypes.CALL:
        updateOption, callOpt = self.__updateWithOptimalOption(currentOption, optimalCallOpt)
        if updateOption:
          optimalCallOpt = callOpt
      else:
        # PUT option
        updateOption, putOpt = self.__updateWithOptimalOption(currentOption, optimalPutOpt)
        if updateOption:
          optimalPutOpt = putOpt

    # Must check that both a CALL and PUT were found which meet criteria and are in the same expiration.
    if optimalPutOpt and optimalCallOpt and optimalPutOpt.expirationDateTime == optimalCallOpt.expirationDateTime:
      strangleObj = strangle.Strangle(self.orderQuantity, optimalCallOpt, optimalPutOpt, self.buyOrSell)

      # If we are requiring that we always have the same amount of money invested regardless of time frame,
      # then we may need to increase the number of strangles to meet this minBuyingPower requirement.
      minBuyingPower = self.minBuyingPower
      if minBuyingPower:
          buyingPowerUsed = strangleObj.getBuyingPower()
          # Require at least one contract; too much buying power will be rejected in the portfolio class.
          numContractsToAdd = max(1, int(minBuyingPower / buyingPowerUsed))
          strangleObj.setNumContracts(numContractsToAdd)

      # Create signal event to put on strangle strategy and add to queue
      # TODO: We need to pass the management strategy to createEvent below.
      signalObj = [strangleObj, self.riskManagement]
      event = signalEvent.SignalEvent()
      event.createEvent(signalObj)
      #event.createEvent(strangleObj)
      self.__eventQueue.put(event)

  def __calcBidAskDiff(self, bidPrice: decimal.Decimal, askPrice: decimal.Decimal):
    """ Calculate the absolute difference between the bid and ask price.
    If any of the arguments are <= 0, return a very large difference (100).
    :param bidPrice: price at which the option can be sold.
    :param askPrice: price at which the option can be bought.
    :return: Absolute difference;
    """
    return abs(bidPrice - askPrice)

  def __isMonthlyExp(self, dateTime: datetime.datetime):
    """
    Check if the option expiration falls on the third Friday of the month, or if the third Friday is a holiday,
    check if the expiration falls on the Thursday that precedes it.
    :param dateTime: option expiration date in mm/dd/yy format.
    :return: True if it's a monthly option; False otherwise.
    """
    return (dateTime.weekday() == 4 and 14 < dateTime.day < 22)

  def __hasMinimumDTE(self, curDateTime: datetime.datetime, expDateTime: datetime.datetime):
    """"
    Determine if the current expiration date of the option is >= self.minimumDTE days from the current date.
    :param curDateTime: current date in mm/dd/yy format.
    :param expDateTime: option expiration date in mm/dd/yy format.
    :return: True if difference between current date and dateTime is >= self.minimumDTE; else False.
    """
    return (expDateTime - curDateTime).days >= self.minimumDTE

  def __getNumDays(self, curDateTime: datetime.datetime, expDateTime: datetime.datetime):
    """"
    Determine the number of days between the curDateTime and the expDateTime.
    :param curDateTime: current date in mm/dd/yy format.
    :param expDateTime: option expiration date in mm/dd/yy format.
    :return: Number of days between curDateTime and expDateTime.
    """
    return (expDateTime - curDateTime).days