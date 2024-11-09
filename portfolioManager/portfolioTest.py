import unittest
import datetime
import decimal
import json
from portfolioManager import portfolio
from optionPrimitives import optionPrimitive, strangle
from base import put
from base import call
from events import signalEvent, tickEvent
from riskManager import strangleRiskManagement


class TestPortfolio(unittest.TestCase):

    def setUp(self):
        """Create portfolio object to be shared among tests."""

        # Strangle object to be shared among tests.
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                         strikePrice=decimal.Decimal(2690), delta=-0.16, gamma=0.01, theta=0.02, vega=0.03,
                         dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                         bidPrice=decimal.Decimal(7.45), askPrice=decimal.Decimal(7.50),
                         tradePrice=decimal.Decimal(7.475),
                         settlementPrice=decimal.Decimal(7.475))
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                            strikePrice=decimal.Decimal(2855), delta=0.16, gamma=0.01, theta=0.02, vega=0.03,
                            dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                          "%m/%d/%Y"),
                            bidPrice=decimal.Decimal(5.20), askPrice=decimal.Decimal(5.40),
                            tradePrice=decimal.Decimal(5.30), settlementPrice=decimal.Decimal(5.30))
        self.__strangleObj = strangle.Strangle(orderQuantity=1, contractMultiplier=100, callOpt=callOpt, putOpt=putOpt,
                                               buyOrSell=optionPrimitive.TransactionType.SELL)
        self.pricingSource = 'tastyworks'
        with open('./dataHandler/pricingConfig.json') as config:
            fullConfig = json.load(config)
            self.pricingSourceConfig = fullConfig[self.pricingSource]
        self.__strangleObj.setOpeningFees(self.__strangleObj.getCommissionsAndFees('open', self.pricingSource,
                                                                                   self.pricingSourceConfig))
        self.__strangleObj.setClosingFees(self.__strangleObj.getCommissionsAndFees('close', self.pricingSource,
                                                                                   self.pricingSourceConfig))
        self.riskManagement = strangleRiskManagement.StrangleRiskManagement(
            strangleRiskManagement.StrangleManagementStrategyTypes.HOLD_TO_EXPIRATION)

        startingCapital = decimal.Decimal(1000000)
        maxCapitalToUse = decimal.Decimal(0.5)
        maxCapitalToUsePerTrade = decimal.Decimal(0.5)
        self.__portfolioObj = portfolio.Portfolio(startingCapital, maxCapitalToUse, maxCapitalToUsePerTrade)

    def testOnSignalSuccess(self):
        """Tests that onSignal event successfully updates portfolio and updates realized capital."""
        # Create signal event.
        event = signalEvent.SignalEvent()
        event.createEvent([self.__strangleObj, self.riskManagement])

        # Test portfolio onSignal event.
        self.__portfolioObj.onSignal(event)

        # Check that positions array in portfolio is not empty.
        self.assertEqual(len(self.__portfolioObj.activePositions), 1)
        self.assertAlmostEqual(self.__portfolioObj.realizedCapital, self.__portfolioObj.startingCapital - (
            self.__strangleObj.getOpeningFees() * self.__strangleObj.getNumContracts()))

    def testOnSignalReturnsEmpty(self):
        """Tests that activePositions has length 0 if eventData is empty."""
        event = signalEvent.SignalEvent()
        self.__portfolioObj.onSignal(event)
        self.assertEqual(len(self.__portfolioObj.activePositions), 0)

    def testUpdatePortfolioSuccess(self):
        """Tests the ability to update option values for a position in the portfolio."""
        # Create strangle event.
        event = signalEvent.SignalEvent()
        event.createEvent([self.__strangleObj, self.riskManagement])

        # Create portfolio onSignal event, which adds the position to the portfolio.
        startingCapital = decimal.Decimal(1000000)
        maxCapitalToUse = decimal.Decimal(0.5)
        maxCapitalToUsePerTrade = decimal.Decimal(0.5)
        portfolioObj = portfolio.Portfolio(startingCapital, maxCapitalToUse, maxCapitalToUsePerTrade)
        portfolioObj.onSignal(event)

        # Next, create a strangle with the next days prices and update the portfolio values.
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                         strikePrice=decimal.Decimal(2690), delta=-0.16, gamma=0.01, theta=0.02, vega=0.03,
                         dateTime=datetime.datetime.strptime('01/02/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                         bidPrice=decimal.Decimal(6.45), askPrice=decimal.Decimal(6.50),
                         tradePrice=decimal.Decimal(6.475),
                         settlementPrice=decimal.Decimal(6.475))
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                            strikePrice=decimal.Decimal(2855), delta=0.16, gamma=0.01, theta=0.02, vega=0.03,
                            dateTime=datetime.datetime.strptime('01/02/2021', "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                          "%m/%d/%Y"),
                            bidPrice=decimal.Decimal(4.20), askPrice=decimal.Decimal(4.40),
                            tradePrice=decimal.Decimal(4.30), settlementPrice=decimal.Decimal(4.30))

        # Create tick event and update portfolio values.
        testOptionChain = [callOpt, putOpt]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        portfolioObj.updatePortfolio(event)

        # Check that the new portfolio values are correct (e.g., buying power, total delta, total gamma, etc.).
        self.assertAlmostEqual(portfolioObj.totalBuyingPower, decimal.Decimal(49278.8))
        self.assertAlmostEqual(portfolioObj.totalVega, 0.06)
        self.assertAlmostEqual(portfolioObj.totalDelta, 0.0)
        self.assertAlmostEqual(portfolioObj.totalGamma, 0.02)
        self.assertAlmostEqual(portfolioObj.totalTheta, 0.04)
        self.assertAlmostEqual(portfolioObj.netLiquidity, decimal.Decimal(1000197.7416999999999))

    def testUpdatePortfolioNoTickData(self):
        """Tests that portfolio is not updated if no tick data is passed."""
        # Create strangle event.
        event = signalEvent.SignalEvent()
        event.createEvent([self.__strangleObj, self.riskManagement])

        # Create portfolio onSignal event, which adds the position to the portfolio.
        startingCapital = decimal.Decimal(1000000)
        maxCapitalToUse = decimal.Decimal(0.5)
        maxCapitalToUsePerTrade = decimal.Decimal(0.5)
        portfolioObj = portfolio.Portfolio(startingCapital, maxCapitalToUse, maxCapitalToUsePerTrade)
        portfolioObj.onSignal(event)

        # No tick data passed in.
        event = tickEvent.TickEvent()
        portfolioObj.updatePortfolio(event)

        # The number of positions in the portfolio and the realized capital should not change.
        self.assertEqual(len(portfolioObj.activePositions), 1)
        self.assertAlmostEqual(portfolioObj.realizedCapital, portfolioObj.startingCapital - (
            self.__strangleObj.getOpeningFees() * self.__strangleObj.getNumContracts()))

    def testUpdatePortfolioNoPositions(self):
        """Tests that the portfolio remains empty if there are no active positions."""
        # Create portfolio onSignal event, which adds the position to the portfolio.
        startingCapital = decimal.Decimal(1000000)
        maxCapitalToUse = decimal.Decimal(0.5)
        maxCapitalToUsePerTrade = decimal.Decimal(0.5)
        portfolioObj = portfolio.Portfolio(startingCapital, maxCapitalToUse, maxCapitalToUsePerTrade)

        # No tick data passed in.
        event = tickEvent.TickEvent()
        portfolioObj.updatePortfolio(event)

        self.assertEqual(len(portfolioObj.activePositions), 0)

    def testUpdatePortfolioNoMatchingOption(self):
        """Tests that a position is removed from the portfolio if there are not matching options."""
        # Create strangle event.
        event = signalEvent.SignalEvent()
        event.createEvent([self.__strangleObj, self.riskManagement])

        # Create portfolio onSignal event, which adds the position to the portfolio.
        startingCapital = decimal.Decimal(1000000)
        maxCapitalToUse = decimal.Decimal(0.5)
        maxCapitalToUsePerTrade = decimal.Decimal(0.5)
        portfolioObj = portfolio.Portfolio(startingCapital, maxCapitalToUse, maxCapitalToUsePerTrade)
        portfolioObj.onSignal(event)

        # Let's change the strike price (2690->2790) of the putOpt below so that there will be no matching option,
        # and the portfolio cannot be updated.
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                         strikePrice=decimal.Decimal(2790), delta=-0.16, gamma=0.01, theta=0.02, vega=0.03,
                         dateTime=datetime.datetime.strptime('01/02/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                         bidPrice=decimal.Decimal(6.45), askPrice=decimal.Decimal(6.50),
                         tradePrice=decimal.Decimal(6.475),
                         settlementPrice=decimal.Decimal(6.475))
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                            strikePrice=decimal.Decimal(2855), delta=0.16, gamma=0.01, theta=0.02, vega=0.03,
                            dateTime=datetime.datetime.strptime('01/02/2021', "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                          "%m/%d/%Y"),
                            bidPrice=decimal.Decimal(4.20), askPrice=decimal.Decimal(4.40),
                            tradePrice=decimal.Decimal(4.30), settlementPrice=decimal.Decimal(4.30))

        # Create tick event and update portfolio values.
        testOptionChain = [callOpt, putOpt]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        portfolioObj.updatePortfolio(event)

        # Only position in portfolio should be removed since we can't update it.
        self.assertEqual(len(portfolioObj.activePositions), 0)
        self.assertAlmostEqual(portfolioObj.realizedCapital,
                               startingCapital - (
                                   self.__strangleObj.getOpeningFees() + self.__strangleObj.getClosingFees()
                               )*self.__strangleObj.getNumContracts())

    def testUpdatePortfolioRiskManagementHoldToExpiration(self):
        """Tests that the position is removed from the portfolio when expiration occurs."""
        startingCapital = decimal.Decimal(1000000)
        maxCapitalToUse = decimal.Decimal(0.5)
        maxCapitalToUsePerTrade = decimal.Decimal(0.25)
        portfolioObj = portfolio.Portfolio(startingCapital, maxCapitalToUse, maxCapitalToUsePerTrade)

        # Add first position to the portfolio
        event = signalEvent.SignalEvent()
        event.createEvent([self.__strangleObj, self.riskManagement])
        portfolioObj.onSignal(event)
        self.assertEqual(len(portfolioObj.activePositions), 1)

        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2800.00),
                         strikePrice=decimal.Decimal(2700), delta=-0.16, gamma=0.01, theta=0.02, vega=0.03,
                         dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/02/2021', "%m/%d/%Y"),
                         bidPrice=decimal.Decimal(8.00), askPrice=decimal.Decimal(8.50),
                         tradePrice=decimal.Decimal(8.25),
                         settlementPrice=decimal.Decimal(8.25))
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2800.00),
                            strikePrice=decimal.Decimal(3000), delta=0.16, gamma=0.01, theta=0.02, vega=0.03,
                            dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/02/2021',
                                                                          "%m/%d/%Y"),
                            bidPrice=decimal.Decimal(6.00), askPrice=decimal.Decimal(6.50),
                            tradePrice=decimal.Decimal(6.25), settlementPrice=decimal.Decimal(6.25))
        strangleObj = strangle.Strangle(orderQuantity=1, contractMultiplier=100, callOpt=callOpt, putOpt=putOpt,
                                        buyOrSell=optionPrimitive.TransactionType.SELL)
        strangleObj.setOpeningFees(
            strangleObj.getCommissionsAndFees('open', self.pricingSource, self.pricingSourceConfig))
        strangleObj.setClosingFees(
            strangleObj.getCommissionsAndFees('close', self.pricingSource, self.pricingSourceConfig))

        # Add second position to the portfolio.
        event = signalEvent.SignalEvent()
        event.createEvent([strangleObj, self.riskManagement])
        portfolioObj.onSignal(event)
        self.assertEqual(len(portfolioObj.activePositions), 2)

        # Update the portfolio, which should remove the second event. We do not change the prices of putOpt or callOpt.
        testOptionChain = [callOpt, putOpt]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        portfolioObj.updatePortfolio(event)
        # There should be no positions in the portfolio since the first position was removed given that there
        # was no tick data to update it, and the second position was removed since expiration occurred.
        self.assertEqual(len(portfolioObj.activePositions), 0)

    def testOnMultipleSignalSuccess(self):
        """Tests that the portfolio values are correct after multiple trades have been put on."""
        event = signalEvent.SignalEvent()
        event.createEvent([self.__strangleObj, self.riskManagement])

        # Create portfolio onSignal event, which adds the position to the portfolio.
        startingCapital = decimal.Decimal(1000000)
        maxCapitalToUse = decimal.Decimal(0.5)
        maxCapitalToUsePerTrade = decimal.Decimal(0.5)
        portfolioObj = portfolio.Portfolio(startingCapital, maxCapitalToUse, maxCapitalToUsePerTrade)
        portfolioObj.onSignal(event)

        # Add second signal / trade.
        event = signalEvent.SignalEvent()
        event.createEvent([self.__strangleObj, self.riskManagement])
        portfolioObj.onSignal(event)

        # Updates the portfolio to get the buying power, delta values, etc.
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2800.00),
                         strikePrice=decimal.Decimal(2690), delta=-0.16, gamma=0.01, theta=0.02, vega=0.03,
                         dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                         bidPrice=decimal.Decimal(8.00), askPrice=decimal.Decimal(8.50),
                         tradePrice=decimal.Decimal(8.25), settlementPrice=decimal.Decimal(8.25))
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2800.00),
                            strikePrice=decimal.Decimal(2855), delta=0.16, gamma=0.01, theta=0.02, vega=0.03,
                            dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                          "%m/%d/%Y"),
                            bidPrice=decimal.Decimal(6.00), askPrice=decimal.Decimal(6.50),
                            tradePrice=decimal.Decimal(6.25), settlementPrice=decimal.Decimal(6.25))
        testOptionChain = [callOpt, putOpt]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        portfolioObj.updatePortfolio(event)

        self.assertAlmostEqual(portfolioObj.totalBuyingPower, decimal.Decimal(102250.00))
        self.assertAlmostEqual(portfolioObj.totalVega, 0.12)
        self.assertAlmostEqual(portfolioObj.totalDelta, 0.0)
        self.assertAlmostEqual(portfolioObj.totalGamma, 0.04)
        self.assertAlmostEqual(portfolioObj.totalTheta, 0.08)


if __name__ == '__main__':
    unittest.main()
