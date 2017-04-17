
class Stock(object):
    """This class defines one the basic types for the backtester or live trader -- a stock.  
    
     A stock has the following internals
     -Underlying price
     -Underlying ticker symbol
     -Buy/Sell (long/short) -- binary value
     -Bid price
     -Ask price
     -Open interest
     -Volume
     -Quote Date / Time
     -Exchange Code
     -Cost to open
     -Cost to close
     -Trade ID:  used to keep track of trade / may not be needed

     Attributes:
       underlyingPrice:  price of the underlying / stock which has option derivatives in dollars
       underlyingTicker:  ticker symbol (e.g., SPY) of underlying
       longOrShort:  indicates if we are long or short the stock; 'Long' = long and 'Short' = short
       bidPrice:  current bid price of option
       askPrice:  current asking price of option
       openInterest:  number of open option contracts
       volume:  number of contracts traded
       dateTime:  data / time of quote recieved; would also be data / time bought / sold
       exchangeCode:  symbol used to denote which exchanged used or where quote came from
       openCost:  cost to open the option trade
       closeCost:  cost to close out the option trade
       tradeID:  used to keep track of the trade that was put on so we can reference it later
                 the tradeID is associated with both the strategy and the options in the strategy
     """

    def __init__(self, underlyingTicker, longOrShort, underlyingPrice=None, bidPrice=None,
                 askPrice=None, openInterest=None, volume=None, dateTime=None, exchangeCode=None,
                 openCost=None, closeCost=None, tradeID=None):
        """Inits Stock class with constructor data."""

        self.__underlyingPrice = underlyingPrice
        self.__underlyingTicker = underlyingTicker
        self.__longOrShort = longOrShort
        self.__bidPrice = bidPrice
        self.__askPrice = askPrice
        self.__openInterest = openInterest
        self.__volume = volume
        self.__dateTime = dateTime
        self.__exchangeCode = exchangeCode
        self.__openCost = openCost
        self.__closeCost = closeCost
        self.__tradeID = tradeID

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

    def getTradeID(self):
        return self.__tradeID

