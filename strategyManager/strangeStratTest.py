import unittest
import strangleStrat
from datetime import datetime
import pytz
from pytz import timezone

class TestStrangleStrategy(unittest.TestCase):
    # Used to set up the unittest class
    def setUp(self):
        """Create instance of strangle strategy
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

           expCycle:  specifies if we want to do monthly ('m'); unspecified means we can do weekly, quarterly, etc
           optimalDTE:  optimal number of days before expiration to put on strategy
           minimumDTE:  minimum number of days before expiration to put on strategy
           roc:  minimal return on capital for overall trade as a decimal
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

        # Create strangle strategy object
        optCallDelta = 16  # integers or floats?
        maxCallDelta = 30
        optPutDelta = 16
        maxPutDelta = 30
        startTime = datetime.now(pytz.utc) #datetime.now(timezone('US/Eastern'))
        buyOrSell = 1  # 0 = buy, 1 = sell (currently only support selling)
        underlying = 'AAPL'
        orderQuantity = 1
        daysBeforeClose = 5
        expCycle = 'm'
        optimalDTE = 45
        minimumDTE = 25
        minCredit = 0.5
        maxBuyingPower = None #4000
        profitTargetPercent = 50
        maxBidAsk = 0.05
        minDaysToEarnings = None #25
        minDaysSinceEarnings = None #3
        minIVR = None #15
        self.curStrategy = strangleStrat.StrangleStrat(optCallDelta, maxCallDelta, optPutDelta, maxPutDelta,
                                                  startTime, buyOrSell, underlying, orderQuantity,
                                                  daysBeforeClose, expCycle=expCycle, optimalDTE=optimalDTE,
                                                  minimumDTE=minimumDTE, minDaysToEarnings=minDaysToEarnings,
                                                  minCredit=minCredit, maxBuyingPower=maxBuyingPower,
                                                  profitTargetPercent=profitTargetPercent, maxBidAsk=maxBidAsk,
                                                  minDaysSinceEarnings=minDaysSinceEarnings, minIVR=minIVR)

    def testStrangleStratCreation(self):

        self.assertEqual(self.curStrategy.getOptimalCallDelta(), 16)

    def testHasMinimumDTE_Method(self):
        local = pytz.timezone('US/Eastern')
        dateTime = datetime.strptime("08/30/17", "%m/%d/%y")
        dateTime = local.localize(dateTime, is_dst=None)
        dateTime = dateTime.astimezone(pytz.utc)

        hasMin = self.curStrategy.hasMinimumDTE(dateTime)

        self.assertEqual(hasMin, True)

if __name__ == '__main__':
    unittest.main()
