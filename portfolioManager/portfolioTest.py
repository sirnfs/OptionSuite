import unittest
import portfolio
from optionPrimitives import strangle
from base import put
from base import call
from events import signalEvent
from events import tickEvent
from dataHandler import csvData
import Queue as queue
import datetime
import pytz

class TestPortfolio(unittest.TestCase):

    def setUp(self):
        """
        Create portfolio object to be used for the remainder of UTs.
        """
        self.startingCapital = 1000000
        self.maxCapitalToUse = 0.5
        self.maxCapitalToUsePerTrade = 0.5
        self.portfolioObj = portfolio.Portfolio(self.startingCapital, self.maxCapitalToUse,
                                                self.maxCapitalToUsePerTrade)

    def testPortfolioClassCreation(self):

        # Check that initial netLiq is the same as the starting capital.
        self.assertEqual(self.portfolioObj.getNetLiq(), self.startingCapital)

        # Check that the initial buying power being used is zero.
        self.assertEqual(self.portfolioObj.getTotalBuyingPower(), 0)

    def testOnSignal(self):

        # Create a strangle.
        putOpt = put.Put('SPX', 2690, 0.16, 34, underlyingPrice=2786.24, bidPrice=7.45, askPrice=7.45)
        # Create CALL option.
        callOpt = call.Call('SPX', 2855, -0.15, 34, underlyingPrice=2786.24, bidPrice=5.20, askPrice=5.20)

        # Create Strangle.
        orderQuantity = 1
        strangleObj = strangle.Strangle(orderQuantity, callOpt, putOpt, "SELL")

        # Create signal event.
        event = signalEvent.SignalEvent()
        event.createEvent(strangleObj)

        # Test portfolio onSignal event.
        self.portfolioObj.onSignal(event)

        # Check that positions array in portfolio is not empty.
        positions = self.portfolioObj.getPositions()
        self.assertNotEqual(len(positions), 0)

        # Check that the buying power used by the strangle is correct.
        self.assertAlmostEqual(self.portfolioObj.getTotalBuyingPower(), 64045.0)

        # Get the total delta value of the portfolio and check that it is 0.01.
        self.assertAlmostEqual(self.portfolioObj.getDelta(), 0.01)

    def testUpdatePortfolio(self):
        """Test the ability to update option values for a position in the portfolio.
        """
        startingCapital = 1000000
        maxCapitalToUse = 0.5
        maxCapitalToUsePerTrade = 0.5
        portfolioObj = portfolio.Portfolio(self.startingCapital, self.maxCapitalToUse,
                                                self.maxCapitalToUsePerTrade)

        # Get an option chain from the CSV.
        # Create CsvData class object.
        dataProvider = 'iVolatility'
        directory = '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_2011_2017'
        filename = 'RawIV_5day_sample.csv'
        chunkSize = 10000
        eventQueue = queue.Queue()
        csvObj = csvData.CsvData(directory, filename, dataProvider, eventQueue, chunkSize)

        # Get the first option chain.
        firstOptionChainValid = csvObj.getOptionChain()
        queueObj = eventQueue.get(False)
        firstOptionChainData = queueObj.getData()

        # Choose two of the options in the first option chain to create a strangle; using first expiration.
        putObj = firstOptionChainData[217] # -0.172245 delta put
        callObj = firstOptionChainData[248] # 0.154042 delta call

        # Create strangle an add to portfolio.
        orderQuantity = 1
        strangleObj = strangle.Strangle(orderQuantity, callObj, putObj, "SELL")

        # Create signal event.
        event = signalEvent.SignalEvent()
        event.createEvent(strangleObj)

        # Create portfolio onSignal event, which adds the position to the portfolio.
        portfolioObj.onSignal(event)

        # Next, get the prices for the next day (1/4/11) and update the portfolio values.
        newOptionChainValid = csvObj.getOptionChain()
        tickEvent = eventQueue.get(False)

        # Update portfolio values.
        portfolioObj.updatePortfolio(tickEvent)

        # Check that the new portfolio values are correct (e.g., buying power, total delta, total gamma, etc).
        self.assertAlmostEqual(portfolioObj.getTotalBuyingPower(), 28950.0)
        self.assertAlmostEqual(portfolioObj.getVega(), 1.303171)
        self.assertAlmostEqual(portfolioObj.getDelta(), -0.018826)
        self.assertAlmostEqual(portfolioObj.getGamma(), 0.012173)
        self.assertAlmostEqual(portfolioObj.getTheta(), -0.583284)
        self.assertAlmostEqual(portfolioObj.getNetLiq(), 1000060.0)

    def testPortfolioPositionRemoveManagement(self):
        """Test that we can remove a managed position from the portfolio without affecting any of the other positions
        in the portfolio.
        """

        # Create portfolio object.
        portfolioObj = portfolio.Portfolio(self.startingCapital, self.maxCapitalToUse,
                                           self.maxCapitalToUsePerTrade)

        # Add first position to the portfolio.
        putOpt = put.Put('SPX', 2690, 0.15, 34, underlyingPrice=2786.24, bidPrice=7.45, askPrice=7.45,
                         optionSymbol="01", tradePrice=7.45)
        callOpt = call.Call('SPX', 2855, -0.15, 34, underlyingPrice=2786.24, bidPrice=5.20, askPrice=5.20,
                            optionSymbol="02", tradePrice=5.20)

        # Create Strangle.
        orderQuantity = 1
        profitTargetPercent = 0.5
        strangleObj = strangle.Strangle(orderQuantity, callOpt, putOpt, "SELL", profitTargetPercent=profitTargetPercent)

        # Create signal event.
        event = signalEvent.SignalEvent()
        event.createEvent(strangleObj)

        # Create portfolio onSignal event, which adds the position to the portfolio.
        portfolioObj.onSignal(event)

        # Add second position to the portfolio.
        putOpt = put.Put('AAPL', 140, 0.15, 34, underlyingPrice=150, bidPrice=5.15, askPrice=5.15,
                         optionSymbol="03", tradePrice=5.15)
        callOpt = call.Call('APPL', 160, -0.15, 34, underlyingPrice=150, bidPrice=3.20, askPrice=3.20,
                            optionSymbol="04", tradePrice=3.20)

        strangleObj = strangle.Strangle(orderQuantity, callOpt, putOpt, "SELL", profitTargetPercent=profitTargetPercent)

        # Create signal event.
        event = signalEvent.SignalEvent()
        event.createEvent(strangleObj)

        # Create portfolio onSignal event, which adds the position to the portfolio.
        portfolioObj.onSignal(event)

        # Add a third position to the portfolio.
        putOpt = put.Put('SPY', 240, 0.15, 34, underlyingPrice=280, bidPrice=4.15, askPrice=4.15,
                         optionSymbol="05", tradePrice=4.15)
        callOpt = call.Call('SPY', 300, -0.15, 34, underlyingPrice=280, bidPrice=2.20, askPrice=2.20,
                            optionSymbol="06", tradePrice=2.20)

        strangleObj = strangle.Strangle(orderQuantity, callOpt, putOpt, "SELL", profitTargetPercent=profitTargetPercent)

        # Create signal event.
        event = signalEvent.SignalEvent()
        event.createEvent(strangleObj)

        # Create portfolio onSignal event, which adds the position to the portfolio.
        portfolioObj.onSignal(event)

        # For the second position in the portfolio, make the option prices less than 50% of the trade price, which
        # should cause the position to be closed / deleted from the portfolio.
        newOptionObjs = []
        putOpt = put.Put('SPX', 2690, 0.15, 34, underlyingPrice=2786.24, bidPrice=7.45, askPrice=7.45,
                         optionSymbol="01", tradePrice=7.45)
        newOptionObjs.append(putOpt)
        callOpt = call.Call('SPX', 2855, -0.15, 34, underlyingPrice=2786.24, bidPrice=5.20, askPrice=5.20,
                            optionSymbol="02", tradePrice=5.20)
        newOptionObjs.append(callOpt)
        putOpt = put.Put('AAPL', 140, 0.15, 34, underlyingPrice=150, bidPrice=2.15, askPrice=2.15,
                         optionSymbol="03")
        newOptionObjs.append(putOpt)
        callOpt = call.Call('APPL', 160, -0.15, 34, underlyingPrice=150, bidPrice=1.20, askPrice=1.20,
                            optionSymbol="04")
        newOptionObjs.append(callOpt)
        putOpt = put.Put('SPY', 240, 0.15, 34, underlyingPrice=280, bidPrice=4.15, askPrice=4.15,
                         optionSymbol="05", tradePrice=4.15)
        newOptionObjs.append(putOpt)
        callOpt = call.Call('SPY', 300, -0.15, 34, underlyingPrice=280, bidPrice=2.20, askPrice=2.20,
                            optionSymbol="06", tradePrice=2.20)
        newOptionObjs.append(callOpt)

        newEvent = tickEvent.TickEvent()
        newEvent.createEvent(newOptionObjs)
        portfolioObj.updatePortfolio(newEvent)

        # Check that the first position is the SPX position, and the second position is the SPY position, i.e., the
        # AAPL position should have been managed / removed.
        positions = portfolioObj.getPositions()
        callPos0 = positions[0].getCallOption()
        callPos1 = positions[1].getCallOption()

        self.assertEqual(callPos0.getUnderlyingTicker(), 'SPX')
        self.assertEqual(callPos1.getUnderlyingTicker(), 'SPY')
        self.assertEqual(len(positions), 2)

    def testPortfolioWithExpirationManagement(self):
        """Put on a strangle; update portfolio values, and then manage the strangle when the daysBeforeClosing
        threshold has been met.
        """
        # Create portfolio object.
        portfolioObj = portfolio.Portfolio(self.startingCapital, self.maxCapitalToUse,
                                           self.maxCapitalToUsePerTrade)

        # Set up date / time formats.
        local = pytz.timezone('US/Eastern')

        # Convert time zone of data 'US/Eastern' to UTC time.
        expDate = datetime.datetime.strptime("02/20/18", "%m/%d/%y")
        expDate = local.localize(expDate, is_dst=None)
        expDate = expDate.astimezone(pytz.utc)

        # Convert time zone of data 'US/Eastern' to UTC time.
        curDate = datetime.datetime.strptime("02/02/18", "%m/%d/%y")
        curDate = local.localize(curDate, is_dst=None)
        curDate = curDate.astimezone(pytz.utc)

        # Add first position to the portfolio.
        putOpt = put.Put('SPX', 2690, 0.15, expDate, underlyingPrice=2786.24, bidPrice=7.45, askPrice=7.45,
                         optionSymbol="01", tradePrice=7.45, dateTime=curDate)
        callOpt = call.Call('SPX', 2855, -0.15, expDate, underlyingPrice=2786.24, bidPrice=5.20, askPrice=5.20,
                            optionSymbol="02", tradePrice=5.20, dateTime=curDate)

        # Create Strangle.
        orderQuantity = 1
        daysBeforeClosing = 5
        strangleObj = strangle.Strangle(orderQuantity, callOpt, putOpt, "SELL", daysBeforeClosing)

        # Create signal event.
        event = signalEvent.SignalEvent()
        event.createEvent(strangleObj)

        # Create portfolio onSignal event, which adds the position to the portfolio.
        portfolioObj.onSignal(event)

        # Check that the position was added to the portfolio.
        self.assertEqual(len(portfolioObj.getPositions()), 1)

        # Change the time to be within five days from the DTE, which should cause the position to be closed / deleted
        # from the portfolio.
        curDate = datetime.datetime.strptime("02/19/18", "%m/%d/%y")
        curDate = local.localize(curDate, is_dst=None)
        curDate = curDate.astimezone(pytz.utc)

        newOptionObjs = []
        putOpt = put.Put('SPX', 2690, 0.15, expDate, underlyingPrice=2786.24, bidPrice=7.45, askPrice=7.45,
                         optionSymbol="01", tradePrice=7.45, dateTime=curDate)
        newOptionObjs.append(putOpt)
        callOpt = call.Call('SPX', 2855, -0.15, expDate, underlyingPrice=2786.24, bidPrice=5.20, askPrice=5.20,
                            optionSymbol="02", tradePrice=5.20, dateTime=curDate)
        newOptionObjs.append(callOpt)

        newEvent = tickEvent.TickEvent()
        newEvent.createEvent(newOptionObjs)
        portfolioObj.updatePortfolio(newEvent)

        # Check that the position was managed / deleted from the portfolio.
        self.assertEqual(len(portfolioObj.getPositions()), 0)

if __name__ == '__main__':
    unittest.main()
