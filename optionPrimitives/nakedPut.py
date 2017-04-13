from base import put
from optionPrimitive import OptionPrimitive

class NakedPut(OptionPrimitive):

    def __init__(self, underlyingTicker, strikePrice, longOrShort, delta, DTE, numContracts):

        self.__numContracts = numContracts

        self.__primitiveElems = []

        #Create multiple objects of class Put
        for i in range(self.__numContracts):
             self.__primitiveElems.append(put.Put(underlyingTicker, strikePrice,
                                          longOrShort, delta, DTE))

    def addPrimitive(self):
        pass

    def removePrimitive(self):
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
