import unittest
import portfolio
from optionPrimitives import strangle
from base import put
from base import call
from events import signalEvent
from dataHandler import csvData
import Queue as queue

class TestPortfolio(unittest.TestCase):

    def setUp(self):
        """
        Create portfolio object to be used for the remainder of UTs
        """
        self.startingCapital = 1000000
        self.maxCapitalToUse = 0.5
        self.maxCapitalToUsePerTrade = 0.5
        self.portfolioObj = portfolio.Portfolio(self.startingCapital, self.maxCapitalToUse,
                                                self.maxCapitalToUsePerTrade)

    def testPortfolioClassCreation(self):

        # Check that initial netLiq is the same as the starting capital
        self.assertEqual(self.portfolioObj.getNetLiq(), self.startingCapital)

        # Check that the initial buying power being used is zero.
        self.assertEqual(self.portfolioObj.getTotalBuyingPower(), 0)

    def testOnSignal(self):

        # Create a strangle
        putOpt = put.Put('SPX', 2690, 0.16, 34, underlyingPrice=2786.24, bidPrice=7.45, askPrice=7.45)
        # Create CALL option
        callOpt = call.Call('SPX', 2855, -0.15, 34, underlyingPrice=2786.24, bidPrice=5.20, askPrice=5.20)

        # Create Strangle
        orderQuantity = 1
        strangleObj = strangle.Strangle(orderQuantity, callOpt, putOpt, "SELL")

        # Create signal event
        event = signalEvent.SignalEvent()
        event.createEvent(strangleObj)

        # Test portfolio onSignal event
        self.portfolioObj.onSignal(event)

        # Check that positions array in portfolio is not empty
        positions = self.portfolioObj.getPositions()
        self.assertNotEqual(len(positions), 0)

        # Check that the buying power used by the strangle is correct
        self.assertAlmostEqual(self.portfolioObj.getTotalBuyingPower(), 64045.0)

        # Get the total delta value of the portfolio and check that it is 0.01
        self.assertAlmostEqual(self.portfolioObj.getDelta(), 0.01)

    def testUpdatePortfolio(self):
        """Test the ability to update option values for a position in the portfolio
        """
        startingCapital = 1000000
        maxCapitalToUse = 0.5
        maxCapitalToUsePerTrade = 0.5
        portfolioObj = portfolio.Portfolio(self.startingCapital, self.maxCapitalToUse,
                                                self.maxCapitalToUsePerTrade)

        # Get an option chain from the CSV
        # Create CsvData class object
        dataProvider = 'iVolatility'
        directory = '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_2011_2017'
        filename = 'RawIV_5day_sample.csv'
        chunkSize = 10000
        eventQueue = queue.Queue()
        csvObj = csvData.CsvData(directory, filename, dataProvider, eventQueue, chunkSize)

        # Get the first option chain
        firstOptionChainValid = csvObj.getOptionChain()
        queueObj = eventQueue.get(False)
        firstOptionChainData = queueObj.getData()

        # Choose two of the options in the first option chain to create a strangle; using first expiration
        putObj = firstOptionChainData[217] # -0.172245 delta put
        callObj = firstOptionChainData[248] # 0.154042 delta call

        # Create strangle an add to portfolio
        orderQuantity = 1
        strangleObj = strangle.Strangle(orderQuantity, callObj, putObj, "SELL")

        # Create signal event
        event = signalEvent.SignalEvent()
        event.createEvent(strangleObj)

        # Create portfolio onSignal event, which adds the position to the portfolio
        portfolioObj.onSignal(event)

        # Next, get the prices for the next day (1/4/11) and update the portfolio values
        newOptionChainValid = csvObj.getOptionChain()
        tickEvent = eventQueue.get(False)

        # Update portfolio values
        portfolioObj.updatePortfolio(tickEvent)

        # Check that the new portfolio values are correct (e.g., buying power, total delta, total gamma, etc)
        self.assertAlmostEqual(portfolioObj.getTotalBuyingPower(), 28950.0)
        self.assertAlmostEqual(portfolioObj.getVega(), 1.303171)
        self.assertAlmostEqual(portfolioObj.getDelta(), -0.018826)
        self.assertAlmostEqual(portfolioObj.getGamma(), 0.012173)
        self.assertAlmostEqual(portfolioObj.getTheta(), -0.583284)
        self.assertAlmostEqual(portfolioObj.getNetLiq(), 1000060.0)

if __name__ == '__main__':
    unittest.main()
