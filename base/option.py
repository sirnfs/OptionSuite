
class Option(object):
    """This class defines the basic type for the backtester or live trader -- an option.
    Other classes such as put or call are derived from this class.

     Attributes:
       underlyingPrice:  price of the underlying / stock which has option derivatives in dollars.
       underlyingTradePrice:  price of underlying at the time the trade was placed.
       underlyingTicker:  ticker symbol (e.g., SPY) of underlying.
       optionSymbol:  code different than the underlying ticker used to denote option.
       optionAlias:  old code used to denote option if it changed; usually blank.
       strikePrice:  strike price of option.
       optionType:  put or call.
       longOrShort:  indicates if we are long or short the option; 'Long' = long and 'Short' = short.
       bidPrice:  current bid price of option.
       askPrice:  current asking price of option.
       tradePrice:  price of option when trade was executed / put on.
       openInterest:  number of open option contracts.
       volume:  number of contracts traded.
       dateTime:  data / time of quote received; would also be data / time bought / sold.
       delta:  greek for quantifying percent of stock we're long or short (-1 to 1).
       theta:  daily return in dollars if no movement in underlying price.
       gamma:  describes rate of change of delta (float).
       rho:  how much option price changes with change in interest rate (dollars).
       vega:  change in price of option for every 1% change in volatility.
       impliedVol:  implied volatility percentage.
       DTE:  days to expiration of option.
       exchangeCode:  symbol used to denote which exchanged used or where quote came from.
       exercisePrice:  price to exercise option early.
       assignPrice:  price you must pay if other party exercises option.
       openCost:  cost to open the option trade.
       closeCost:  cost to close out the option trade.
     """

    def __init__(self, underlyingTicker, strikePrice, optionType, delta, DTE, longOrShort=None,
                 underlyingPrice=None, underlyingTradePrice=None, optionSymbol=None, optionAlias=None, bidPrice=None,
                 askPrice=None, tradePrice=None, openInterest=None, volume=None, dateTime=None, theta=None,
                 gamma=None, rho=None, vega=None, impliedVol=None, exchangeCode=None,
                 exercisePrice=None, assignPrice=None, openCost=None, closeCost=None):
        """Initializes Option class with constructor data.  We check to make sure that
        the user doesn't try to instantiate the Option class."""

        if self.__class__ == Option:
            raise NotImplementedError, "Cannot create object of class Option; must use PUT or CALL " \
                                       "classes"

        self.__underlyingPrice = underlyingPrice
        self.__underlyingTradePrice = underlyingTradePrice
        self.__underlyingTicker = underlyingTicker
        self.__optionSymbol = optionSymbol
        self.__optionAlias = optionAlias
        self.__strikePrice = strikePrice
        self.__optionType = optionType
        self.__longOrShort = longOrShort
        self.__bidPrice = bidPrice
        self.__askPrice = askPrice
        self.__tradePrice = tradePrice
        self.__openInterest = openInterest
        self.__volume = volume
        self.__dateTime = dateTime
        self.__delta = delta
        self.__theta = theta
        self.__gamma = gamma
        self.__rho = rho
        self.__vega = vega
        self.__impliedVol = impliedVol
        self.__DTE = DTE
        self.__exchangeCode = exchangeCode
        self.__exercisePrice = exercisePrice
        self.__assignPrice = assignPrice
        self.__openCost = openCost
        self.__closeCost = closeCost

    # Getters
    def getUnderlyingPrice(self):
        return self.__underlyingPrice

    def getUnderlyingTradePrice(self):
        return self.__underlyingTradePrice

    def getUnderlyingTicker(self):
        return self.__underlyingTicker

    def getOptionSymbol(self):
        return self.__optionSymbol

    def getOptionAlias(self):
        return self.__optionAlias

    def getStrikePrice(self):
        return self.__strikePrice

    def getOptionType(self):
        return self.__optionType

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

    def getDelta(self):
        return self.__delta

    def getTheta(self):
        return self.__theta

    def getGamma(self):
        return self.__gamma

    def getRho(self):
        return self.__rho

    def getVega(self):
        return self.__vega

    def getImpliedVol(self):
        return self.__impliedVol

    def getDTE(self):
        return self.__DTE

    def getExchangeCode(self):
        return self.__exchangeCode

    def getExercisePrice(self):
        return self.__exercisePrice

    def getAssignPrice(self):
        return self.__assignPrice

    def getOpenCost(self):
        return self.__openCost

    def getCloseCost(self):
        return self.__closeCost

    # Setters
    def setUnderlyingPrice(self, underlyingPrice):
        self.__underlyingPrice = underlyingPrice

    def setBidPrice(self, bidPrice):
        self.__bidPrice = bidPrice

    def setAskPrice(self, askPrice):
        self.__askPrice = askPrice

    def setOpenInterest(self, openInterest):
        self.__openInterest = openInterest

    def setOptionVolume(self, optionVolume):
        self.__volume = optionVolume

    def setDateTime(self, dateTime):
        self.__dateTime = dateTime

    def setDelta(self, delta):
        self.__delta = delta

    def setTheta(self, theta):
        self.__theta = theta

    def setGamma(self, gamma):
        self.__gamma = gamma

    def setRho(self, rho):
        self.__rho = rho

    def setVega(self, vega):
        self.__vega = vega

    def setImpliedVol(self, impliedVol):
        self.__impliedVol = impliedVol

    # Calculations
    def calcOptionPriceDiff(self):
        """Calculate the difference in price of the put when the trade was placed versus its current value.
        Specifically, diff = original price - current price.  The current price used is actually the mid price, or
        the average of the bid price and ask price.

        :return: price difference (original price - current price).
        """
        midPrice = (self.getBidPrice() + self.getAskPrice())/2.0
        return (self.getTradePrice() - midPrice) * 100

    def getNumDaysLeft(self):
        '''
        Determine the number of days between the curDateTime and the expDateTime.
        curDateTime: current date in mm/dd/yy format.
        expDateTime: option expiration date in mm/dd/yy format.
        :return: number of days between curDateTime and expDateTime.
        '''
        curDateTime = self.getDateTime()
        expDateTime = self.getDTE()
        return (expDateTime - curDateTime).days
