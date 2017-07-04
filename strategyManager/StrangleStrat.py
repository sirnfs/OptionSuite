import strategy
from events import signalEvent

class StrangleStrat(strategy.Strategy):
    """This class sets up the basics for a SPECIFIC strategy that will be used;
       In this case, we set up the strangle strategy, which involves buying or
       selling strangles with certain parameters
       
       Strangle specific attributes:
           optCallDelta:  optimal delta for call, usually around 16 delta
           maxCallDelta:  max delta for call, usually around 30 delta
           optPutDelta:  optimal delta for put, usually around 16 delta
           maxPutDelta:  max delta for put, usually around 30 delta


       General strategy attributes:
            startDateTime:  date/time to start the live trading or backtest
            strategy:  option strategy to use -- e.g., iron condor, strangle
            buyOrSell:  do we buy an iron condor or sell an iron condor? 0 = buy, 1 = sell
            underlying:  which underlying to use for the strategy
            orderQuantity:  number of strangles, iron condors, etc
            daysBeforeClose:  number of days before expiration to close the trade

            optional attributes:

            optimalDTE:  optimal number of days before expiration to put on strategy
            minimumDTE:  minimum number of days before expiration to put on strategy
            roc:  return on capital for overall trade
            minDaysToEarnings:  minimum number of days to put on trade before earnings
            minCredit:  minimum credit to collect on overall trade
            maxBuyingPower:  maximum buying power to use on overall trade
            profitTargetPercent:  percentage of initial credit to use when closing trade
            avoidAssignment:  boolean -- closes out trade using defined rules to avoid stock assignment
            maxBidAsk:  maximum price to allow between bid and ask prices of option (for any strike or put/call)
            maxMidDev:  maximum deviation from midprice on opening and closing of trade (e.g., 0.02 cents from midprice)
            minDaysSinceEarnings:  minimum number of days to wait after last earnings before putting on strategy
            minIVR:  minimum implied volatility rank needed to put on strategy
    """

    def __init__(self, optCallDelta, maxCallDelta, optPutDelta, maxPutDelta, startTime, buyOrSell,
                 underlying, orderQuantity, daysBeforeClose, optimalDTE=None,
                 minimumDTE=None, roc=None, minDaysToEarnings=None, minCredit=None, maxBuyingPower=None,
                 profitTargetPercent=None, avoidAssignment=None, maxBidAsk=None, minDaysSinceEarnings=None,
                 minIVR=None):

        self.__strategy = "strangle"
        self.__optCallDelta = optCallDelta
        self.__maxCallDelta = maxCallDelta
        self.__optPutDelta = optPutDelta
        self.__maxPutDelta = maxPutDelta

        strategy.Strategy.__init__(self, startTime, self.__strategy, buyOrSell, underlying, orderQuantity,
                                   daysBeforeClose, optimalDTE, minimumDTE, roc, minDaysToEarnings,
                                   minCredit, maxBuyingPower, profitTargetPercent, avoidAssignment,
                                   maxBidAsk, minDaysSinceEarnings, minIVR)

    def getOptimalCallDelta(self):
        return self.__optCallDelta

    def getMaxCallDelta(self):
        return self.__maxCallDelta

    def getOptimalPutDelta(self):
        return self.__optPutDelta

    def getMaxPutDelta(self):
        return self.__maxPutDelta


    def checkForSignal(self, event):
        """Criteria that we need to check before generating a signal event:

        Required:
        optCallDelta:  optimal delta for call, usually around 16 delta
        maxCallDelta:  max delta for call, usually around 30 delta
        optPutDelta:  optimal delta for put, usually around 16 delta
        maxPutDelta:  max delta for put, usually around 30 delta
        startDateTime:  date/time to start the live trading or backtest
        strategy:  option strategy to use -- e.g., iron condor, strangle
        buyOrSell:  do we buy an iron condor or sell an iron condor? 0 = buy, 1 = sell
        underlying:  which underlying to use for the strategy
        orderQuantity:  number of strangles, iron condors, etc
        daysBeforeClose:  number of days before expiration to close the trade

        Optional:
        optimalDTE:  optimal number of days before expiration to put on strategy
        minimumDTE:  minimum number of days before expiration to put on strategy
        roc:  return on capital for overall trade
        minDaysToEarnings:  minimum number of days to put on trade before earnings
        minCredit:  minimum credit to collect on overall trade
        maxBuyingPower:  maximum buying power to use on overall trade
        profitTargetPercent:  percentage of initial credit to use when closing trade
        avoidAssignment:  boolean -- closes out trade using defined rules to avoid stock assignment
        maxBidAsk:  maximum price to allow between bid and ask prices of option (for any strike or put/call)
        maxMidDev:  maximum deviation from midprice on opening and closing of trade (e.g., 0.02 cents from midprice)
        minDaysSinceEarnings:  minimum number of days to wait after last earnings before putting on strategy
        minIVR:  minimum implied volatility rank needed to put on strategy

        We go through each option in the option chain and find all of the options that meet the criteria.  If there
        are multiple options that meet the criteria, we choose the first one, but we could use some other type of
        rule for choosing.
        """

        #Get the data from the tick event
        eventData = event.getData()

        #These temporary variables will be used to keep track of the optimal options as we go through the options
        #chain
        optimalCallOpt = []
        optimalPutOpt = []

        #Process one option at a time from the option chain (now objects of option class)
        for option in eventData:
            #First check if the option is a call or a put
            if option.getOptionType() == 'CALL':
                pass
            elif option.getOptionType() == 'PUT':
                pass

        return eventData