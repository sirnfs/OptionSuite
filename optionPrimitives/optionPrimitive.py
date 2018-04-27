from abc import ABCMeta, abstractmethod

class OptionPrimitive(object):
    """This class is a generic type for any primitive that can be made using
       a PUT or CALL option and/or stock, e.g., iron condor or strangle.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def getUnderlyingTicker(self):
        """Get the name (string) of the underlying being used for the option primitive.
        """
        pass

    @abstractmethod
    def getBuyingPower(self):
        """Used to calculate the buying power needed for the
        option primitive.
        """
        pass

    @abstractmethod
    def getDelta(self):
        """Used to get the delta for the option primitive.
        """
        pass

    @abstractmethod
    def getVega(self):
        """Used to get the vega for the option primitive.
        """
        pass

    @abstractmethod
    def getTheta(self):
        """Used to get the theta for the option primitive.
        """
        pass

    @abstractmethod
    def getGamma(self):
        """Used to get the gamma for the option primitive.
        """
        pass

    @abstractmethod
    def calcProfitLoss(self):
        """Calculate the profit and loss for the option primitive based on option values when the trade
        was placed and new option values.

        :return: Profit / loss (positive decimal for profit, negative decimal for loss).
        """
        pass

    @abstractmethod
    def calcProfitLossPercentage(self):
        """Calculate the profit and loss for the option primitive based on option values when the trade
        was placed and new option values.

        :return: Profit / loss as a percentage of the initial option prices.  Returns negative percentage for a loss.
        """
        pass

    @abstractmethod
    def updateValues(self, tickData):
        """Based on the latest pricing data, update the option values.
        :param tickData: option chain with pricing information.
        :return True if we were able to update values, false otherwise.
        """
        pass
