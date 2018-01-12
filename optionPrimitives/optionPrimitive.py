from abc import ABCMeta, abstractmethod

class OptionPrimitive(object):
    """This class is a generic type for any primitive that can be made using
       a PUT or CALL option and/or stock, e.g., iron condor or strangle
       Since the primitive is often created prior to having historical data or
       live data, many of the Option fields will be blank until the trade
       is executed
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def getBuyingPower(self):
        """Used to calculate the buying power needed for the
        option primitive
        """
        pass

    @abstractmethod
    def addPrimitive(self):
        """Used to add the strategy to the order book
           This is not closing out an order, and it can
           only be used if the strategy hasn't been executed
           This will probably need to add the strategy to the
           database
        """
        pass

    @abstractmethod
    def removePrimitive(self):
        """Used to remove the strategy from order book
           This is not closing out an order, and it can
           only be used if the strategy hasn't been executed
           Is this needed here?  We will probably need to save the
           strategy to a database, and we can probably remove it
           through a different module.  
        """
        pass
