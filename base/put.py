import option

class Put(option.Option):
    """This class defines a PUT option, which inherits from the Option class"""
    def __init__(self, underlyingTicker, strikePrice, delta, DTE, longOrShort=None, underlyingPrice=None,
                 underlyingTradePrice=None, optionSymbol=None, optionAlias=None, bidPrice=None, askPrice=None,
                 tradePrice=None, openInterest=None, volume=None, dateTime=None, theta=None, gamma=None, rho=None,
                 vega=None, impliedVol=None, exchangeCode=None, exercisePrice=None, assignPrice=None, openCost=None,
                 closeCost=None, tradeID=None):

        __optionType = "PUT"

        option.Option.__init__(self, underlyingTicker, strikePrice, __optionType, delta, DTE, longOrShort,
                               underlyingPrice, underlyingTradePrice, optionSymbol, optionAlias, bidPrice, askPrice,
                               tradePrice, openInterest, volume, dateTime, theta, gamma, rho, vega, impliedVol,
                               exchangeCode, exercisePrice, assignPrice, openCost, closeCost, tradeID)
