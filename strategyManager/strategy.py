class Strategy(object):
     """This class sets up the basics for every strategy that will be used;
     For example, if we want to do an iron condor or a strangle, there
     are certain parameters that must be define.
     Attributes:
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

     def __init__(self, startTime, strategy, buyOrSell, underlying, orderQuantity, daysBeforeClose, optimalDTE=None,
                  minimumDTE=None, roc=None, minDaysToEarnings=None, minCredit=None, maxBuyingPower=None,
                  profitTargetPercent=None, avoidAssignment=None, maxBidAsk=None, minDaysSinceEarnings=None,
                  minIVR=None):

         """Inits Strategy class with constructor data.  We check to make sure that
         the user doesn't try to instantiate the Strategy class"""

         if self.__class__ == Strategy:
             raise NotImplementedError, "Cannot create object of class Strategy; must use derived classes such " \
                                         "as StrangleStrat or ICStrat"

         self.__startTime = startTime
         self.__strategy = strategy
         self.__buyOrSell = buyOrSell
         self.__underlying = underlying
         self.__orderQuantity = orderQuantity
         self.__daysBeforeClose = daysBeforeClose
         self.__optimalDTE = optimalDTE
         self.__minimumDTE = minimumDTE
         self.__roc = roc
         self.__minDaysToEarnings = minDaysToEarnings
         self.__minCredit = minCredit
         self.__maxBuyingPower = maxBuyingPower
         self.__profitTargetPercent = profitTargetPercent
         self.__avoidAssignment = avoidAssignment
         self.__maxBidAsk = maxBidAsk
         self.__minDaysSinceEarnings = minDaysSinceEarnings
         self.__minIVR = minIVR

     def getStartTime(self):
         return self.__startTime

     def getStrategyName(self):
         return self.__strategy

     def getBuyOrSell(self):
         return self.__buyOrSell

     def getUnderlying(self):
         return self.__underlying

     def getOrderQuantity(self):
         return self.__orderQuantity

     def getDaysBeforeClose(self):
         return self.__daysBeforeClose

     def getOptimalDTE(self):
         return self.__optimalDTE

     def getMinimumDTE(self):
         return self.__minimumDTE

     def getROC(self):
         return self.__roc

     def getMinDaysToEarnings(self):
         return self.__minDaysToEarnings

     def getMinCredit(self):
         return self.__minCredit

     def getMaxBuyingPower(self):
         return self.__maxBuyingPower

     def getProfitTargetPercent(self):
         return self.__profitTargetPercent

     def getAvoidAssignmentFlag(self):
         return self.__avoidAssignment

     def getMaxBidAsk(self):
         return self.__maxBidAsk

     def getMinDaysSinceEarnings(self):
         return self.__minDaysSinceEarnings

     def getMinIVR(self):
         return self.__minIVR
