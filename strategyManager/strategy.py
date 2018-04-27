class Strategy(object):
     """This class sets up the basics for every strategy that will be used;
     For example, if we want to do an iron condor or a strangle, there
     are certain parameters that must be defined.
     Attributes:
         startDateTime:  Date/time to start the live trading or backtest.
         strategy:  Option strategy to use -- e.g., iron condor, strangle.
         buyOrSell:  Do we buy an iron condor or sell an iron condor? 0 = buy, 1 = sell.
         underlying:  Which underlying to use for the strategy.
         orderQuantity:  Number of strangles, iron condors, etc.
         daysBeforeClose:  Number of days before expiration to close the trade.
         
         optional attributes:

         expCycle:  Specifies if we want to do monthly ('m'); unspecified means we can do weekly, quarterly, etc.
         optimalDTE:  Optimal number of days before expiration to put on strategy.
         minimumDTE:  Minimum number of days before expiration to put on strategy.
         roc:  Minimal return on capital for overall trade as a decimal.
         minDaysToEarnings:  Minimum number of days to put on trade before earnings.
         minCredit:  Minimum credit to collect on overall trade.
         profitTargetPercent:  Percentage of initial credit to use when closing trade.
         customManagement:  boolean -- manages trade using custom rules.
         maxBidAsk:  Maximum price to allow between bid and ask prices of option (for any strike or put/call).
         maxMidDev:  Maximum deviation from midprice on opening and closing of trade (e.g., 0.02 cents from midprice).
         minDaysSinceEarnings:  Minimum number of days to wait after last earnings before putting on strategy.
         minIVR:  Minimum implied volatility rank needed to put on strategy.
         minBuyingPower:  Minimum investment we want for the strategy -- since prices vary greatly over a range like
                          1990 to 2017, we would like to have the same amount of money in the market at any given
                          time, so we increase the number of contracts to reach this minBuyingPower.
     """

     def __init__(self, startTime, strategy, buyOrSell, underlying, orderQuantity, daysBeforeClose, expCycle=None,
                  optimalDTE=None, minimumDTE=None, roc=None, minDaysToEarnings=None, minCredit=None,
                  profitTargetPercent=None, customManagement=None, maxBidAsk=None, maxMidDev=None,
                  minDaysSinceEarnings=None, minIVR=None, minBuyingPower=None):

         """Inits Strategy class with constructor data.  We check to make sure that
         the user doesn't try to instantiate the Strategy class."""

         if self.__class__ == Strategy:
             raise NotImplementedError, "Cannot create object of class Strategy; must use derived classes such " \
                                         "as StrangleStrat."

         self.__startTime = startTime
         self.__strategy = strategy
         self.__buyOrSell = buyOrSell
         self.__underlying = underlying
         self.__orderQuantity = orderQuantity
         self.__daysBeforeClose = daysBeforeClose
         self.__expCycle = expCycle
         self.__optimalDTE = optimalDTE
         self.__minimumDTE = minimumDTE
         self.__roc = roc
         self.__minDaysToEarnings = minDaysToEarnings
         self.__minCredit = minCredit
         self.__profitTargetPercent = profitTargetPercent
         self.__customManagement = customManagement
         self.__maxBidAsk = maxBidAsk
         self.__maxMidDev = maxMidDev
         self.__minDaysSinceEarnings = minDaysSinceEarnings
         self.__minIVR = minIVR
         self.__minBuyingPower = minBuyingPower

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

     def getExpCycle(self):
         return self.__expCycle

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

     def getProfitTargetPercent(self):
         return self.__profitTargetPercent

     def getCustomManagementFlag(self):
         return self.__customManagement

     def getMaxBidAsk(self):
         return self.__maxBidAsk

     def getMaxMidDev(self):
         return self.__maxMidDev

     def getMinDaysSinceEarnings(self):
         return self.__minDaysSinceEarnings

     def getMinIVR(self):
         return self.__minIVR

     def getMinBuyingPower(self):
         return self.__minBuyingPower

     def setMinBuyingPower(self, minBuyingPower):
         self.__minBuyingPower = minBuyingPower

     def checkForSignal(self, event):
         raise NotImplementedError("Each strategy must implement the 'checkForSignal' method.")
