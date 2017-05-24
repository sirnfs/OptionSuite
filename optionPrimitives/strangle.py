from base import put
from optionPrimitive import OptionPrimitive

class Strangle(OptionPrimitive):
    """This class sets up the strangle option primitive
           
        Other attributes which must be provided:
           buyOrSell:  do we buy a strangle or sell a strangle?
           underlying:  which underlying to use for the strategy
           orderQuantity:  number of strangles, iron condors, etc
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
