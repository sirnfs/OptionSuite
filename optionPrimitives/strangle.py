from base import put
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
    def __init__(self, underlying, delta,
                 DTE, orderQuantity, buyOrSell):

        self.__numContracts = orderQuantity

        self.__primitiveElems = []

        #TODO:  need to specify delta for put or call and not strike price

        #Create multiple objects of class Put and class Call
        #for i in range(self.__numContracts):
        #     self.__primitiveElems.append(put.Put(underlying, strikePrice,
        #                                  longOrShort, delta, DTE))

    def addPrimitive(self):
        pass

    def removePrimitive(self):
        pass

    def getNumContracts(self):
        """This function returns the number of contracts for the overall
        primitive, and it should not confused with the number of option 
        contracts; e.g., number of strangles.
        For this particular class, we are only dealing with puts, so it
        will return the number of put contracts"""
        return self.__numContracts

    def getPrimitiveElements(self):
        """This function returns the array which contains all of the
        options making up a primitive"""
        return self.__primitiveElems
