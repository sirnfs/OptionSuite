import option

class Call(option.Option):
    """This class defines a CALL option, which inherits from the Option class"""
    def __init__(self, underlyingTicker, strikePrice, delta, DTE, longOrShort=None, underlyingPrice=None,
                 optionSymbol=None, optionAlias=None, bidPrice=None, askPrice=None, openInterest=None,
                 volume=None, dateTime=None, theta=None, gamma=None, rho=None, vega=None, impliedVol=None,
                 exchangeCode=None, exercisePrice=None, assignPrice=None, openCost=None, closeCost=None, tradeID=None):

        __optionType = "CALL"

        option.Option.__init__(self, underlyingTicker, strikePrice, __optionType, delta, DTE, longOrShort,
                               underlyingPrice, optionSymbol, optionAlias, bidPrice, askPrice, openInterest,
                               volume, dateTime, theta, gamma, rho, vega, impliedVol, exchangeCode, exercisePrice,
                               assignPrice, openCost, closeCost, tradeID)



    #def getUnderlyingTicker(self):

    #    return self.getUnderlyingTicker()


    #def getStrikePrice(self):
    #    return self.getStrikePrice()
