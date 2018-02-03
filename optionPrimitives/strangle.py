from optionPrimitive import OptionPrimitive
import logging

class Strangle(OptionPrimitive):
    """This class sets up the strangle option primitive
           
        Attributes:
           orderQuantity:  number of strangles
           callOpt:  call option
           putOpt:  put option
           buyOrSell:  indicates if we want to buy or sell the strangle ("BUY" or "SELL")

        Optional attributes:
           daysBeforeClosing:  number of days before expiration to close the trade
           roc:  minimal return on capital for overall trade as a decimal
           profitTargetPercent:  percentage of initial credit to use when closing trade
           avoidAssignment:  boolean -- closes out trade using defined rules to avoid stock assignment
           maxBidAsk:  maximum price to allow between bid and ask prices of option (for any strike or put/call)
           maxMidDev:  maximum deviation from midprice on opening and closing of trade (e.g., 0.02 cents from midprice)
    """
    def __init__(self, orderQuantity, callOpt, putOpt, buyOrSell, daysBeforeClosing=None, roc=None,
                 profitTargetPercent=None, avoidAssignment=None, maxBidAsk=None, maxMidDev=None):

        self.__numContracts = orderQuantity
        self.__putOpt = putOpt
        self.__callOpt = callOpt
        self.__buyOrSell = buyOrSell
        self.__daysBeforeClosing = daysBeforeClosing
        self.__roc = roc
        self.__profitTargetPercent = profitTargetPercent
        self.__avoidAssignment = avoidAssignment
        self.__maxBidAsk = maxBidAsk
        self.__maxMidDev = maxMidDev

        # TODO?? Should we do this?  if orderQuantity > 1, duplicate call and put options; we'd like to have
        # orderQuantity number of calls and puts

    def addPrimitive(self):
        pass

    def removePrimitive(self):
        pass

    def getDelta(self):
        """Used to get the delta for the strangle
        """
        if self.__putOpt.getDelta() and self.__putOpt.getDelta():
            totPutDelta = self.__numContracts*self.__putOpt.getDelta()
            totCallDelta = self.__numContracts*self.__callOpt.getDelta()

            return (totCallDelta + totPutDelta)
        else:
            return None

    def getVega(self):
        """Used to get the vega for the strangle
        """
        if self.__putOpt.getVega() and self.__callOpt.getVega():
            totPutVega = self.__numContracts * self.__putOpt.getVega()
            totCallVega = self.__numContracts * self.__callOpt.getVega()

            return (totCallVega + totPutVega)
        else:
            return None

    def getTheta(self):
        """Used to get the theta for the strangle
        """
        if self.__putOpt.getTheta() and self.__callOpt.getTheta():
            totPutTheta = self.__numContracts * self.__putOpt.getTheta()
            totCallTheta = self.__numContracts * self.__callOpt.getTheta()

            return (totCallTheta + totPutTheta)
        else:
            return None

    def getGamma(self):
        """Used to get the gamma for the strangle
        """
        if self.__putOpt.getGamma() and self.__callOpt.getGamma():
            totPutGamma = self.__numContracts * self.__putOpt.getGamma()
            totCallGamma = self.__numContracts * self.__callOpt.getGamma()

            return (totCallGamma + totPutGamma)
        else:
            return None

    def calcProfitLoss(self):
        """Calculate the profit and loss for the strangle position based on option values when the trade
        was placed and new option values.  Note that profit and loss are reversed if we buy or sell a put/call;
        if we buy a put/call, we want the option value to increase; if we sell a put/call, we want the option value
        to decrease.

        :return: profit / loss (positive decimal for profit, negative decimal for loss)
        """

        # Handle profit / loss for put first
        putOpt = self.__putOpt
        putProfitLoss = putOpt.calcOptionPriceDiff()

        # If we're buying the strangle, we will have a loss if the put option decreases in value
        if self.__buyOrSell == "BUY":
            putProfitLoss = -putProfitLoss

        # Handle profit /loss for call second
        callOpt = self.__callOpt
        callProfitLoss = callOpt.calcOptionPriceDiff()

        if self.__buyOrSell == "BUY":
            callProfitLoss = -callProfitLoss

        # Add the profit / loss of put and call, and multiply by the number of contracts
        totProfitLoss = (putProfitLoss + callProfitLoss) * self.__numContracts

        return totProfitLoss

    def getNumContracts(self):
        """This function returns the number of contracts for the overall
        primitive.
        For this particular class, we are dealing with strangles, so it
        will return the total number of strangles"""
        return self.__numContracts

    def getBuyingPower(self):
        """The formula for calculating buying power is based off of Tastyworks.  This is for cash settled indices!
        There are two possible methods to calculate buying power, and the method which
        generates the maximum possible buying power is the one chosen

        :return: amount of buying power required to put on the trade
        """

        # Method 1 - 25% rule -- 25% of the underlying, less the difference between the strike price and the stock
        # price, plus the option value, multiplied by number of contracts.
        # Use one of the options to get underlying price (put option)
        underlyingPrice = self.__callOpt.getUnderlyingPrice()

        # Handle call side of strangle
        callStrikePrice = self.__callOpt.getStrikePrice()
        # Assumes that current option price is the mid price.
        currentCallPrice = (self.__callOpt.getBidPrice() + self.__callOpt.getAskPrice()) / 2
        callBuyingPower1 = ((0.25*underlyingPrice)-(callStrikePrice - underlyingPrice) + currentCallPrice) * \
                           (self.__numContracts*100)

        # Handle put side of strangle
        putStrikePrice = self.__putOpt.getStrikePrice()
        currentPutPrice = (self.__putOpt.getBidPrice() + self.__putOpt.getAskPrice()) / 2
        putBuyingPower1 = ((0.25 * underlyingPrice)-(underlyingPrice - putStrikePrice) + currentPutPrice) * \
                          (self.__numContracts*100)

        # Decide which side requires more buying power; if both sides require same buying power, use the premium
        # from the side which has a higher option price (more premium)
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

        # Handle call side of strangle
        callBuyingPower2 = (0.15 * callStrikePrice + currentCallPrice) * self.__numContracts * 100

        # Handle put side of strangle
        putBuyingPower2 = (0.15 * putStrikePrice + currentPutPrice) * self.__numContracts * 100

        # Decide which side requires more buying power; if both sides require same buying power, use the premium
        # from the side which has a higher option price (more premium)
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

        # Return the highest buying power from the two methods
        return max(methodOneBuyingPower, methodTwoBuyingPower)

    def updateValues(self, tickData):
        """Based on the latest pricing data, update the option values for the strangle
        :param tickData: option chain with pricing information (puts, calls)
        """

        # TODO:  can we do this search faster?
        # Work with put option first
        putOpt = self.__putOpt

        # Get put strike
        putStrike = putOpt.getStrikePrice()

        # Get option expiration date / time
        putExpiration = putOpt.getDTE()

        # Go through the tickData to find the PUT option with a strike price that matches the putStrike above
        # Note that this should not return more than one option since we specify the strike price, expiration, and
        # the option type (PUT)
        matchingPutOption = None
        for option in tickData:
            if (option.getStrikePrice() == putStrike and option.getOptionType() == 'PUT'
                    and option.getDTE() == putExpiration):
                matchingPutOption = option
                break

        if not matchingPutOption:
            logging.warning("No matching PUT was found in the option chain for the strangle")
        else:
            # Update option intrinsics
            putOpt.updateIntrinsics(matchingPutOption)

        # Work with call option
        callOpt = self.__callOpt

        # Get call strike
        callStrike = callOpt.getStrikePrice()

        # Get option expiration date / time
        callExpiration = callOpt.getDTE()

        # Go through the tickData to find the CALL option with a strike price that matches the callStrike above
        # Note that this should not return more than one option since we specify the strike price, expiration, and
        # the option type (CALL)
        matchingCallOption = None
        for option in tickData:
            if (option.getStrikePrice() == callStrike and option.getOptionType() == 'CALL'
                    and option.getDTE() == callExpiration):
                matchingCallOption = option
                break

        if not matchingCallOption:
            logging.warning("No matching CALL was found in the option chain for the strangle")
        else:
            # Update option intrinsics
            callOpt.updateIntrinsics(matchingCallOption)

