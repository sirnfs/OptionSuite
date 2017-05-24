import strategy
from optionPrimitives import strangle

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
            buyOrSell:  do we buy an iron condor or sell an iron condor?
            underlying:  which underlying to use for the strategy
            orderQuantity:  number of strangles, iron condors, etc
            closeDate:  latest date / time to wait before closing the trade (generally before expiration)

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
                 underlying, orderQuantity, closeDateTime, optimalDTE=None,
                 minimumDTE=None, roc=None, minDaysToEarnings=None, minCredit=None, maxBuyingPower=None,
                 profitTargetPercent=None, avoidAssignment=None, maxBidAsk=None, minDaysSinceEarnings=None,
                 minIVR=None):

        self.__strategy = "strangle"

        strategy.Strategy.__init__(self, startTime, self.__strategy, buyOrSell, underlying, orderQuantity, closeDateTime,
                                   optimalDTE=None, minimumDTE=None, roc=None, minDaysToEarnings=None, minCredit=None,
                                   maxBuyingPower=None, profitTargetPercent=None, avoidAssignment=None, maxBidAsk=None,
                                   minDaysSinceEarnings=None, minIVR=None)

        #Create strangle strategy using strangle optionPrimitive
        #strangle.Strangle.__init__(self, underlying, optCallDelta, maxCallDelta, optPutDelta, maxPutDelta,
        #                           DTE, orderQuantity, buyOrSell)