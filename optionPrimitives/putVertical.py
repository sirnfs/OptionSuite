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
      putToBuy:  put option
      putToSell:  put option
      buyOrSell:  Indicates if we want to the vertical to be long (buy) or short (sell).
  """
  def __init__(self, orderQuantity: int, putToBuy: put.Put, putToSell: put.Put,
               buyOrSell: optionPrimitive.TransactionType) -> None:

    if orderQuantity < 1:
      raise ValueError('Order quantity must be a positive (> 0) number.')
    if putToBuy.expirationDateTime != putToSell.expirationDateTime:
      raise ValueError('Both put options must have the same expiration.')
    self.__numContracts = orderQuantity
    self.__putToBuy = putToBuy
    self.__putToSell = putToSell
    self.__buyOrSell = buyOrSell

  def getDateTime(self) -> Optional[datetime.datetime]:
    """Get the current date/time for the options in the vertical."""
    if self.__putToBuy.dateTime is not None:
      return self.__putToBuy.dateTime
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

  def setNumContracts(self, numContracts: int) -> None:
    """Sets the number of contracts for the put vertical.
    :param numContracts: Number of put vertical contracts we want to put on.
    """
    self.__numContracts = numContracts

  def calcProfitLoss(self) -> decimal.Decimal:
    """Calculate the profit and loss for the vertical position using option values when the trade
    was placed and new option values.

    :return: Profit / loss (positive decimal for profit, negative decimal for loss).
    """
    putToBuyProfitLoss = -self.__putToBuy.calcOptionPriceDiff()
    putToSellProfitLoss = self.__putToSell.calcOptionPriceDiff()

    # Add the profit / loss of put and call, and multiply by the number of contracts.
    totProfitLoss = (putToBuyProfitLoss + putToSellProfitLoss) * self.__numContracts
    return totProfitLoss

  def calcProfitLossPercentage(self) -> float:
    """Calculate the profit and loss for the vertical position as a percentage of the initial trade price.

    :return: Profit / loss as a percentage of the initial option prices. Returns negative percentage for a loss.
    """
    # Add the profit / loss of put and call.
    totProfitLoss = self.calcProfitLoss()

    # Get the initial credit or debit paid for selling or buying the vertical, respectively.
    putToBuyCreditDebit = self.__putToBuy.tradePrice
    putToSellCreditDebit = self.__putToSell.tradePrice
    totCreditDebit = (putToBuyCreditDebit + putToSellCreditDebit) * 100 * self.__numContracts

    # Express totProfitLoss as a percentage.
    percentProfitLoss = (totProfitLoss / totCreditDebit) * 100
    return percentProfitLoss

  def getBuyingPower(self) -> decimal.Decimal:
    """The formula for calculating buying power is based off of TastyWorks. Note that this only applies to equity
    options (not futures options).
    buying power short put vertical = distance between strikes * 100 + (short put option price - long put option price)
    buying power long put vertical = difference between cost of two options * 100

    :return: Amount of buying power required to put on the trade.
    """
    currentPutToBuyPrice = (self.__putToBuy.askPrice + self.__putToBuy.bidPrice) / decimal.Decimal(2.0)
    currentPutToSellPrice = (self.__putToSell.askPrice + self.__putToSell.bidPrice) / decimal.Decimal(2.0)
    if self.__buyOrSell == optionPrimitive.TransactionType.BUY:
      buyingPower = (currentPutToBuyPrice - currentPutToSellPrice) * self.__numContracts * 100
      if buyingPower <= 0:
        logging.warning('Buying power cannot be less <= 0; check strikes in long putVertical')
    else:
      buyingPower = ((self.__putToSell.strikePrice - self.__putToBuy.strikePrice) - (
      currentPutToSellPrice - currentPutToBuyPrice)) * self.__numContracts * 100
      if buyingPower <= 0:
        logging.warning('Buying power cannot be <= 0; check strikes for short putVertical')
    return buyingPower

  def getCommissionsAndFees(self, openOrClose: Text, pricingSourceConfig: Dict[Any, Any]) -> decimal.Decimal:
    """Compute / apply the commissions and fees necessary to put on the trade.

    :param openOrClose: indicates whether we are opening or closing a trade, where the commissions can be different.
    :param pricingSourceConfig: JSON object for the pricing source. See the pricingConfig.json file for the structure.
    :return total commission and fees for opening or closing the trade.
    """
    # TODO(msantoro): At the moment, we only support SPX index options; add support for other options.
    if openOrClose == 'open':
      indexOptionConfig = pricingSourceConfig['stock_options']['index_option']['open']
      # Multiply by 2 to handle both puts in the vertical.
      return decimal.Decimal(2*self.getNumContracts() * (indexOptionConfig['commission_per_contract'] +
                                       indexOptionConfig['clearing_fee_per_contract'] +
                                       indexOptionConfig['orf_fee_per_contract']))
    elif openOrClose == 'close':
      indexOptionConfig = pricingSourceConfig['stock_options']['index_option']['close']
      putToBuyMidPrice = (self.__putToBuy.bidPrice + self.__putToBuy.askPrice) / decimal.Decimal(2.0)
      putToBuyFees = decimal.Decimal(indexOptionConfig['commission_per_contract'] +
                                     indexOptionConfig['clearing_fee_per_contract'] +
                                     indexOptionConfig['orf_fee_per_contract'] +
                                     indexOptionConfig['finra_taf_per_contract']) +\
                                     decimal.Decimal(
                                       indexOptionConfig['sec_fee_per_contract_wo_trade_price'])*putToBuyMidPrice
      putToSellMidPrice = (self.__putToSell.bidPrice + self.__putToSell.askPrice) / decimal.Decimal(2.0)
      putToSellFees = decimal.Decimal(indexOptionConfig['commission_per_contract'] +
                                      indexOptionConfig['clearing_fee_per_contract'] +
                                      indexOptionConfig['orf_fee_per_contract'] +
                                      indexOptionConfig['finra_taf_per_contract']) +\
                                      decimal.Decimal(
                                        indexOptionConfig['sec_fee_per_contract_wo_trade_price'])*putToSellMidPrice
      return decimal.Decimal(self.getNumContracts()) * (putToBuyFees + putToSellFees)
    else:
      raise TypeError('Only open or close types can be provided to getCommissionsAndFees().')

  def updateValues(self, tickData: Iterable[option.Option]) -> bool:
    """Based on the latest pricing data, update the option values for the vertical.

    :param tickData: option chain with pricing information (puts, calls)
    :return: returns True if we were able to update the options; false otherwise.
    """
    putToSell = self.__putToSell
    putStrike = putToSell.strikePrice
    putExpiration = putToSell.expirationDateTime

    # Go through the tickData to find the PUT option with a strike price that matches the putStrike above.
    # Note that this should not return more than one option since we specify the strike price, expiration,
    # and option type (PUT).
    # TODO: we can speed this up by indexing / keying the options by option symbol.
    matchingPutToSellOption = None
    for currentOption in tickData:
      if (currentOption.strikePrice == putStrike and currentOption.expirationDateTime == putExpiration and (
        currentOption.optionType == option.OptionTypes.PUT)):
        matchingPutToSellOption = currentOption
        break

    if matchingPutToSellOption is None:
      logging.warning("No matching short PUT was found in the option chain for the vertical; cannot update vertical.")
      return False

    putToBuy = self.__putToBuy
    putStrike = putToBuy.strikePrice
    putExpiration = putToBuy.expirationDateTime

    # Go through the tickData to find the PUT option with a strike price that matches the putStrike above
    # Note that this should not return more than one option since we specify the strike price, expiration,
    # and the option type (PUT).
    # TODO: we can speed this up by indexing / keying the options by option symbol.
    matchingPutToBuyOption = None
    for currentOption in tickData:
      if (currentOption.strikePrice == putStrike and currentOption.expirationDateTime == putExpiration and (
        currentOption.optionType == option.OptionTypes.PUT)):
        matchingPutToBuyOption = currentOption
        break

    if matchingPutToBuyOption is None:
      logging.warning("No matching long PUT was found in the option chain for the vertical; cannot update vertical.")
      return False

    # Update option intrinsics.
    putToSell.updateOption(matchingPutToSellOption)
    putToBuy.updateOption(matchingPutToBuyOption)
    return True

  def getNumberOfDaysLeft(self) -> int:
    """
    Determine the number of days between the dateTime and the expirationDateTime.
    :return: number of days between curDateTime and expDateTime.
    """
    # Since we require both put options to have the same dateTime and expirationDateTime, we can use either option to
    # get the number of days until expiration.
    putOpt = self.__putToBuy
    currentDateTime = putOpt.dateTime
    expirationDateTime = putOpt.expirationDateTime
    return (expirationDateTime - currentDateTime).days
