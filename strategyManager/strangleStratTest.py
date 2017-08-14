import unittest
import strangleStrat
from datetime import datetime
import pytz
import Queue as queue
from dataHandler import csvData

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

        self.eventQueue = queue.Queue()

        # Create strangle strategy object
        optCallDelta = 0.16  # integers or floats?
        maxCallDelta = 0.30
        optPutDelta = -0.16
        maxPutDelta = -0.30
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
        self.curStrategy = strangleStrat.StrangleStrat(self.eventQueue, optCallDelta, maxCallDelta, optPutDelta,
                                                       maxPutDelta,startTime, buyOrSell, underlying, orderQuantity,
                                                       daysBeforeClose, expCycle=expCycle, optimalDTE=optimalDTE,
                                                       minimumDTE=minimumDTE, minDaysToEarnings=minDaysToEarnings,
                                                       minCredit=minCredit, maxBuyingPower=maxBuyingPower,
                                                       profitTargetPercent=profitTargetPercent, maxBidAsk=maxBidAsk,
                                                       minDaysSinceEarnings=minDaysSinceEarnings, minIVR=minIVR)

        # Create CsvData class object
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

    # def testFileWrite(self):
    #     f = open('fileWriteTest.txt', 'w')
    #     f.write("Date / Time")
    #     f.write("\n")
    #     f.write("Put Delta, Put DTE")
    #     f.write("\n")
    #     f.write("Call Delta, Call DTE")
    #     f.write("\n")
    #     f.close()
    #     pass

    def testStrangleCriteriaMet(self):
        # Get option chain and see if we trigger any signal events
        while self.csvObj.getOptionChain():
            # Get event from the queue
            event = self.eventQueue.get()
            self.curStrategy.checkForSignal(event)
            # Get the signal event
            # Check if queue is empty
            if self.eventQueue.empty():
                print("Empty queue; problem?")
            else:
              event = self.eventQueue.get()
              # Do nothing with the event for now

        #self.curStrategy._f.close()
        pass

if __name__ == '__main__':
    unittest.main()
