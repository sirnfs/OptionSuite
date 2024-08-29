from base import option
from base import put
from optionPrimitives import optionPrimitive
from typing import Any, Dict, Iterable, Optional, Text
import datetime
import decimal
import logging


class PutVertical(optionPrimitive.OptionPrimitive):
    """This class sets up the put vertical option primitive.

    Attributes:
      orderQuantity:  number of put verticals.
      contractMultiplier: scaling factor for number of "shares" represented by an option or future. (E.g. 100 for
                          options and 50 for ES futures options).
      putToBuy:  put option
      putToSell:  put option
      buyOrSell:  Indicates if we want to the vertical to be long (buy) or short (sell).
    """

    def __init__(self, orderQuantity: int, contractMultiplier: int, putToBuy: put.Put, putToSell: put.Put,
                 buyOrSell: optionPrimitive.TransactionType) -> None:

        if orderQuantity < 1:
            raise ValueError('Order quantity must be a positive (> 0) number.')
        if contractMultiplier < 1:
            raise ValueError('Contract multiplier must be a positive (> 0) number.')
        if putToBuy.expirationDateTime != putToSell.expirationDateTime:
            raise ValueError('Both put options must have the same expiration.')
        self.__numContracts = orderQuantity
        self.__contractMultiplier = contractMultiplier
        self.__putToBuy = putToBuy
        self.__putToSell = putToSell
        self.__buyOrSell = buyOrSell
        # The opening and closing fees per vertical (one short and one long put) are populated by the strategyManager.
        self.__openingFees = None
        self.__closingFees = None

    def getDateTime(self) -> Optional[datetime.datetime]:
        """Get the current date/time for the options in the vertical."""
        if self.__putToBuy.dateTime is not None:
            return self.__putToBuy.dateTime
        return None

    def getExpirationDateTime(self) -> Optional[datetime.datetime]:
        """Gets the expiration date/time for the vertical."""
        if self.__putToBuy.expirationDateTime is not None:
            return self.__putToBuy.expirationDateTime
        return None

    def getUnderlyingTicker(self) -> Optional[Text]:
        """Get the name of the underlying being used for the vertical."""
        if self.__putToBuy.underlyingTicker is not None:
            return self.__putToBuy.underlyingTicker
        return None

    def getUnderlyingPrice(self) -> Optional[decimal.Decimal]:
        """Get the price of the underlying being used for the vertical."""
        if self.__putToBuy.underlyingPrice is not None:
            return self.__putToBuy.underlyingPrice
        return None

    def getDelta(self) -> Optional[float]:
        """Get the delta for the vertical.

        :return Delta of vertical or None if deltas don't exist for both options.
        """
        if self.__putToBuy.delta is not None and self.__putToSell.delta is not None:
            return self.__numContracts * (self.__putToBuy.delta + self.__putToSell.delta)
        return None

    def getVega(self) -> Optional[float]:
        """Get the vega for the vertical.

        :return Vega of vertical or None if vegas don't exist for both options.
        """
        if self.__putToBuy.vega is not None and self.__putToSell.vega is not None:
            return self.__numContracts * (self.__putToBuy.vega + self.__putToSell.vega)
        return None

    def getTheta(self) -> Optional[float]:
        """Get the theta for the vertical.

        :return Theta of vertical or None if thetas don't exist for both options.
        """
        if self.__putToBuy.theta is not None and self.__putToSell.theta is not None:
            return self.__numContracts * (self.__putToBuy.theta + self.__putToSell.theta)
        return None

    def getGamma(self) -> Optional[float]:
        """Get the gamma for the vertical.

        :return Gamma of vertical or None if gammas don't exist for both options.
        """
        if self.__putToBuy.gamma is not None and self.__putToSell.gamma is not None:
            return self.__numContracts * (self.__putToBuy.gamma + self.__putToSell.gamma)
        return None

    def getNumContracts(self) -> int:
        """Returns the total number of put verticals."""
        return self.__numContracts

    def getContractMultiplier(self) -> int:
        """Returns the contract multiplier."""
        return self.__contractMultiplier

    def setNumContracts(self, numContracts: int) -> None:
        """Sets the number of contracts for the put vertical.

        :param numContracts: Number of put vertical contracts we want to put on.
        """
        if numContracts < 1:
            raise ValueError('Number of contracts must be a positive (> 0) number.')
        self.__numContracts = numContracts

    def calcProfitLoss(self) -> decimal.Decimal:
        """Calculate the profit and loss for the vertical position using option values when the trade
        was placed and new option values.

        :return: Profit / loss (positive decimal for profit, negative decimal for loss).
        """
        putToBuyProfitLoss = -self.__putToBuy.calcOptionPriceDiff()
        putToSellProfitLoss = self.__putToSell.calcOptionPriceDiff()

        # Add the profit / loss of put and call, and multiply by the number of contracts.
        totProfitLoss = (putToBuyProfitLoss + putToSellProfitLoss) * self.__numContracts * self.__contractMultiplier
        return totProfitLoss

    def calcRealizedProfitLoss(self) -> decimal.Decimal:
        """This is the same as calcProfitLoss() except that we include the commissions and fees to close."""
        return self.calcProfitLoss() - self.getClosingFees() * self.__numContracts

    def calcProfitLossPercentage(self) -> float:
        """Calculate the profit and loss for the vertical position as a percentage of the initial trade price.

        :return: Profit / loss as a percentage of the initial option prices. Returns negative percentage for a loss.
        """
        # Add the profit / loss of put and call.
        totProfitLoss = self.calcProfitLoss()

        # Get the initial credit or debit paid for selling or buying the vertical, respectively.
        putToBuyCreditDebit = -self.__putToBuy.tradePrice
        putToSellCreditDebit = self.__putToSell.tradePrice
        totCreditDebit = (putToBuyCreditDebit + putToSellCreditDebit) * self.__contractMultiplier * self.__numContracts

        # Express totProfitLoss as a percentage.
        percentProfitLoss = (totProfitLoss / totCreditDebit) * 100
        return percentProfitLoss

    def getBuyingPower(self) -> decimal.Decimal:
        """The formula for calculating buying power is based off of TastyWorks. Note that this only applies to equity
        options (not futures options).
        buying power short put vertical = distance between strikes * contract multiplier +
                                          (short put option price - long put option price)
        buying power long put vertical = difference between cost of two options * contract multiplier

        :return: Amount of buying power required to put on the trade.
        """
        currentPutToBuyPrice = self.__putToBuy.settlementPrice
        currentPutToSellPrice = self.__putToSell.settlementPrice
        if self.__buyOrSell == optionPrimitive.TransactionType.BUY:
            buyingPower = (currentPutToBuyPrice - currentPutToSellPrice) * self.__numContracts * (
                self.__contractMultiplier)
            if buyingPower <= 0:
                logging.warning('Buying power cannot be less <= 0; check strikes in long putVertical')
        else:
            buyingPower = ((self.__putToSell.strikePrice - self.__putToBuy.strikePrice) - (
                currentPutToSellPrice - currentPutToBuyPrice)) * self.__numContracts * self.__contractMultiplier
            if buyingPower <= 0:
                logging.warning('Buying power cannot be <= 0; check strikes for short putVertical')
        return buyingPower

    def getCommissionsAndFees(self, openOrClose: Text, pricingSource: Text, pricingSourceConfig: Dict[Any, Any]) -> \
            decimal.Decimal:
        """Compute / apply the commissions and fees necessary to put on the trade. These are per put vertical contract,
        which consists of one short put and one long put.

        :param openOrClose: indicates whether we are opening or closing a trade, where the commissions can be different.
        :param pricingSource: indicates which source to read commissions and fee information from.
        :param pricingSourceConfig: JSON object for the pricing source. See pricingConfig.json file for the structure.
        :return total commission and fees for opening or closing the trade (per put vertical contract; two puts).
        """
        if pricingSource == 'tastyworks':
            putToBuySettlementPrice = self.__putToBuy.settlementPrice
            putToSellSettlementPrice = self.__putToSell.settlementPrice
            if openOrClose == 'open':
                indexOptionConfig = pricingSourceConfig['stock_options']['index_option']['open']
                secFees = indexOptionConfig['sec_fee_per_contract_wo_trade_price'] * float(putToSellSettlementPrice)
            elif openOrClose == 'close':
                indexOptionConfig = pricingSourceConfig['stock_options']['index_option']['close']
                secFees = indexOptionConfig['sec_fee_per_contract_wo_trade_price'] * float(putToBuySettlementPrice)
            else:
                raise TypeError('Only open or close types can be provided to getCommissionsAndFees().')

            # SEC fees only apply to one leg, not both, which is which it's not multiplied by '2'.
            return decimal.Decimal(2 * (indexOptionConfig['commission_per_contract'] +
                                        indexOptionConfig['clearing_fee_per_contract'] +
                                        indexOptionConfig['orf_fee_per_contract'] +
                                        indexOptionConfig['proprietary_index_fee_per_contract']) + secFees)
        elif pricingSource == 'tastyworks_futures':
            if openOrClose == 'open':
                esOptionConfig = pricingSourceConfig['futures_options']['es_option']['open']
            elif openOrClose == 'close':
                esOptionConfig = pricingSourceConfig['futures_options']['es_option']['close']
            else:
                raise TypeError('Only open or close types can be provided to getCommissionsAndFees().')
            return decimal.Decimal(2 * (esOptionConfig['commission_per_contract'] +
                                        esOptionConfig['clearing_fee_per_contract'] +
                                        esOptionConfig['nfa_fee_per_contract'] +
                                        esOptionConfig['exchange_fee_per_contract']))

    def updateValues(self, tickData: Iterable[option.Option]) -> bool:
        """Based on the latest pricing data, update the option values for the vertical.

        :param tickData: option chain with pricing information (puts, calls)
        :return: returns True if we were able to update the options; false otherwise.
        """
        putToSell = self.__putToSell
        putStrike = putToSell.strikePrice
        putExpiration = putToSell.expirationDateTime
        putTicker = putToSell.underlyingTicker

        # Go through the tickData to find the PUT option with a strike price that matches the putStrike above.
        # Note that this should not return more than one option since we specify the strike price, expiration,
        # and option type (PUT).
        # TODO: we can speed this up by indexing / keying the options by option symbol.
        matchingPutToSellOption = None
        for currentOption in tickData:
            if (putTicker in currentOption.underlyingTicker and currentOption.strikePrice == putStrike and (
                  currentOption.expirationDateTime == putExpiration) and (
                  currentOption.optionType == option.OptionTypes.PUT)):
                matchingPutToSellOption = currentOption
                break

        if matchingPutToSellOption is None:
            logging.warning(
                "No matching short PUT was found in the option chain for the vertical; cannot update vertical.")
            return False

        if matchingPutToSellOption.settlementPrice is None:
            logging.warning("Settlement price was zero for the put to sell option update; won't update. See below")
            logging.warning('Bad option info: %s', matchingPutToSellOption)
            return False

        putToBuy = self.__putToBuy
        putStrike = putToBuy.strikePrice
        putExpiration = putToBuy.expirationDateTime
        putTicker = putToBuy.underlyingTicker

        # Go through the tickData to find the PUT option with a strike price that matches the putStrike above
        # Note that this should not return more than one option since we specify the strike price, expiration,
        # and the option type (PUT).
        # TODO: we can speed this up by indexing / keying the options by option symbol.
        matchingPutToBuyOption = None
        for currentOption in tickData:
            if (putTicker in currentOption.underlyingTicker and currentOption.strikePrice == putStrike and (
                  currentOption.expirationDateTime == putExpiration) and (
                  currentOption.optionType == option.OptionTypes.PUT)):
                matchingPutToBuyOption = currentOption
                break

        if matchingPutToBuyOption is None:
            logging.warning(
                "No matching long PUT was found in the option chain for the vertical; cannot update vertical.")
            return False

        # This handles data errors in the CSV where there was no bid or ask price.
        if matchingPutToBuyOption.settlementPrice is None:
            logging.warning("Settlement price was zero for the put to buy option update; won't update. See below")
            logging.warning('Bad option info: %s', matchingPutToBuyOption)
            return False

        putToBuyProfitLoss = -(putToBuy.tradePrice - matchingPutToBuyOption.settlementPrice)
        putToSellProfitLoss = putToSell.tradePrice - matchingPutToSellOption.settlementPrice
        totProfitLoss = (putToBuyProfitLoss + putToSellProfitLoss) * self.__contractMultiplier

        # Get the initial credit or debit paid for selling or buying the vertical, respectively.
        putToBuyCreditDebit = -putToBuy.tradePrice
        putToSellCreditDebit = putToSell.tradePrice
        totCreditDebit = (putToBuyCreditDebit + putToSellCreditDebit) * self.__contractMultiplier

        # TODO(msantoro): This should be in the putVerticalOnDownMoveStrat and not here.
        # This check is here to prevent potential data errors in the CSV.
        if totCreditDebit <= 0:
            logging.warning('Total credit/debit <=0. Check bid/ask spread in CSV data for errors.')
            logging.warning('Put to buy: %s', putToBuy)
            logging.warning('Put to sell: %s', putToSell)
            return False

        # Express totProfitLoss as a percentage.
        percentProfitLoss = (totProfitLoss / totCreditDebit) * 100

        # This is a CSV data error case. Return False if the %profit is > 100 so that option is not updated, and the
        # option will be removed in portfolio.py.
        if abs(percentProfitLoss) > 100:
            logging.warning('Percent profit was greater than 100; cannot update vertical.')
            logging.warning('Put to buy: %s', putToBuy)
            logging.warning('Put to sell: %s', putToSell)
            return False

        # Update option intrinsics.
        putToSell.updateOption(matchingPutToSellOption)
        putToBuy.updateOption(matchingPutToBuyOption)
        return True

    def getNumberOfDaysLeft(self) -> int:
        """Determine the number of days between the dateTime and the expirationDateTime.

        :return: number of days between curDateTime and expDateTime.
        """
        # Since we require both put options to have the same dateTime and expirationDateTime, we can use either option
        # to get the number of days until expiration.
        putOpt = self.__putToBuy
        currentDateTime = putOpt.dateTime
        expirationDateTime = putOpt.expirationDateTime
        return (expirationDateTime - currentDateTime).days

    def getOpeningFees(self) -> decimal.Decimal:
        """Get the saved opening fees for the put vertical.

        :return: opening fees.
        """
        if self.__openingFees is None:
            raise ValueError('Opening fees have not been populated in the respective strategyManager class.')
        return self.__openingFees

    def setOpeningFees(self, openingFees: decimal.Decimal) -> None:
        """Set the opening fees for the put vertical per contract (one short and one long put)

        :param openingFees: cost to open put vertical.
        """
        self.__openingFees = openingFees

    def getClosingFees(self) -> decimal.Decimal:
        """Get the saved closing fees for the put vertical.

        :return: closing fees.
        """
        if self.__closingFees is None:
            raise ValueError('Closing fees have not been populated in the respective strategyManager class.')
        return self.__closingFees

    def setClosingFees(self, closingFees: decimal.Decimal) -> None:
        """Set the closing fees for the put vertical per contract (one short and one long put).

        :param closingFees: cost to close put vertical.
        """
        self.__closingFees = closingFees
