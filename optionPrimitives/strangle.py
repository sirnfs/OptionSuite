from optionPrimitive import OptionPrimitive

class Strangle(OptionPrimitive):
    """This class sets up the strangle option primitive
           
        Attributes:
           orderQuantity:  number of strangles
           callOpt:  call option
           putOpt:  put option
           daysBeforeClosing:  number of days before expiration to close the trade

        Optional attributes:
           roc:  minimal return on capital for overall trade as a decimal
           profitTargetPercent:  percentage of initial credit to use when closing trade
           avoidAssignment:  boolean -- closes out trade using defined rules to avoid stock assignment
           maxBidAsk:  maximum price to allow between bid and ask prices of option (for any strike or put/call)
           maxMidDev:  maximum deviation from midprice on opening and closing of trade (e.g., 0.02 cents from midprice)
    """
    def __init__(self, orderQuantity, callOpt, putOpt, daysBeforeClosing, roc=None, profitTargetPercent=None,
                 avoidAssignment=None, maxBidAsk=None, maxMidDev=None):

        self.__numContracts = orderQuantity
        self.__putOpt = putOpt
        self.__callOpt = callOpt
        self.__daysBeforeClosing = daysBeforeClosing
        self.__roc = roc
        self.__profitTargetPercent = profitTargetPercent
        self.__avoidAssignment = avoidAssignment
        self.__maxBidAsk = maxBidAsk
        self.__maxMidDev = maxMidDev
        self.__profitLoss = 0

    def addPrimitive(self):
        pass

    def removePrimitive(self):
        pass

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


