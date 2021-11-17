from strategyManager import strategy
from events import tickEvent, signalEvent
from optionPrimitives import optionPrimitive, strangle
from base import option
from riskManagement import riskManagement
from typing import Optional, Text, Tuple
import datetime
import decimal
import logging
import queue

class StrangleStrat(strategy.Strategy):
  """This class sets up strangle strategy, which involves buying or selling strangles.

  Strangle specific attributes:
    optCallDelta:  Optimal delta for call.
    maxCallDelta:  Max delta for call.
    optPutDelta:  Optimal delta for put.
    maxPutDelta:  Max delta for put.

  General strategy attributes:
    startDateTime:  Date/time to start the backtest.
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
    maxCapitalToUsePerTrade: percent (as a decimal) of portfolio value we want to use per trade.
"""

  def __init__(self, eventQueue:queue.Queue, optCallDelta: float, maxCallDelta: float, optPutDelta: float,
               maxPutDelta: float, buyOrSell: optionPrimitive.TransactionType,
               underlyingTicker: Text, orderQuantity: int, riskManagement: riskManagement.RiskManagement,
               expCycle: Optional[strategy.ExpirationTypes]=None, optimalDTE: Optional[int]=None,
               minimumDTE: Optional[int]=None, minimumROC: Optional[float]=None,
               minCredit: Optional[decimal.Decimal]=None, maxBidAsk: Optional[decimal.Decimal]=None,
               maxCapitalToUsePerTrade: Optional[decimal.Decimal]=None,
               startDateTime: Optional[datetime.datetime]=None):

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
    self.maxCapitalToUsePerTrade=maxCapitalToUsePerTrade

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
      if not self.isMonthlyExp(currentOption.expirationDateTime):
        return noUpdateRule
    else:
      return noUpdateRule

    if self.minimumDTE:
      if not self.hasMinimumDTE(currentOption.dateTime, currentOption.expirationDateTime):
        return noUpdateRule

    # Check that delta is less or equal to max delta specified.
    if currentOption.optionType == option.OptionTypes.CALL:
      if currentOption.delta > self.__maxCallDelta:
        return noUpdateRule
    else:
      # PUT option.
      if currentOption.delta < self.__maxPutDelta:
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
      if currentOption.optionType == option.OptionTypes.CALL:
        requestedDelta = self.__optCallDelta
      else:
        requestedDelta = self.__optPutDelta

      if abs(currentDelta - requestedDelta) < abs(optimalDelta - requestedDelta):
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
      event - Tick data we parse through to determine if we want to create a strangle for the strategy.
      portfolioNetLiquidity: Net liquidity of portfolio.
      availableBuyingPower: Amount of buying power available to use.
    """
    # These variables will be used to keep track of the optimal options as we go through the option chain.
    optimalCallOpt = None
    optimalPutOpt = None

    # Get the data from the tick event.
    eventData = event.getData()

    if not eventData:
      return

    if self.startDateTime is not None:
      if eventData[0].dateTime < self.startDateTime:
        return

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

      # There is a case in the input data where the delta values are incorrect, and this results the strike price
      # of the short put being greater than the strike price of the short call, and this results in negative buying
      # power. To handle this error case, we return if the buying power is zero or negative.
      buyingPowerUsed = strangleObj.getBuyingPower()
      if buyingPowerUsed <= 0:
        return

      # There is an error case in the input data where the options may will have zero credit / debit when put on.
      if optimalPutOpt.tradePrice <= 0 or optimalCallOpt.tradePrice <= 0:
        logging.warning('Optimal put or optimal call had a zero tradePrice, which should not happen.')
        return

      if self.maxCapitalToUsePerTrade:
        portfolioToUsePerTrade = decimal.Decimal(self.maxCapitalToUsePerTrade) * portfolioNetLiquidity
        maxBuyingPowerPerTrade = min(availableBuyingPower, portfolioToUsePerTrade)
      else:
        maxBuyingPowerPerTrade = availableBuyingPower

      numContractsToAdd = int(maxBuyingPowerPerTrade / buyingPowerUsed)
      if numContractsToAdd < 1:
        return

      strangleObj.setNumContracts(numContractsToAdd)

      # Create signal event to put on strangle strategy and add to queue.
      signalObj = [strangleObj, self.riskManagement]
      event = signalEvent.SignalEvent()
      event.createEvent(signalObj)
      self.__eventQueue.put(event)
    else:
      logging.info('Could not execute strategy for this option chain.')