import unittest
import portfolio
from optionPrimitives import strangle
from base import put
from base import call
from events import signalEvent

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

    def testOnSignalEvent(self):

        # Create a strangle
        putOpt = put.Put('SPX', 2690, 0.15, 34, underlyingPrice=2786.24, bidPrice=7.45, askPrice=7.45)
        # Create CALL option
        callOpt = call.Call('SPX', 2855, -0.15, 34, underlyingPrice=2786.24, bidPrice=5.20, askPrice=5.20)

        # Create Strangle
        orderQuantity = 1
        strangleObj = strangle.Strangle(orderQuantity, callOpt, putOpt)

        # Create signal event
        event = signalEvent.SignalEvent()
        event.createEvent(strangleObj)

        # Test portfolio onSignal event
        self.portfolioObj.onSignal(event)

        # Check that positions array in portfolio is not empty
        positions = self.portfolioObj.getPositions()
        self.assertNotEqual(len(positions), 0)

        # Check that the buying power used by the strangle is correct
        self.assertAlmostEqual(self.portfolioObj.getTotalBuyingPower(), 64045.0, 2)


if __name__ == '__main__':
    unittest.main()
