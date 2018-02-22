from base import put
from optionPrimitive import OptionPrimitive

class NakedPut(OptionPrimitive):

    def __init__(self, underlyingTicker, strikePrice, longOrShort, delta, DTE, numContracts, underlyingPrice=None,
                 bidPrice=None, askPrice=None):

        self.__numContracts = numContracts
        self.__primitiveElems = []

        #Create multiple objects of class Put
        for i in range(self.__numContracts):
             self.__primitiveElems.append(put.Put(underlyingTicker, strikePrice,
                                          longOrShort, delta, DTE, underlyingPrice=underlyingPrice, bidPrice=bidPrice,
                                                  askPrice=askPrice))

    def addPrimitive(self):
        pass

    def removePrimitive(self):
        pass

    def getUnderlyingTicker(self):
        """Get the name (string) of the underlying being used for the naked put
        """
        pass

    def getDelta(self):
        """Used to get the delta for the strangle
        """
        pass

    def getVega(self):
        """Used to get the vega for the strangle
        """
        pass

    def getTheta(self):
        """Used to get the theta for the strangle
        """
        pass

    def getGamma(self):
        """Used to get the gamma for the strangle
        """
        pass

    def calcProfitLoss(self):
        """Calculate the profit and loss for the naked put position based on option values when the trade
        was placed and new option values

        :return: profit / loss (positive decimal for profit, negative decimal for loss)
        """
        pass

    def calcProfitLossPercentage(self):
        """Calculate the profit and loss for the naked put position based on option values when the trade
        was placed and new option values.  Note that profit and loss are reversed if we buy or sell a put;
        if we buy a put, we want the option value to increase; if we sell a put, we want the option value
        to decrease.

        :return: profit / loss as a percentage of the initial option price.  Returns negative percentage for a loss
        """
        pass

    def getNumContracts(self):
        """This function returns the number of contracts for the overall
        primitive, and it should not confused with the number of option 
        contracts; e.g., number of iron condors or number of strangles.
        For this particular class, we are only dealing with puts, so it
        will return the number of put contracts"""
        return self.__numContracts

    def getPrimitiveElements(self):
        """This function returns the array which contains all of the
        options making up a primitive"""
        return self.__primitiveElems

    def getBuyingPower(self):
        """The formula for calculating buying power is based off of Tastyworks.  This is for cash settled indices!
           There are two possible methods to calculate buying power, and the method which
           generates the maximum possible buying power is the one chosen

           :return: amount of buying power required to put on the trade
        """

        # Method 1 - 25% rule -- 25% of the underlying, less the difference between the strike price and the stock
        # price, plus the option value, multiplied by number of contracts.
        underlyingPrice = self.__primitiveElems[0].getUnderlyingPrice()

        putStrikePrice = self.__primitiveElems[0].getStrikePrice()
        currentPutPrice = (self.__primitiveElems[0].getBidPrice() + self.__primitiveElems[0].getAskPrice()) / 2
        putBuyingPower1 = ((0.2 * underlyingPrice) - (underlyingPrice - putStrikePrice) + currentPutPrice) * \
                          (self.__numContracts * 100)

        # Method 2 - 15% rule -- 15% of the exercise value plus premium value.
        putBuyingPower2 = (0.1 * putStrikePrice + currentPutPrice) * self.__numContracts * 100

        # Return the highest buying power from the two methods
        return max(putBuyingPower1, putBuyingPower2)

    def updateValues(self, tickData):
        """Based on the latest pricing data, update the option values for the naked put
        :param tickData: option chain with pricing information (puts, calls)
         :return True if we were able to update values, false otherwise.
        """
        pass