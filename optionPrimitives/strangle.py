from base import call
from base import option
from base import put
from optionPrimitives import optionPrimitive
from typing import Any, Dict, Iterable, Optional, Text
import datetime
import decimal
import logging

class Strangle(optionPrimitive.OptionPrimitive):
  """This class sets up the strangle option primitive.

    Attributes:
      orderQuantity:  number of strangles
      callOpt:  call option
      putOpt:  put option
      buyOrSell:  Indicates if we want to buy or sell the strangle.
  """
  def __init__(self, orderQuantity: int, callOpt: call.Call, putOpt: put.Put,
               buyOrSell: optionPrimitive.TransactionType) -> None:

    if orderQuantity < 1:
      raise ValueError('Order quantity must be a positive (> 0) number.')
    self.__numContracts = orderQuantity
    self.__putOpt = putOpt
    self.__callOpt = callOpt
    self.__buyOrSell = buyOrSell

  def getDateTime(self) -> Optional[datetime.datetime]:
    """Get the current date/time for the options in the strange."""
    if self.__putOpt.dateTime is not None:
      return self.__putOpt.dateTime
    return None

  def getUnderlyingTicker(self) -> Optional[Text]:
    """Get the name of the underlying being used for the strangle."""
    if self.__putOpt.underlyingTicker is not None:
      return self.__putOpt.underlyingTicker
    return None

  def getUnderlyingPrice(self) -> Optional[decimal.Decimal]:
    """Get the price of the underlying being used for the strangle."""
    if self.__putOpt.underlyingPrice is not None:
      return self.__putOpt.underlyingPrice
    return None

  def getDelta(self) -> Optional[float]:
    """Get the delta for the strangle.

    :return Delta of strangle or None if deltas don't exist for both options.
    """
    if self.__putOpt.delta is not None and self.__callOpt.delta is not None:
      return self.__numContracts * (self.__putOpt.delta + self.__callOpt.delta)
    return None

  def getVega(self) -> Optional[float]:
    """Get the vega for the strangle.

    :return Vega of strangle or None if vegas don't exist for both options.
    """
    if self.__putOpt.vega is not None and self.__callOpt.vega is not None:
      return self.__numContracts * (self.__putOpt.vega + self.__callOpt.vega)
    return None

  def getTheta(self) -> Optional[float]:
    """Get the theta for the strangle.

    :return Theta of strange or None if thetas don't exist for both options.
    """
    if self.__putOpt.theta is not None and self.__callOpt.theta is not None:
      return self.__numContracts * (self.__putOpt.theta + self.__callOpt.theta)
    return None

  def getGamma(self) -> Optional[float]:
    """Get the gamma for the strangle.

    :return Gamma of strange or None if gammas don't exist for both options.
    """
    if self.__putOpt.gamma is not None and self.__callOpt.gamma is not None:
      return self.__numContracts * (self.__putOpt.gamma + self.__callOpt.gamma)
    return None

  def setNumContracts(self, numContracts: int) -> None:
    """Sets the number of contracts for the strangle primitive.
    :param numContracts: Number of strangle contracts we want to put on.
    """
    self.__numContracts = numContracts

  def calcProfitLoss(self) -> decimal.Decimal:
    """Calculate the profit and loss for the strangle position using option values when the trade
    was placed and new option values.  Note that profit and loss are reversed if we buy or sell a put/call;
    if we buy a put/call, we want the option value to increase; if we sell a put/call, we want the option value
    to decrease.

    :return: Profit / loss (positive decimal for profit, negative decimal for loss).
    """
    # Handle profit / loss for put first.
    putProfitLoss = self.__putOpt.calcOptionPriceDiff()
    callProfitLoss = self.__callOpt.calcOptionPriceDiff()

    # If we're buying the strangle, we have the opposite of the selling case.
    if self.__buyOrSell == optionPrimitive.TransactionType.BUY:
      putProfitLoss = -putProfitLoss
      callProfitLoss = -callProfitLoss

    # Add the profit / loss of put and call, and multiply by the number of contracts.
    totProfitLoss = (putProfitLoss + callProfitLoss) * self.__numContracts
    return totProfitLoss

  def calcProfitLossPercentage(self) -> float:
    """Calculate the profit and loss for the strangle position as a percentage of the initial trade price.

    :return: Profit / loss as a percentage of the initial option prices. Returns negative percentage for a loss.
    """
    # Add the profit / loss of put and call.
    totProfitLoss = self.calcProfitLoss()

    # Get the initial credit or debit paid for selling or buying the strangle, respectively.
    callCreditDebit = self.__callOpt.tradePrice
    putCreditDebit = self.__putOpt.tradePrice
    totCreditDebit = (callCreditDebit + putCreditDebit) * 100 * self.__numContracts

    # Express totProfitLoss as a percentage.
    percentProfitLoss = (totProfitLoss / totCreditDebit) * 100
    return percentProfitLoss

  def getNumContracts(self) -> int:
    """Returns the total number of strangles."""
    return self.__numContracts

  def getBuyingPower(self) -> decimal.Decimal:
    """The formula for calculating buying power is based off of TastyWorks. This is for cash settled indices!
      There are two possible methods to calculate buying power, and the method which generates the maximum possible
      buying power is the one chosen.

      :return: Amount of buying power required to put on the trade.
    """
    currentCallPrice = (self.__callOpt.askPrice + self.__callOpt.bidPrice) / decimal.Decimal(2.0)
    currentPutPrice = (self.__putOpt.askPrice + self.__putOpt.bidPrice) / decimal.Decimal(2.0)
    # Method 1 - 25% rule -- 25% of the underlying, less the difference between the strike price and the stock
    # price, plus the option value, multiplied by number of contracts. Use one of the options to get underlying
    # price (call option used here).
    underlyingPrice = self.__callOpt.underlyingPrice

    # Handle call side of strangle.
    callBuyingPower1 = ((decimal.Decimal(0.25) * underlyingPrice)-(
      self.__callOpt.strikePrice - underlyingPrice) + currentCallPrice) * self.__numContracts * 100
    # Handle put side of strangle.
    putBuyingPower1 = ((decimal.Decimal(0.25) * underlyingPrice)-(
      underlyingPrice - self.__putOpt.strikePrice) + currentPutPrice) * self.__numContracts * 100
    methodOneBuyingPower = max(callBuyingPower1, putBuyingPower1)

    # Method 2 - 15% rule -- 15% of the exercise value plus premium value.
    # Handle call side of strangle.
    callBuyingPower2 = (decimal.Decimal(0.15) * self.__callOpt.strikePrice + currentCallPrice) * (
      self.__numContracts * 100)
    # Handle put side of strangle.
    putBuyingPower2 = (decimal.Decimal(0.15) * self.__putOpt.strikePrice + currentPutPrice) * self.__numContracts * 100
    methodTwoBuyingPower = max(callBuyingPower2, putBuyingPower2)

    return max(methodOneBuyingPower, methodTwoBuyingPower)

  def getCommissionsAndFees(self, openOrClose: Text, pricingSourceConfig: Dict[Any, Any]) -> decimal.Decimal:
    """Compute / apply the commissions and fees necessary to put on the trade.

    :param openOrClose: indicates whether we are opening or closing a trade, where the commissions can be different.
    :param pricingSourceConfig: JSON object for the pricing source. See the pricingConfig.json file for the structure.
    :return total commission and fees for opening or closing the trade.
    """
    # TODO(msantoro): At the moment, we only support SPX index options; add support for other options.
    if openOrClose == 'open':
      indexOptionConfig = pricingSourceConfig['stock_options']['index_option']['open']
      # Multiply by 2 to handle put and call.
      return decimal.Decimal(2*self.getNumContracts() * (indexOptionConfig['commission_per_contract'] +
                                       indexOptionConfig['clearing_fee_per_contract'] +
                                       indexOptionConfig['orf_fee_per_contract']))
    elif openOrClose == 'close':
      indexOptionConfig = pricingSourceConfig['stock_options']['index_option']['close']
      putMidPrice = (self.__putOpt.bidPrice + self.__putOpt.askPrice) / decimal.Decimal(2.0)
      putFees = decimal.Decimal(indexOptionConfig['commission_per_contract'] +
                                     indexOptionConfig['clearing_fee_per_contract'] +
                                     indexOptionConfig['orf_fee_per_contract'] +
                                     indexOptionConfig['finra_taf_per_contract']) +\
                                     decimal.Decimal(
                                       indexOptionConfig['sec_fee_per_contract_wo_trade_price'])*putMidPrice
      callMidPrice = (self.__callOpt.bidPrice + self.__callOpt.askPrice) / decimal.Decimal(2.0)
      callFees = decimal.Decimal(indexOptionConfig['commission_per_contract'] +
                                      indexOptionConfig['clearing_fee_per_contract'] +
                                      indexOptionConfig['orf_fee_per_contract'] +
                                      indexOptionConfig['finra_taf_per_contract']) +\
                                      decimal.Decimal(
                                        indexOptionConfig['sec_fee_per_contract_wo_trade_price'])*callMidPrice
      return decimal.Decimal(self.getNumContracts()) * (putFees + callFees)
    else:
      raise TypeError('Only open or close types can be provided to getCommissionsAndFees().')

  def updateValues(self, tickData: Iterable[option.Option]) -> bool:
    """Based on the latest pricing data, update the option values for the strangle.

    :param tickData: option chain with pricing information (puts, calls)
    :return: returns True if we were able to update the options; false otherwise.
    """
    # Work with put option first.
    putOpt = self.__putOpt
    putStrike = putOpt.strikePrice
    putExpiration = putOpt.expirationDateTime

    # Go through the tickData to find the PUT option with a strike price that matches the putStrike above.
    # Note that this should not return more than one option since we specify the strike price, expiration,
    # option type (PUT), and option symbol.
    # TODO: we can speed this up by indexing / keying the options by option symbol.
    matchingPutOption = None
    for currentOption in tickData:
      if (currentOption.strikePrice == putStrike and currentOption.expirationDateTime == putExpiration and (
        currentOption.optionType == option.OptionTypes.PUT)):
        matchingPutOption = currentOption
        break

    if not matchingPutOption:
      logging.warning("No matching PUT was found in the option chain for the strangle; cannot update strangle.")
      return False

    # Work with call option.
    callOpt = self.__callOpt
    callStrike = callOpt.strikePrice
    callExpiration = callOpt.expirationDateTime

    # Go through the tickData to find the CALL option with a strike price that matches the callStrike above
    # Note that this should not return more than one option since we specify the strike price, expiration,
    # the option type (CALL), and option symbol.
    # TODO: we can speed this up by indexing / keying the options by option symbol.
    matchingCallOption = None
    for currentOption in tickData:
      if (currentOption.strikePrice == callStrike and currentOption.expirationDateTime == callExpiration and (
        currentOption.optionType == option.OptionTypes.CALL)):
        matchingCallOption = currentOption
        break

    if not matchingCallOption:
      logging.warning("No matching CALL was found in the option chain for the strangle; cannot update strangle.")
      return False

    # Update option intrinsics
    putOpt.updateOption(matchingPutOption)
    callOpt.updateOption(matchingCallOption)
    return True

  def getNumberOfDaysLeft(self) -> int:
    """
    Determine the number of days between the dateTime and the expirationDateTime.
    :return: number of days between curDateTime and expDateTime.
    """
    # Since we require the put and call options to have the same dateTime and expirationDateTime, we can use either
    # option to get the number of days until expiration.
    putOpt = self.__putOpt
    currentDateTime = putOpt.dateTime
    expirationDateTime = putOpt.expirationDateTime
    return (expirationDateTime - currentDateTime).days
