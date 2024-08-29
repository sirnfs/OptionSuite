from strategyManager import strategy
from events import tickEvent, signalEvent
from optionPrimitives import optionPrimitive, putVertical
from base import option
from riskManager import riskManagement
from typing import Optional, Text, Tuple, Mapping
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
    WRONG_TICKER = 7


class PutVerticalStrat(strategy.Strategy):
    """This class sets up the strategy which to put on put verticals.

      Specific strategy attributes:
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
        contractMultiplier: scaling factor for number of "shares" represented by an option or future. (E.g. 100 for
                            options and 50 for ES futures options).
        riskManagement: Risk management strategy (how to manage the trade; e.g., close, roll, hold to expiration).
        pricingSource:  Used to indicate which brokerage to use for commissions / fees.
        pricingSourceConfigFile:  File path to the JSON config file for commission / fees.

      Optional attributes:
        optimalDTE:  Optimal number of days before expiration to put on strategy.
        minimumDTE:  Minimum number of days before expiration to put on strategy.
        maximumDTE: Maximum days to expiration to put on strategy.
        maxBidAsk:  Maximum price to allow between bid and ask prices of option (for any strike or put/call).
        maxCapitalToUsePerTrade: percent (as a decimal) of portfolio value we want to use per trade.
    """

    def __init__(self, eventQueue: queue.Queue, optPutToBuyDelta: float, maxPutToBuyDelta: float,
                 minPutToBuyDelta: float, optPutToSellDelta: float, maxPutToSellDelta: float, minPutToSellDelta: float,
                 underlyingTicker: Text, orderQuantity: int, contractMultiplier: int,
                 riskManagement: riskManagement.RiskManagement, pricingSource: Text, pricingSourceConfigFile: Text,
                 optimalDTE: Optional[int] = None, minimumDTE: Optional[int] = None, maximumDTE: Optional[int] = None,
                 maxBidAsk: Optional[decimal.Decimal] = None, maxCapitalToUsePerTrade: Optional[decimal.Decimal] = None,
                 startDateTime: Optional[datetime.datetime] = None):

        self.__eventQueue = eventQueue
        self.__optPutToBuyDelta = optPutToBuyDelta
        self.__maxPutToBuyDelta = maxPutToBuyDelta
        self.__minPutToBuyDelta = minPutToBuyDelta
        self.__optPutToSellDelta = optPutToSellDelta
        self.__maxPutToSellDelta = maxPutToSellDelta
        self.__minPutToSellDelta = minPutToSellDelta

        self.startDateTime = startDateTime
        self.buyOrSell = optionPrimitive.TransactionType.SELL
        self.underlyingTicker = underlyingTicker
        self.orderQuantity = orderQuantity
        self.contractMultiplier = contractMultiplier
        self.riskManagement = riskManagement
        self.pricingSourceConfigFile = pricingSourceConfigFile
        self.pricingSource = pricingSource
        self.optimalDTE = optimalDTE
        self.minimumDTE = minimumDTE
        self.maximumDTE = maximumDTE
        self.maxBidAsk = maxBidAsk
        self.maxCapitalToUsePerTrade = maxCapitalToUsePerTrade

        # Open JSON file and select the pricingSource.
        self.pricingSourceConfig = None
        if self.pricingSource is not None and self.pricingSourceConfigFile is not None:
            with open(self.pricingSourceConfigFile) as config:
                fullConfig = json.load(config)
                self.pricingSourceConfig = fullConfig[self.pricingSource]

    def __updateWithOptimalOption(self, currentOption: option.Option, optimalOption: option.Option, maxPutDelta: float,
                                  optPutDelta: float, minPutDelta: float) -> Tuple[bool, option.Option, enum.Enum]:
        """Find the option that is closest to the requested parameters (delta, expiration).

        :param currentOption: current option from the option chain.
        :param optimalOption: current optimal option based on expiration and delta.
        :param maxPutDelta: maximum delta of the put option.
        :param optPutDelta: optimal delta of the put option.
        :param minPutDelta: minimum delta of the put option.
        :return: tuple of (updateOption: bool, optimalOpt: option.Option, noUpdateReason: enum.Enum ). updateOption bool
                 is used to indicate if we should update the optimal option with the current option.
        """
        # TODO: Add support for selecting specific expiration cycles (e.g., quarterly, monthly).

        # Check that we are using the right ticker symbol.
        if self.underlyingTicker not in currentOption.underlyingTicker:
            return (False, optimalOption, NoUpdateReason.WRONG_TICKER)

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

        # Check if bid / ask of option < maxBidAsk specific in put vertical strategy.
        # This can't be used for futures option data since bid and ask price are not reliable / zero / etc.
        if self.maxBidAsk:
            if self.calcBidAskDiff(currentOption.bidPrice, currentOption.askPrice) > self.maxBidAsk:
                return (False, optimalOption, NoUpdateReason.MAX_BID_ASK)

        # Get current DTE in days.
        currentDTE = self.getNumDays(currentOption.dateTime, currentOption.expirationDateTime)
        optimalDTE = self.getNumDays(optimalOption.dateTime,
                                     optimalOption.expirationDateTime) if optimalOption else None
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
        # We should not be able to enter this else.
        # else:
        #     return (False, newOptimalOption, NoUpdateReason.OK)

        return (True, newOptimalOption, NoUpdateReason.OK)

    def checkForSignal(self, event: tickEvent, portfolioNetLiquidity: decimal.Decimal,
                       availableBuyingPower: decimal.Decimal) -> Mapping[Text, NoUpdateReason]:
        """Criteria that we need to check before generating a signal event.
        We go through each option in the option chain and find all the options that meet the criteria.  If there are
        multiple options that meet the criteria, we choose the first one, but we could use some other type of rule.

        Attributes:
          event: Tick data we parse through to determine if we want to create a putVertical for the strategy.
          portfolioNetLiquidity: Net liquidity of portfolio.
          availableBuyingPower: Amount of buying power available to use.
        Return:
          Dictionary of reasons for why option(s) could not be updated. Empty dictionary if options updated.
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

        # Dictionary to keep track of the reasons we couldn't find acceptable options for the strategy.
        noUpdateReasonDict = {}
        # Process one option at a time from the option chain (objects of option class).
        for currentOption in eventData:
            if currentOption.optionType == option.OptionTypes.PUT:
                # Handle put to buy first.
                updateOption, putOptToBuy, noUpdateReason = self.__updateWithOptimalOption(
                    currentOption, optimalPutOptionToBuy, self.__maxPutToBuyDelta, self.__optPutToBuyDelta,
                    self.__minPutToBuyDelta)
                if updateOption:
                    optimalPutOptionToBuy = putOptToBuy
                if noUpdateReasonDict.get('putToBuy', None) is None or (
                    noUpdateReasonDict['putToBuy'] != NoUpdateReason.OK):
                  noUpdateReasonDict['putToBuy'] = noUpdateReason

                # Handle put to sell.
                updateOption, putOptToSell, noUpdateReason = self.__updateWithOptimalOption(
                    currentOption, optimalPutOptionToSell, self.__maxPutToSellDelta, self.__optPutToSellDelta,
                    self.__minPutToSellDelta)
                if updateOption:
                    optimalPutOptionToSell = putOptToSell
                if noUpdateReasonDict.get('putToSell', None) is None or (
                    noUpdateReasonDict['putToSell'] != NoUpdateReason.OK):
                    noUpdateReasonDict['putToSell'] = noUpdateReason

        # Must check that both PUTs were found which are in the same expiration but do not have the same strike price.
        if (optimalPutOptionToBuy and optimalPutOptionToSell) and (
            optimalPutOptionToBuy.expirationDateTime == optimalPutOptionToSell.expirationDateTime) and not (
              optimalPutOptionToBuy.strikePrice == optimalPutOptionToSell.strikePrice):
            putVerticalObj = putVertical.PutVertical(self.orderQuantity, self.contractMultiplier, optimalPutOptionToBuy,
                                                     optimalPutOptionToSell, self.buyOrSell)

            # There is a case in the input data where the delta values are incorrect, and this results the strike price
            # of the long put being greater than the strike price of the short put, and this results in negative buying
            # power. To handle this error case, we return if the buying power is zero or negative.
            capitalNeeded = putVerticalObj.getBuyingPower()
            if capitalNeeded <= 0:
                return

            # Calculate opening and closing fees for the putVertical.
            opening_fees = putVerticalObj.getCommissionsAndFees('open', self.pricingSource,
                                                                self.pricingSourceConfig)
            putVerticalObj.setOpeningFees(opening_fees)
            putVerticalObj.setClosingFees(putVerticalObj.getCommissionsAndFees('close', self.pricingSource,
                                                                               self.pricingSourceConfig))

            # Update capitalNeeded to include the opening fees.
            capitalNeeded += opening_fees

            if self.maxCapitalToUsePerTrade:
                portfolioToUsePerTrade = decimal.Decimal(self.maxCapitalToUsePerTrade) * portfolioNetLiquidity
                maxBuyingPowerPerTrade = min(availableBuyingPower, portfolioToUsePerTrade)
            else:
                maxBuyingPowerPerTrade = availableBuyingPower

            numContractsToAdd = int(maxBuyingPowerPerTrade / capitalNeeded)
            if numContractsToAdd < 1:
                return

            putVerticalObj.setNumContracts(numContractsToAdd)

            # Create signal event to put on put vertical strategy and add to queue.
            signalObj = [putVerticalObj, self.riskManagement]
            event = signalEvent.SignalEvent()
            event.createEvent(signalObj)
            self.__eventQueue.put(event)
        else:
            logging.info('Could not execute strategy. Reason: %s', noUpdateReasonDict)

        return noUpdateReasonDict
