
class Stock(object):
    """This class defines one the basic types for the backtester or live trader -- a stock.

     Attributes:
       underlyingPrice:  price of the underlying / stock which has option derivatives in dollars.
       underlyingTicker:  ticker symbol (e.g., SPY) of underlying.
       longOrShort:  indicates if we are long or short the stock; 'Long' = long and 'Short' = short.
       bidPrice:  current bid price of option.
       askPrice:  current asking price of option.
       tradePrice:  price of stock when order was executed.
       openInterest:  number of open option contracts.
       volume:  number of contracts traded.
       dateTime:  data / time of quote recieved; would also be data / time bought / sold.
       exchangeCode:  symbol used to denote which exchanged used or where quote came from.
       openCost:  cost to open the option trade.
       closeCost:  cost to close out the option trade.
     """

    def __init__(self, underlyingTicker, longOrShort, underlyingPrice=None, bidPrice=None,
                 askPrice=None, tradePrice=None, openInterest=None, volume=None, dateTime=None, exchangeCode=None,
                 openCost=None, closeCost=None):
        """Inits Stock class with constructor data."""

        self.__underlyingPrice = underlyingPrice
        self.__underlyingTicker = underlyingTicker
        self.__longOrShort = longOrShort
        self.__bidPrice = bidPrice
        self.__askPrice = askPrice
        self.__tradePrice = tradePrice
        self.__openInterest = openInterest
        self.__volume = volume
        self.__dateTime = dateTime
        self.__exchangeCode = exchangeCode
        self.__openCost = openCost
        self.__closeCost = closeCost

    def getUnderlyingPrice(self):
        return self.__underlyingPrice

    def getUnderlyingTicker(self):
        return self.__underlyingTicker

    def getLongOrShort(self):
        return self.__longOrShort

    def getBidPrice(self):
        return self.__bidPrice

    def getAskPrice(self):
        return self.__askPrice

    def getTradePrice(self):
        return self.__tradePrice

    def getOpenInterest(self):
        return self.__openInterest

    def getOptionVolume(self):
        return self.__volume

    def getDateTime(self):
        return self.__dateTime

    def getExchangeCode(self):
        return self.__exchangeCode

    def getOpenCost(self):
        return self.__openCost

    def getCloseCost(self):
        return self.__closeCost

