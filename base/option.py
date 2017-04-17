
class Option(object):
    """This class defines one the basic types for the backtester or live trader -- an option.  
    Other classes such as put or call will be derived from this class

     An option has the following internals
     -Underlying price
     -Underlying ticker symbol
     -Option Symbol
     -Alias (old symbol for option if it exists)
     -Strike price
     -Buy/Sell (long/short) -- binary value
     -Bid price
     -Ask price
     -Open interest
     -Volume
     -Quote Date / Time
     -Delta
     -Theta
     -Gamma
     -Rho
     -Vega
     -Implied Volatility
     -Days to Expiration
     -Exchange Code
     -Exercise Price
     -Assignment price
     -Cost to open
     -Cost to close
     -Trade ID:  used to keep track of trade / may not be needed

     Attributes:
       underlyingPrice:  price of the underlying / stock which has option derivatives in dollars
       underlyingTicker:  ticker symbol (e.g., SPY) of underlying
       optionSymbol:  code different than the underlying ticker used to denote option
       optionAlias:  old code used to denote option if it changed; usually blank
       strikePrice:  strike price of option
       optionType:  put or call
       longOrShort:  indicates if we are long or short the option; 'Long' = long and 'Short' = short
       bidPrice:  current bid price of option
       askPrice:  current asking price of option
       openInterest:  number of open option contracts
       volume:  number of contracts traded
       dateTime:  data / time of quote recieved; would also be data / time bought / sold
       delta:  greek for quantifying percent of stock we're long or short (-1 to 1)
       theta:  daily return in dollars if no movement in underlying price
       gamma:  describes rate of change of delta (float)
       rho:  how much option price changes with change in interest rate (dollars)
       vega:  change in price of option for every 1% change in volatility
       impliedVol:  implied volatility percentage (calculated using Black Scholes & binominal tree
       DTE:  days to expiration of option 
       exchangeCode:  symbol used to denote which exchanged used or where quote came from
       exercisePrice:  price to exercise option early 
       assignPrice:  price you must pay if other party exercises option
       openCost:  cost to open the option trade
       closeCost:  cost to close out the option trade
       tradeID:  used to keep track of the trade that was put on so we can reference it later
                 the tradeID is associated with both the strategy and the options in the strategy
     """

    def __init__(self, underlyingTicker, strikePrice, optionType, longOrShort, delta, DTE,
                 underlyingPrice=None, optionSymbol=None, optionAlias=None, bidPrice=None,
                 askPrice=None, openInterest=None, volume=None, dateTime=None, theta=None,
                 gamma=None, rho=None, vega=None, impliedVol=None, exchangeCode=None,
                 exercisePrice=None, assignPrice=None, openCost=None, closeCost=None,
                 tradeID=None):
        """Inits Option class with constructor data.  We check to make sure that
        the user doesn't try to instantiate the Option class"""

        if self.__class__ == Option:
            raise NotImplementedError, "Cannot create object of class Option; must use PUT or CALL " \
                                       "classes"

        self.__underlyingPrice = underlyingPrice
        self.__underlyingTicker = underlyingTicker
        self.__optionSymbol = optionSymbol
        self.__optionAlias = optionAlias
        self.__strikePrice = strikePrice
        self.__optionType = optionType
        self.__longOrShort = longOrShort
        self.__bidPrice = bidPrice
        self.__askPrice = askPrice
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
        self.__tradeID = tradeID

    def getUnderlyingPrice(self):
        return self.__underlyingPrice

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

    def getTradeID(self):
        return self.__tradeID

