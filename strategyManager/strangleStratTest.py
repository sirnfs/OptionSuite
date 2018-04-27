import unittest
import strangleStrat
from datetime import datetime
import pytz
import Queue as queue
from dataHandler import csvData

class TestStrangleStrategy(unittest.TestCase):
    # Used to set up the unittest class.
    def setUp(self):
        """Create instance of strangle strategy
          Strangle specific attributes:
          optCallDelta:  Optimal delta for call, usually around 16 delta.
          maxCallDelta:  Max delta for call, usually around 30 delta.
          optPutDelta:  Optimal delta for put, usually around 16 delta.
          maxPutDelta:  Max delta for put, usually around 30 delta.


        General strategy attributes:
           startDateTime:  Date/time to start the live trading or backtest.
           strategy:  Option strategy to use -- e.g., iron condor, strangle
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
           maxBuyingPower:  Maximum buying power to use on overall trade.
           profitTargetPercent:  Percentage of initial credit to use when closing trade.
           maxBidAsk:  Maximum price to allow between bid and ask prices of option (for any strike or put/call).
           maxMidDev:  Maximum deviation from midprice on opening and closing of trade (e.g., 0.02 cents from midprice).
           minDaysSinceEarnings:  Minimum number of days to wait after last earnings before putting on strategy.
           minIVR:  Minimum implied volatility rank needed to put on strategy.
        """

        self.eventQueue = queue.Queue()

        # Create strangle strategy object.
        optCallDelta = 0.16
        maxCallDelta = 0.30
        optPutDelta = -0.16
        maxPutDelta = -0.30
        startTime = datetime.now(pytz.utc)
        buyOrSell = 1  # 0 = buy, 1 = sell (currently only support selling)
        underlying = 'AAPL'
        orderQuantity = 1
        daysBeforeClose = 5
        expCycle = 'm'
        optimalDTE = 45
        minimumDTE = 25
        minCredit = 0.5
        profitTargetPercent = 50
        maxBidAsk = 0.05
        minDaysToEarnings = None
        minDaysSinceEarnings = None
        minIVR = None
        self.curStrategy = strangleStrat.StrangleStrat(self.eventQueue, optCallDelta, maxCallDelta, optPutDelta,
                                                       maxPutDelta,startTime, buyOrSell, underlying, orderQuantity,
                                                       daysBeforeClose, expCycle=expCycle, optimalDTE=optimalDTE,
                                                       minimumDTE=minimumDTE, minDaysToEarnings=minDaysToEarnings,
                                                       minCredit=minCredit, profitTargetPercent=profitTargetPercent,
                                                       maxBidAsk=maxBidAsk, minDaysSinceEarnings=minDaysSinceEarnings,
                                                       minIVR=minIVR)

        # Create CsvData class object.
        self.dataProvider = 'iVolatility'
        self.directory = '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_2011_2017'
        self.filename = 'RawIV.csv'
        self.chunkSize = 10000
        self.csvObj = csvData.CsvData(self.directory, self.filename, self.dataProvider, self.eventQueue, self.chunkSize)

    def testStrangleStratCreation(self):

        self.assertEqual(self.curStrategy.getOptimalCallDelta(), 0.16)

    def testHasMinimumDTE_Method(self):
        local = pytz.timezone('US/Eastern')
        expDateTime = datetime.strptime("08/30/17", "%m/%d/%y")
        expDateTime = local.localize(expDateTime, is_dst=None)
        expDateTime = expDateTime.astimezone(pytz.utc)

        curDateTime = datetime.strptime("08/01/17", "%m/%d/%y")
        curDateTime = local.localize(curDateTime, is_dst=None)
        curDateTime = curDateTime.astimezone(pytz.utc)

        hasMin = self.curStrategy.hasMinimumDTE(curDateTime, expDateTime)

        self.assertEqual(hasMin, True)

    def testIsMonthlyExp(self):
        local = pytz.timezone('US/Eastern')
        expDateTime = datetime.strptime("12/16/11", "%m/%d/%y")
        expDateTime = local.localize(expDateTime, is_dst=None)
        expDateTime = expDateTime.astimezone(pytz.utc)

        isMonthly = self.curStrategy.isMonthlyExp(expDateTime)
        self.assertTrue(isMonthly)

if __name__ == '__main__':
    unittest.main()
