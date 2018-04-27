from optionPrimitive import OptionPrimitive
import logging

class Strangle(OptionPrimitive):
    """This class sets up the strangle option primitive.
           
        Attributes:
           orderQuantity:  number of strangles
           callOpt:  call option
           putOpt:  put option
           buyOrSell:  Indicates if we want to buy or sell the strangle ("BUY" or "SELL").

        Optional attributes:
           daysBeforeClosing:  Number of days before expiration to close the trade.
           profitTargetPercent:  Percentage of initial credit to use when closing trade.
           customManagement:  boolean -- manages trade using custom strategy.
           maxBidAsk:  Maximum price to allow between bid and ask prices of option (for any strike or put/call).
           maxMidDev:  Maximum deviation from midprice on opening and closing of trade (e.g., 0.02 cents from midprice).
    """
    def __init__(self, orderQuantity, callOpt, putOpt, buyOrSell, daysBeforeClosing=None, profitTargetPercent=None,
                 customManagement=None, maxBidAsk=None, maxMidDev=None):

        self.__numContracts = orderQuantity
        self.__putOpt = putOpt
        self.__callOpt = callOpt
        self.__buyOrSell = buyOrSell
        self.__daysBeforeClosing = daysBeforeClosing
        self.__profitTargetPercent = profitTargetPercent
        self.__customManagement = customManagement
        self.__maxBidAsk = maxBidAsk
        self.__maxMidDev = maxMidDev

        # If there is no tick data when reading the CSV data, e.g., if the option chain isn't being updated, we need to
        # delete the strangle position from the portfolio.
        self.__forceClose = False

    def getUnderlyingTicker(self):
        """Get the name (string) of the underlying being used for the strangle.
        """
        return self.__putOpt.getUnderlyingTicker()

    def getPutOption(self):
        """Return the put option portion of the strangle.
        """
        return self.__putOpt

    def getCallOption(self):
        """Return the call option portion of the strangle.
        """
        return self.__callOpt

    def getDelta(self):
        """Used to get the delta for the strangle.
        """
        if self.__putOpt.getDelta() and self.__putOpt.getDelta():
            totPutDelta = self.__numContracts*self.__putOpt.getDelta()
            totCallDelta = self.__numContracts*self.__callOpt.getDelta()

            return (totCallDelta + totPutDelta)
        else:
            return None

    def getVega(self):
        """Used to get the vega for the strangle.
        """
        if self.__putOpt.getVega() and self.__callOpt.getVega():
            totPutVega = self.__numContracts * self.__putOpt.getVega()
            totCallVega = self.__numContracts * self.__callOpt.getVega()

            return (totCallVega + totPutVega)
        else:
            return None

    def getTheta(self):
        """Used to get the theta for the strangle.
        """
        if self.__putOpt.getTheta() and self.__callOpt.getTheta():
            totPutTheta = self.__numContracts * self.__putOpt.getTheta()
            totCallTheta = self.__numContracts * self.__callOpt.getTheta()

            return (totCallTheta + totPutTheta)
        else:
            return None

    def getGamma(self):
        """Used to get the gamma for the strangle.
        """
        if self.__putOpt.getGamma() and self.__callOpt.getGamma():
            totPutGamma = self.__numContracts * self.__putOpt.getGamma()
            totCallGamma = self.__numContracts * self.__callOpt.getGamma()

            return (totCallGamma + totPutGamma)
        else:
            return None

    def getDaysBeforeClosing(self):
        """Used to get the number of days before closing for which we should manage / close the strangle.
        :return: Number of days
        """
        return self.__daysBeforeClosing

    def getProfitTargetPercent(self):
        """Get the profit target percent we require to close out a strangle if we're doing early management.
        :return: Profit target percent as a deicmal (0 to 1).
        """
        return self.__profitTargetPercent

    def getCustomManagementFlag(self):
        """In the case we want to some more complex strategy management, check to see if this flag is set.
        :return: True if flag set; False otherwise.
        """
        return self.__customManagement

    def setNumContracts(self, numContracts):
        """Sets the number of contracts for the strangle primitive.
        :param numContracts: Number of strangle contracts we want to put on.
        """
        self.__numContracts = numContracts

    def calcProfitLoss(self):
        """Calculate the profit and loss for the strangle position using option values when the trade
        was placed and new option values.  Note that profit and loss are reversed if we buy or sell a put/call;
        if we buy a put/call, we want the option value to increase; if we sell a put/call, we want the option value
        to decrease.

        :return: Profit / loss (positive decimal for profit, negative decimal for loss).
        """

        # Handle profit / loss for put first.
        putOpt = self.__putOpt
        putProfitLoss = putOpt.calcOptionPriceDiff()

        # If we're buying the strangle, we will have a loss if the put option decreases in value.
        if self.__buyOrSell == "BUY":
            putProfitLoss = -putProfitLoss

        # Handle profit /loss for the call next.
        callOpt = self.__callOpt
        callProfitLoss = callOpt.calcOptionPriceDiff()

        if self.__buyOrSell == "BUY":
            callProfitLoss = -callProfitLoss

        # Add the profit / loss of put and call, and multiply by the number of contracts.
        totProfitLoss = (putProfitLoss + callProfitLoss) * self.__numContracts

        return totProfitLoss

    def calcProfitLossPercentage(self):
        """Calculate the profit and loss for the strangle position using option values when the trade
        was placed and new option values.  Note that profit and loss are reversed if we buy or sell a put/call;
        if we buy a put/call, we want the option value to increase; if we sell a put/call, we want the option value
        to decrease.

        :return: Profit / loss as a percentage of the initial option prices.  Returns negative percentage for a loss.
        """

        # Handle profit / loss for put first.
        putOpt = self.__putOpt
        putProfitLoss = putOpt.calcOptionPriceDiff()

        # If we're buying the strangle, we will have a loss if the put option decreases in value.
        if self.__buyOrSell == "BUY":
            putProfitLoss = -putProfitLoss

        # Handle profit /loss for call next.
        callOpt = self.__callOpt
        callProfitLoss = callOpt.calcOptionPriceDiff()

        if self.__buyOrSell == "BUY":
            callProfitLoss = -callProfitLoss

        # Add the profit / loss of put and call.
        totProfitLoss = putProfitLoss + callProfitLoss

        # Get the initial credit or debit paid for selling or buying the strangle, respectively.
        callCreditDebit = callOpt.getTradePrice()
        putCreditDebit = putOpt.getTradePrice()
        totCreditDebit = (callCreditDebit + putCreditDebit) * 100

        # Express totProfitLoss as a percentage.
        # 5.00 -> 2.50 when selling strangle, profit / loss = (5 - 2.50) / 5 = 2.5/5 = 0.5 * 100 = 50
        # 5.00 -> 10.00 when buying strangle, profit / loss = -(5 - 10) / 5 = 1 * 100 = 100
        percentProfitLoss = (totProfitLoss / totCreditDebit) * 100

        return percentProfitLoss

    def getNumContracts(self):
        """This function returns the number of contracts for the overall
        primitive.
        For this particular class, we are dealing with strangles, so it
        will return the total number of strangles."""
        return self.__numContracts

    def getBuyingPower(self):
        """The formula for calculating buying power is based off of TastyWorks.  This is for cash settled indices!
        There are two possible methods to calculate buying power, and the method which
        generates the maximum possible buying power is the one chosen.

        :return: Amount of buying power required to put on the trade.
        """

        # Method 1 - 25% rule -- 25% of the underlying, less the difference between the strike price and the stock
        # price, plus the option value, multiplied by number of contracts.
        # Use one of the options to get underlying price (put option).
        underlyingPrice = self.__callOpt.getUnderlyingPrice()

        # Handle call side of strangle.
        callStrikePrice = self.__callOpt.getStrikePrice()
        # Assumes that current option price is the mid price.
        currentCallPrice = (self.__callOpt.getBidPrice() + self.__callOpt.getAskPrice()) / 2
        callBuyingPower1 = ((0.25*underlyingPrice)-(callStrikePrice - underlyingPrice) + currentCallPrice) * \
                           (self.__numContracts*100)

        # Handle put side of strangle.
        putStrikePrice = self.__putOpt.getStrikePrice()
        currentPutPrice = (self.__putOpt.getBidPrice() + self.__putOpt.getAskPrice()) / 2
        putBuyingPower1 = ((0.25 * underlyingPrice)-(underlyingPrice - putStrikePrice) + currentPutPrice) * \
                          (self.__numContracts*100)

        # Decide which side requires more buying power; if both sides require same buying power, use the premium
        # from the side which has a higher option price (more premium).
        if putBuyingPower1 > callBuyingPower1:
            methodOneBuyingPower = putBuyingPower1 + currentCallPrice * self.__numContracts * 100
        elif callBuyingPower1 > putBuyingPower1:
            methodOneBuyingPower = callBuyingPower1 + currentPutPrice * self.__numContracts * 100
        else:
            if currentCallPrice > currentPutPrice:
                premiumToUse = currentCallPrice
            else:
                premiumToUse = currentPutPrice

            methodOneBuyingPower = callBuyingPower1 + premiumToUse * self.__numContracts * 100

        # Method 2 - 15% rule -- 15% of the exercise value plus premium value.

        # Handle call side of strangle.
        callBuyingPower2 = (0.15 * callStrikePrice + currentCallPrice) * self.__numContracts * 100

        # Handle put side of strangle.
        putBuyingPower2 = (0.15 * putStrikePrice + currentPutPrice) * self.__numContracts * 100

        # Decide which side requires more buying power; if both sides require same buying power, use the premium
        # from the side which has a higher option price (more premium).
        if putBuyingPower2 > callBuyingPower2:
            methodTwoBuyingPower = putBuyingPower2 + currentCallPrice * self.__numContracts * 100
        elif callBuyingPower2 > putBuyingPower2:
            methodTwoBuyingPower = callBuyingPower2 + currentPutPrice * self.__numContracts * 100
        else:
            if currentCallPrice > currentPutPrice:
                premiumToUse = currentCallPrice
            else:
                premiumToUse = currentPutPrice

            methodTwoBuyingPower = callBuyingPower2 + premiumToUse * self.__numContracts * 100

        # Return the highest buying power from the two methods.
        return max(methodOneBuyingPower, methodTwoBuyingPower)

    def updateValues(self, tickData):
        """Based on the latest pricing data, update the option values for the strangle.
        :param tickData: option chain with pricing information (puts, calls)
        :return True if we were able to update values, false otherwise.
        """

        # Work with put option first.
        putOpt = self.__putOpt

        # Get put option symbol.
        putOptSymbol = putOpt.getOptionSymbol()

        # Get put strike.
        putStrike = putOpt.getStrikePrice()

        # Get option expiration date / time.
        putExpiration = putOpt.getDTE()

        # Go through the tickData to find the PUT option with a strike price that matches the putStrike above.
        # Note that this should not return more than one option since we specify the strike price, expiration,
        # option type (PUT), and option symbol.
        # TODO:  can we do this search faster?
        matchingPutOption = None
        for option in tickData:
            if (option.getStrikePrice() == putStrike and option.getOptionType() == 'PUT'
                    and option.getDTE() == putExpiration and option.getOptionSymbol() == putOptSymbol):
                matchingPutOption = option
                break

        if not matchingPutOption:
            logging.warning("No matching PUT was found in the option chain for the strangle.")

        # Work with call option.
        callOpt = self.__callOpt

        # Get call option symbol.
        callOptSymbol = callOpt.getOptionSymbol()

        # Get call strike.
        callStrike = callOpt.getStrikePrice()

        # Get option expiration date / time.
        callExpiration = callOpt.getDTE()

        # Go through the tickData to find the CALL option with a strike price that matches the callStrike above
        # Note that this should not return more than one option since we specify the strike price, expiration,
        # the option type (CALL), and option symbol.
        matchingCallOption = None
        for option in tickData:
            if (option.getStrikePrice() == callStrike and option.getOptionType() == 'CALL'
                    and option.getDTE() == callExpiration and option.getOptionSymbol() == callOptSymbol):
                matchingCallOption = option
                break

        if not matchingCallOption:
            logging.warning("No matching CALL was found in the option chain for the strangle.")

        # If we were able to find an update for both the put and call option, we update option intrinsics.
        if matchingCallOption and matchingPutOption:
            # Update option intrinsics
            putOpt.updateIntrinsics(matchingPutOption)
            callOpt.updateIntrinsics(matchingCallOption)
            return True
        else:
            # Can't update the position we have on; need to exit strangle.
            self.__forceClose = True
            return False

    def managePosition(self):
        """Using the criteria in the optional class attributes:
           daysBeforeClosing:  Number of days before expiration to close the trade.
           profitTargetPercent:  Percentage of initial credit to use when closing trade.
           customManagement:  boolean -- manages trade using defined rules.

        :return: True if position should be removed; False otherwise.
        """

        putOpt = self.__putOpt
        callOpt = self.__callOpt

        if not putOpt or not callOpt:
            logging.warning("Could not manage position since put or call option in the strangle had a None type.")
            return False

        # If we weren't able to update the current position since there was no matching tick data, we need to exit
        # the trade.
        if self.__forceClose:
            # Reset the forceClose attribute
            self.__forceClose = False
            return True

        if self.getProfitTargetPercent():

            target = self.getProfitTargetPercent()

            # Work with put option first.
            putOptCurPrice = (putOpt.getBidPrice() + putOpt.getAskPrice())/2.0
            putOptTradePrice = putOpt.getTradePrice()

            # Work with call option next.
            callOptCurPrice = (callOpt.getBidPrice() + callOpt.getAskPrice()) / 2.0
            callOptTradePrice = callOpt.getTradePrice()

            if self.__buyOrSell == "SELL":
                if putOptCurPrice + callOptCurPrice <= target*(putOptTradePrice + callOptTradePrice):
                    return True
            else:
                if putOptCurPrice + callOptCurPrice >= (1+target)*(putOptTradePrice + callOptTradePrice):
                    return True

        if self.getDaysBeforeClosing():

            # Get the difference in time between current date / time and the option expiration date.
            daysBeforeClosing = self.getDaysBeforeClosing()

            # Get difference between current date and option expiration date in days for put and call option.
            putDays = putOpt.getNumDaysLeft()
            callDays = callOpt.getNumDaysLeft()

            # If either the put option or call option has less days to expiration than the daysBeforeClosing threshold,
            # we will return True to close out the strangle position.
            # TODO: We may want to adjust this behavior later if we'd like to be able to have a strange with a call
            # and put option in different expirations.
            if putDays <= daysBeforeClosing or callDays <= daysBeforeClosing:
                return True

        if self.getCustomManagementFlag():
            pass
            # Example of custom management which closes out 3x losers.
            # if self.calcProfitLossPercentage() <= -300:
            #    return True

        return False