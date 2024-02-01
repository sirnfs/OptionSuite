from strategyManager import strategy
from events import tickEvent, signalEvent
from optionPrimitives import optionPrimitive, nakedPut
from base import option
from riskManager import riskManagement
from typing import Optional, Text, Tuple
import datetime
import decimal
import enum
import json
import logging
import queue

# Used to keep track of reasons why options could not be found for the strategy.
class NoUpdateReason(enum.Enum):
  OK = 0
  NO_DELTA = 1
  NO_SETTLEMENT_PRICE = 2
  MIN_DTE = 3
  MAX_DTE = 4
  MIN_MAX_DELTA = 5
  MAX_BID_ASK = 6

class NakedPutStrat(strategy.Strategy):
  """This class sets up the strategy which sells naked puts.
  This strategy currently assumes that we are using EOD data for the backtesting.

  Specific strategy attributes:
    optPutToSellDelta:  Optimal delta for the put to sell.
    maxPutToSellDelta:  Maximum delta for the put to sell.
    minPutToSellDelta:  Minimum delta for the put to sell.

  General strategy attributes:
    startDateTime:  Date/time to start the backtest.
    underlyingTicker:  Which underlying to use for the strategy.
    orderQuantity:  Number of naked puts to sell.
    contractMultiplier: scaling factor for number of "shares" represented by an option or future. (E.g. 100 for options
                        and 50 for ES futures options).
    riskManagement: Risk management strategy (how to manage the trade; e.g., close, roll, hold to expiration).
    pricingSource -- Used to indicate which brokerage to use for commissions / fees.
    pricingSourceConfigFile -- File path to the JSON config file for commission / fees.

  Optional attributes:
    expCycle:  Specifies if we want to do monthly, weekly, quarterly, etc.
    optimalDTE:  Optimal number of days before expiration to put on strategy.
    minimumDTE:  Minimum number of days before expiration to put on strategy.
    maximumDTE: Maximum days to expiration to put on strategy.
    minimumROC:  Minimal return on capital for overall trade as a decimal.
    minCredit:  Minimum credit to collect on overall trade.
    maxBidAsk:  Maximum price to allow between bid and ask prices of option (for any strike or put/call).
    maxCapitalToUsePerTrade: percent (as a decimal) of portfolio value we want to use per trade.
"""

  def __init__(self, eventQueue:queue.Queue, optPutToSellDelta: float, maxPutToSellDelta: float,
               minPutToSellDelta: float, underlyingTicker: Text, orderQuantity: int, contractMultiplier: int,
               riskManagement: riskManagement.RiskManagement, pricingSource: Text, pricingSourceConfigFile: Text,
               expCycle: Optional[strategy.ExpirationTypes]=None, optimalDTE: Optional[int]=None,
               minimumDTE: Optional[int]=None, maximumDTE: Optional[int]=None, minimumROC: Optional[float]=None,
               minCredit: Optional[decimal.Decimal]=None, maxBidAsk: Optional[decimal.Decimal]=None,
               maxCapitalToUsePerTrade: Optional[decimal.Decimal]=None,
               startDateTime: Optional[datetime.datetime]=None):

    self.__eventQueue = eventQueue
    self.__optPutToSellDelta = optPutToSellDelta
    self.__maxPutToSellDelta = maxPutToSellDelta
    self.__minPutToSellDelta = minPutToSellDelta

    self.startDateTime=startDateTime
    self.buyOrSell=optionPrimitive.TransactionType.SELL
    self.underlyingTicker=underlyingTicker
    self.orderQuantity=orderQuantity
    self.contractMultiplier = contractMultiplier
    self.riskManagement = riskManagement
    self.pricingSourceConfigFile = pricingSourceConfigFile
    self.pricingSource = pricingSource
    self.expCycle=expCycle
    self.optimalDTE=optimalDTE
    self.minimumDTE=minimumDTE
    self.maximumDTE=maximumDTE
    self.minimumROC=minimumROC
    self.minCredit=minCredit
    self.maxBidAsk=maxBidAsk
    self.maxCapitalToUsePerTrade=maxCapitalToUsePerTrade

    # Open JSON file and select the pricingSource.
    self.pricingSourceConfig = None
    if self.pricingSource is not None and self.pricingSourceConfigFile is not None:
      with open(self.pricingSourceConfigFile) as config:
        fullConfig = json.load(config)
        self.pricingSourceConfig = fullConfig[self.pricingSource]

  def __updateWithOptimalOption(self, currentOption: option.Option,
                                optimalOption: option.Option, maxPutDelta: float, optPutDelta: float,
                                minPutDelta: float) -> Tuple[bool, option.Option, enum.Enum]:
    """Find the option that is closest to the requested parameters (delta, expiration).

    :param currentOption: current option from the option chain.
    :param optimalOption: current optimal option based on expiration and delta.
    :param maxPutDelta: maximum delta of the put option.
    :param optPutDelta: optimal delta of the put option.
    :param minPutDelta: minimum delta of the put option.
    :return: tuple of (updateOption: bool, optimalOpt: option.Option, noUpdateReason: enum.Enum ). updateOption bool is
             used to indicate if we should update the optimal option with the current option.
    """
    # TODO: Add support for expiration cycles other than monthly.
    # if self.expCycle == strategy.ExpirationTypes.MONTHLY:
    #   if not self.isMonthlyExp(currentOption.expirationDateTime):
    #     return noUpdateRule
    # else:
    #   return noUpdateRule

    # Check that delta is present in the data (could have bad data).
    if currentOption.delta is None:
      return (False, optimalOption, NoUpdateReason.NO_DELTA)

    # There is an error case in the input data where the options may have zero credit / debit when put on.
    if currentOption.settlementPrice is None:
      return (False, optimalOption, NoUpdateReason.NO_SETTLEMENT_PRICE)

    # Check that DTE is greater than the minimum.
    if self.minimumDTE:
      if not self.hasMinimumDTE(currentOption.dateTime, currentOption.expirationDateTime):
        return (False, optimalOption, NoUpdateReason.MIN_DTE)

    # Check that DTE is less than the maximum.
    if self.maximumDTE:
      if not self.hasMaximumDTE(currentOption.dateTime, currentOption.expirationDateTime):
        return (False, optimalOption, NoUpdateReason.MAX_DTE)

    # Check that delta is between the minimum and maximum delta.
    if currentOption.delta < maxPutDelta or currentOption.delta > minPutDelta:
      return (False, optimalOption, NoUpdateReason.MIN_MAX_DELTA)

    # Check if bid / ask of option < maxBidAsk specific in strangle strategy.
    if self.maxBidAsk:
      if self.calcBidAskDiff(currentOption.bidPrice, currentOption.askPrice) > self.maxBidAsk:
        return (False, optimalOption, NoUpdateReason.MAX_BID_ASK)

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
      return (False, newOptimalOption, NoUpdateReason.OK)

    return (True, newOptimalOption, NoUpdateReason.OK)

  def checkForSignal(self, event: tickEvent, portfolioNetLiquidity: decimal.Decimal,
                     availableBuyingPower: decimal.Decimal) -> None:
    """Criteria that we need to check before generating a signal event.
    We go through each option in the option chain and find all of the options that meet the criteria.  If there are
    multiple options that meet the criteria, we choose the first one, but we could use some other type of rule.

    Attributes:
      event: Tick data we parse through to determine if we want to create a nakedPut for the strategy.
      portfolioNetLiquidity: Net liquidity of portfolio.
      availableBuyingPower: Amount of buying power available to use.
    """
    # These variables will be used to keep track of the optimal options as we go through the option chain.
    optimalPutOptionToSell = None

    # Get the data from the tick event.
    eventData = event.getData()

    if not eventData:
      return

    print(eventData[0].dateTime)
    if self.startDateTime is not None:
      if eventData[0].dateTime < self.startDateTime:
        return

    # Dictionary to keep track of the reasons we couldn't find acceptable options for the strategy.
    noUpdateReasonDict = {}
    # Process one option at a time from the option chain (objects of option class).
    for currentOption in eventData:
      if currentOption.optionType == option.OptionTypes.PUT:
        # Handle put to sell.
        updateOption, putOptToSell, noUpdateReason = self.__updateWithOptimalOption(currentOption,
          optimalPutOptionToSell, self.__maxPutToSellDelta, self.__optPutToSellDelta, self.__minPutToSellDelta)
        if updateOption:
          optimalPutOptionToSell = putOptToSell
        else:
          noUpdateReasonDict['putToSell'] = noUpdateReason

    # Must check that both PUTs were found which are in the same expiration but do not have the same strike price.
    if optimalPutOptionToSell:
      nakedPutObj = nakedPut.NakedPut(self.orderQuantity, self.contractMultiplier, optimalPutOptionToSell,
                                      self.buyOrSell)

      # There is a case in the input data where the delta values are incorrect, and this results the strike price
      # of the long put being greater than the strike price of the short put, and this results in negative buying
      # power. To handle this error case, we return if the buying power is zero or negative.
      capitalNeeded = nakedPutObj.getBuyingPower()
      if capitalNeeded <= 0:
        return

      # Calculate opening and closing fees for the nakedPut.
      opening_fees = nakedPutObj.getCommissionsAndFees('open', self.pricingSource, self.pricingSourceConfig)
      nakedPutObj.setOpeningFees(opening_fees)
      nakedPutObj.setClosingFees(nakedPutObj.getCommissionsAndFees('close', self.pricingSource,
                                                                   self.pricingSourceConfig))

      # Update capitalNeeded to include the opening fees.
      capitalNeeded += opening_fees

      if self.maxCapitalToUsePerTrade:
        portfolioToUsePerTrade = decimal.Decimal(self.maxCapitalToUsePerTrade)*portfolioNetLiquidity
        maxBuyingPowerPerTrade = min(availableBuyingPower, portfolioToUsePerTrade)
      else:
        maxBuyingPowerPerTrade = availableBuyingPower

      numContractsToAdd = int(maxBuyingPowerPerTrade / capitalNeeded)
      if numContractsToAdd < 1:
        logging.warning('No contracts were added; check buying power.')
        return

      nakedPutObj.setNumContracts(numContractsToAdd)

      # Create signal event to put on naked put and add to queue.
      signalObj = [nakedPutObj, self.riskManagement]
      event = signalEvent.SignalEvent()
      event.createEvent(signalObj)
      self.__eventQueue.put(event)
    else:
      logging.info('Could not execute strategy. Reason: %s', noUpdateReasonDict)
