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
           maxBuyingPower:  maximum buying power to use on overall trade
           profitTargetPercent:  percentage of initial credit to use when closing trade
           avoidAssignment:  boolean -- closes out trade using defined rules to avoid stock assignment
           maxBidAsk:  maximum price to allow between bid and ask prices of option (for any strike or put/call)
           maxMidDev:  maximum deviation from midprice on opening and closing of trade (e.g., 0.02 cents from midprice)
    """
    def __init__(self, orderQuantity, callOpt, putOpt, daysBeforeClosing, roc=None, maxBuyingPower=None,
                 profitTargetPercent=None, avoidAssignment=None, maxBidAsk=None, maxMidDev=None):

        self.__numContracts = orderQuantity
        self.__putOpt = putOpt
        self.__callOpt = callOpt
        self.__daysBeforeClosing = daysBeforeClosing
        self.__roc = roc
        self.__maxBuyingPower = maxBuyingPower
        self.__profitTargetPercent = profitTargetPercent
        self.__avoidAssignment = avoidAssignment
        self.__maxBidAsk = maxBidAsk
        self.__maxMidDev = maxMidDev

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


