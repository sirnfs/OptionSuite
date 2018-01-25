import unittest
import portfolio

class TestPortfolio(unittest.TestCase):

    def setUp(self):
        """
        Create portfolio object to be used for the remainder of UTs
        """
        self.startingCapital = 100000
        self.maxCapitalToUse = 0.5
        self.maxCapitalToUsePerTrade = 0.05
        self.portfolioObj = portfolio.Portfolio(self.startingCapital, self.maxCapitalToUse,
                                                self.maxCapitalToUsePerTrade)

    def testPortfolioClassCreation(self):

        # Check that initial netLiq is the same as the starting capital
        self.assertEqual(self.portfolioObj.getNetLiq(), self.startingCapital)

        # Check that the initial buying power being used is zero.
        self.assertEqual(self.portfolioObj.getTotalBuyingPower(), 0)


if __name__ == '__main__':
    unittest.main()
