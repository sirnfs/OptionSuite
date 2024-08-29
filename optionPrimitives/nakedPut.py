from base import option
from base import put
from optionPrimitives import optionPrimitive
from typing import Any, Dict, Iterable, Optional, Text
import datetime
import decimal
import logging


class NakedPut(optionPrimitive.OptionPrimitive):
    """This class sets up the naked put option primitive.

      Attributes:
        orderQuantity:  number of naked puts.
        contractMultiplier: scaling factor for number of "shares" represented by an option or future. (E.g. 100 for
                            options and 50 for ES futures options).
        putToBuyOrSell:  put option
        buyOrSell:  Indicates if we want to the put to be long (buy) or short (sell) the put.
    """

    def __init__(self, orderQuantity: int, contractMultiplier: int, putToBuyOrSell: put.Put,
                 buyOrSell: optionPrimitive.TransactionType) -> None:
        if orderQuantity < 1:
            raise ValueError('Order quantity must be a positive (> 0) number.')
        self.__numContracts = orderQuantity
        self.__contractMultiplier = contractMultiplier
        self.__putToBuyOrSell = putToBuyOrSell
        self.__buyOrSell = buyOrSell
        # The opening and closing fees for the naked put are populated by the strategyManager.
        self.__openingFees = None
        self.__closingFees = None

    def getDateTime(self) -> Optional[datetime.datetime]:
        """Get the current date/time for the naked put."""
        if self.__putToBuyOrSell.dateTime is not None:
            return self.__putToBuyOrSell.dateTime
        return None

    def getTradeDateTime(self) -> Optional[datetime.datetime]:
        """Gets the date/time for when the naked put was created."""
        if self.__putToBuyOrSell.tradeDateTime is not None:
            return self.__putToBuyOrSell.tradeDateTime
        return None

    def getExpirationDateTime(self) -> Optional[datetime.datetime]:
        """Gets the expiration date/time for the naked put."""
        if self.__putToBuyOrSell.expirationDateTime is not None:
            return self.__putToBuyOrSell.expirationDateTime
        return None

    def getUnderlyingTicker(self) -> Optional[Text]:
        """Get the name of the underlying being used for the naked put."""
        if self.__putToBuyOrSell.underlyingTicker is not None:
            return self.__putToBuyOrSell.underlyingTicker
        return None

    def getUnderlyingPrice(self) -> Optional[decimal.Decimal]:
        """Get the price of the underlying being used for the naked put."""
        if self.__putToBuyOrSell.underlyingPrice is not None:
            return self.__putToBuyOrSell.underlyingPrice
        return None

    def getDelta(self) -> Optional[float]:
        """Get total delta (all contracts) for the naked put.

          :return Delta of naked put.
        """
        return self.__numContracts * self.__putToBuyOrSell.delta

    def getVega(self) -> Optional[float]:
        """Get total vega for the naked put.

          :return Vega of naked put.
        """
        return self.__numContracts * self.__putToBuyOrSell.vega

    def getTheta(self) -> Optional[float]:
        """Get total theta for the naked put.

          :return Theta of naked put.
        """
        return self.__numContracts * self.__putToBuyOrSell.theta

    def getGamma(self) -> Optional[float]:
        """Get total gamma for the naked put.

          :return Gamma of naked put.
        """
        return self.__numContracts * self.__putToBuyOrSell.gamma

    def getNumContracts(self) -> int:
        """Returns the total number of naked puts."""
        return self.__numContracts

    def getContractMultiplier(self) -> int:
        """Returns the contract multiplier."""
        return self.__contractMultiplier

    def setNumContracts(self, numContracts: int) -> None:
        """Sets the number of contracts for the naked put.

          :param numContracts: Number of naked put contracts we want to put on.
        """
        if numContracts < 1:
            raise ValueError('Number of contracts must be a positive (> 0) number.')
        self.__numContracts = numContracts

    def calcProfitLoss(self) -> decimal.Decimal:
        """Calculate the profit and loss for the naked put using option values when the trade was placed and new option
          values from tick data.

          :return: Profit / loss (positive decimal for profit, negative decimal for loss).
        """
        putProfitLoss = self.__putToBuyOrSell.calcOptionPriceDiff()
        if self.__buyOrSell == optionPrimitive.TransactionType.BUY:
            putProfitLoss = -putProfitLoss

        # Multiple profit / loss of naked put by the number of contracts and contract multiplier.
        totProfitLoss = putProfitLoss * self.__numContracts * self.__contractMultiplier
        return totProfitLoss

    def calcProfitLossPercentage(self) -> float:
        """Calculate the profit and loss for the naked put as a percentage of the initial trade price.

          :return: Profit / loss as a percentage of the initial trade price. Returns a negative percentage for a loss.
        """
        totProfitLoss = self.calcProfitLoss()

        # Calculate the initial credit or debit paid for selling or buying the naked put.
        totCreditDebit = self.__putToBuyOrSell.tradePrice * self.__contractMultiplier * self.__numContracts

        # Express totProfitLoss as a percentage.
        percentProfitLoss = (totProfitLoss / totCreditDebit) * 100
        return percentProfitLoss

    def getBuyingPower(self) -> decimal.Decimal:
        """The formula for calculating buying power is based off of Tastyworks. Note that this only applies to equity
          options (not futures options).
          buying power short put -- greatest of (1, 2) * number of contracts * 100:
            (1) 20% of the underlying price minus the out of money amount plus the option premium
            (2) 10% of the strike price plus the option premium
          buying power long put = premium of the put * number of contracts

          :return: Amount of buying power required to put on the trade.
        """
        currentPutPrice = self.__putToBuyOrSell.settlementPrice
        if self.__buyOrSell == optionPrimitive.TransactionType.BUY:
            buyingPower = currentPutPrice * self.__numContracts * self.__contractMultiplier
            if buyingPower <= 0:
                logging.warning('Buying power cannot be less <= 0; check option data.')
        else:
            buyingPower1 = decimal.Decimal(-0.8) * self.__putToBuyOrSell.underlyingPrice + (
                self.__putToBuyOrSell.strikePrice + currentPutPrice)
            buyingPower2 = decimal.Decimal(0.1) * self.__putToBuyOrSell.strikePrice + currentPutPrice
            maxBuyingPower = max(buyingPower1, buyingPower2)

            buyingPower = maxBuyingPower * self.__numContracts * self.__contractMultiplier
            if buyingPower <= 0:
                logging.warning('Buying power cannot be <= 0; check option data.')
        return buyingPower

    def getCommissionsAndFees(self, openOrClose: Text, pricingSource: Text, pricingSourceConfig: Dict[Any, Any]) -> \
            decimal.Decimal:
        """Compute / apply the commissions and fees necessary to put on the trade.

          :param openOrClose: indicates whether we are opening or closing a trade; commissions may be different.
          :param pricingSource: indicates which source to read commissions and fee information from.
          :param pricingSourceConfig: JSON object for the pricing source. See pricingConfig.json for the file structure.
          :return total commission and fees for opening or closing the trade.
        """
        if pricingSource == 'tastyworks':
            putToBuyOrSellSettlementPrice = self.__putToBuyOrSell.settlementPrice
            if openOrClose == 'open':
                indexOptionConfig = pricingSourceConfig['stock_options']['index_option']['open']
            elif openOrClose == 'close':
                indexOptionConfig = pricingSourceConfig['stock_options']['index_option']['close']
            else:
                raise TypeError('Only open or close types can be provided to getCommissionsAndFees().')

            secFees = indexOptionConfig['sec_fee_per_contract_wo_trade_price'] * float(putToBuyOrSellSettlementPrice)
            return decimal.Decimal(indexOptionConfig['commission_per_contract'] +
                                   indexOptionConfig['clearing_fee_per_contract'] +
                                   indexOptionConfig['orf_fee_per_contract'] +
                                   indexOptionConfig['proprietary_index_fee_per_contract'] + secFees)
        elif pricingSource == 'tastyworks_futures':
            if openOrClose == 'open':
                esOptionConfig = pricingSourceConfig['futures_options']['es_option']['open']
            elif openOrClose == 'close':
                esOptionConfig = pricingSourceConfig['futures_options']['es_option']['close']
            else:
                raise TypeError('Only open or close types can be provided to getCommissionsAndFees().')
            return decimal.Decimal(
                esOptionConfig['commission_per_contract'] + esOptionConfig['clearing_fee_per_contract'] +
                esOptionConfig['nfa_fee_per_contract'] + esOptionConfig['exchange_fee_per_contract'])

    def updateValues(self, tickData: Iterable[option.Option]) -> bool:
        """Based on the latest price data, update the option values for the naked put.

          :param tickData: option chain with price information (puts, calls)
          :return: returns True if we were able to update the options; false otherwise.
        """
        putToBuyOrSell = self.__putToBuyOrSell
        putStrike = putToBuyOrSell.strikePrice
        putExpiration = putToBuyOrSell.expirationDateTime

        # Go through the tickData to find the PUT option with a strike price that matches the putStrike above.
        # Note that this should not return more than one option since we specify the strike price, expiration,
        # and option type (PUT).
        # TODO: we can speed this up by indexing / keying the options by option symbol.
        matchingPutToBuyOrSellOption = None
        for currentOption in tickData:
            if (currentOption.strikePrice == putStrike and currentOption.expirationDateTime == putExpiration and (
               currentOption.optionType == option.OptionTypes.PUT)):
                # TODO: is there not actually an optionType in currentOption?
                matchingPutToBuyOrSellOption = currentOption
                break

        if matchingPutToBuyOrSellOption is None:
            logging.warning("No matching PUT was found in the option chain; cannot update naked put.")
            return False

        if matchingPutToBuyOrSellOption.settlementPrice is None:
            logging.warning("Settlement price was zero for the put to update; won't update. See warning below.")
            logging.warning('Bad option info: %s', matchingPutToBuyOrSellOption)
            return False

        # Update option intrinsics.
        putToBuyOrSell.updateOption(matchingPutToBuyOrSellOption)
        return True

    def getNumberOfDaysLeft(self) -> int:
        """Determine the number of days between the dateTime and the expirationDateTime.

          :return: number of days between curDateTime and expDateTime.
        """
        putToBuyOrSell = self.__putToBuyOrSell
        currentDateTime = putToBuyOrSell.dateTime
        expirationDateTime = putToBuyOrSell.expirationDateTime
        return (expirationDateTime - currentDateTime).days

    def getOpeningFees(self) -> decimal.Decimal:
        """Get the saved opening fees for the naked put.

          :return: opening fees.
        """
        return self.__openingFees

    def setOpeningFees(self, openingFees: decimal.Decimal) -> None:
        """Set the opening fees for the naked put.

          :param openingFees: cost to open naked put.
        """
        self.__openingFees = openingFees

    def getClosingFees(self) -> decimal.Decimal:
        """Get the saved closing fees for the naked put.

          :return: closing fees.
        """
        return self.__closingFees

    def setClosingFees(self, closingFees: decimal.Decimal) -> None:
        """Set the closing fees for the naked put.

          :param closingFees: cost to close naked put.
        """
        self.__closingFees = closingFees
