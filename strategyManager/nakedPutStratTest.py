# TODO(msantoro): Modify this to support naked puts.
import unittest
import decimal
import queue
from datetime import datetime
from dataHandler import csvData
from events import tickEvent
from riskManager import strangleRiskManagement
from strategyManager import strategy, nakedPutStrat

class TestShortNakedPutStrategy(unittest.TestCase):

  def setUp(self):
    """Create instance of short naked put strategy.

    Specific strategy attributes:
      optPutToSellDelta:  Optimal delta for the put to sell.
      maxPutToSellDelta:  Maximum delta for the put to sell.
      minPutToSellDelta:  Minimum delta for the put to sell.

    General strategy attributes:
      startDateTime:  Date/time to start the live trading or backtest.
      underlyingTicker:  Which underlying to use for the strategy.
      orderQuantity:  Number of naked puts to sell.
      riskManager: Risk management strategy (how to manage the trade; e.g., close, roll, hold to expiration).

    Optional attributes:
      expCycle:  Specifies if we want to do monthly, weekly, quarterly, etc.
      optimalDTE:  Optimal number of days before expiration to put on strategy.
      minimumDTE:  Minimum number of days before expiration to put on strategy.
      minimumROC:  Minimal return on capital for overall trade as a decimal.
      minCredit:  Minimum credit to collect on overall trade.
      maxBidAsk:  Maximum price to allow between bid and ask prices of option (for any strike or put/call).
      minBuyingPower:  Minimum investment we want for the strategy -- since prices vary greatly over a range like
                       1990 to 2017, we would like to have the same amount of money in the market at any given
                       time, so we increase the number of contracts to reach this minBuyingPower.
    """
    # Use CSV data source to test.
    tickEventQueue = queue.Queue()
    dataProvider = 'iVolatility'
    filename = '/Users/msantoro/PycharmProjects/Backtester/sampleData/aapl_sample_ivolatility.csv'
    csvObj = csvData.CsvData(csvPath=filename, dataProvider=dataProvider, eventQueue=tickEventQueue)
    csvObj.getNextTick()
    self.optionChain = tickEventQueue.get()

    # Set up pricing source info.
    self.pricingSource = 'tastyworks'
    self.pricingSourceConfigFile = '/Users/msantoro/PycharmProjects/Backtester/dataHandler/pricingConfig.json'

    # Create short naked put strategy object.
    self.signalEventQueue = queue.Queue()
    self.optPutToSellDelta = -0.16
    self.maxPutToSellDelta = -0.18
    self.minPutToSellDelta = -0.12
    self.underlyingTicker = 'SPX'
    self.orderQuantity = 1
    self.contractMultiplier = 100
    self.riskManagement = strangleRiskManagement.StrangleRiskManagement(
      strangleRiskManagement.StrangleManagementStrategyTypes.HOLD_TO_EXPIRATION)
    self.expCycle = strategy.ExpirationTypes.MONTHLY
    self.optimalDTE = 45
    self.minimumDTE = 25
    self.maxBidAsk = 0.15
    self.maxCapitalToUsePerTrade = 0.10  # 10% max capital to use per trade / strategy.
    self.curStrategy = nakedPutStrat.NakedPutStrat(self.signalEventQueue, self.optPutToSellDelta,
                                                   self.maxPutToSellDelta, self.minPutToSellDelta,
                                                   self.underlyingTicker, self.orderQuantity, self.contractMultiplier,
                                                   self.riskManagement, self.pricingSource,
                                                   self.pricingSourceConfigFile, self.expCycle, self.optimalDTE,
                                                   self.minimumDTE, maxBidAsk=self.maxBidAsk,
                                                   maxCapitalToUsePerTrade=self.maxCapitalToUsePerTrade)
    self.portfolioNetLiquidity = decimal.Decimal(100000)
    self.availableBuyingPower = decimal.Decimal(50000)

  def testUpdateWithOptimalOptionNotMonthlyExpiration(self):
    """Tests that no signal event is created if we do not have a monthly expiration."""
    # These options do not have a monthly expiration.
    testOptionChain = [self.optionChain.getData()[1]]
    event = tickEvent.TickEvent()
    event.createEvent(testOptionChain)
    self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower)
    self.assertEqual(self.signalEventQueue.qsize(), 0)

  def testUpdateWithOptimalOptionDTELessThanMinimum(self):
    """Tests that no signal event is created if the number of days to expiration is less than minimum."""
    putOption = self.optionChain.getData()[1]
    # Modify expiration to be a monthly expiration, but set the number of days such that it is less than
    # self.minimumDTE.
    putOption.expirationDateTime = datetime.fromisoformat('2014-08-15')
    testOptionChain = [putOption]
    event = tickEvent.TickEvent()
    event.createEvent(testOptionChain)
    self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower)
    self.assertEqual(self.signalEventQueue.qsize(), 0)

  def testUpdateWithOptimalOptionDeltaGreaterThanMaxPutDelta(self):
    """Tests that no signal event is created if the put delta is greater than the max delta."""
    putOptionToSell = self.optionChain.getData()[1]
    # Set expiration to be monthly and less than self.minimumDTE.
    putOptionToSell.expirationDateTime = datetime.fromisoformat('2014-09-19')
    # Modify delta of put option to be greater than max delta.
    putOptionToSell.delta = self.maxPutToSellDelta * 2
    testOptionChain = [putOptionToSell]
    event = tickEvent.TickEvent()
    event.createEvent(testOptionChain)
    self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower)
    self.assertEqual(self.signalEventQueue.qsize(), 0)

  def testUpdateWithOptimalOptionBidAskDiffGreaterThanMax(self):
    """Tests that no signal event is created if the bid/ask difference is greater than the max bid/ask."""
    putOptionToSell = self.optionChain.getData()[1]
    # Set expiration to be monthly and less than self.minimumDTE.
    putOptionToSell.expirationDateTime = datetime.fromisoformat('2014-09-19')
    # Set put deltas to be the desired values.
    putOptionToSell.delta = self.optPutToSellDelta
    # Set the bidPrice and askPrice such that the difference is greater than self.maxBidAsk.
    putOptionToSell.bidPrice = 0.00
    putOptionToSell.askPrice = self.maxBidAsk*2
    testOptionChain = [putOptionToSell]
    event = tickEvent.TickEvent()
    event.createEvent(testOptionChain)
    self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower)
    self.assertEqual(self.signalEventQueue.qsize(), 0)

  def testUpdateWithOptimalOptionChooseCloserExpiration(self):
    """Tests that we choose the option with the expiration date closer to self.optimalDTE."""
    putOptionToSellNonOptimalDTE = self.optionChain.getData()[5]
    putOptionToSellOptimalDTE = self.optionChain.getData()[7]

    # Set expiration to be monthly and less than self.minimumDTE.
    putOptionToSellNonOptimalDTE.expirationDateTime = datetime.fromisoformat('2014-10-17')
    putOptionToSellOptimalDTE.expirationDateTime = datetime.fromisoformat('2014-09-19')

    # Set put deltas. We use these delta values to check that the options with the optimal DTE were chosen.
    putOptionToSellNonOptimalDTE.delta = self.maxPutToSellDelta
    putOptionToSellOptimalDTE.delta = self.optPutToSellDelta

    # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
    epsilon = 0.001
    putOptionToSellNonOptimalDTE.bidPrice = decimal.Decimal(0.00)
    putOptionToSellNonOptimalDTE.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
    putOptionToSellOptimalDTE.bidPrice = decimal.Decimal(0.00)
    putOptionToSellOptimalDTE.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)

    testOptionChain = [putOptionToSellNonOptimalDTE, putOptionToSellOptimalDTE]
    event = tickEvent.TickEvent()
    event.createEvent(testOptionChain)
    self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower)
    shortNakedPutObj = self.signalEventQueue.get().getData()[0]
    # We use delta to check since we can't access the expiration date from shortNakedPutObj.
    self.assertAlmostEqual(shortNakedPutObj.getDelta(),
                           shortNakedPutObj.getNumContracts()*putOptionToSellOptimalDTE.delta)

  def testUpdateWithOptimalOptionChooseCloserDelta(self):
    """Tests that if options have the same DTE, chose option with the delta closer to requested delta."""
    putOptionToSellNonOptimalDelta = self.optionChain.getData()[5]
    putOptionToSellOptimalDelta = self.optionChain.getData()[7]

    # Set expiration to be the same, monthly, and less than self.minimumDTE.
    putOptionToSellNonOptimalDelta.expirationDateTime = datetime.fromisoformat('2014-09-19')
    putOptionToSellOptimalDelta.expirationDateTime = datetime.fromisoformat('2014-09-19')

    # Set put deltas. We use these delta values to check that the options with the optimal DTE were chosen.
    putOptionToSellNonOptimalDelta.delta = -0.19
    putOptionToSellOptimalDelta.delta = self.optPutToSellDelta

    # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
    epsilon = 0.001
    putOptionToSellNonOptimalDelta.bidPrice = decimal.Decimal(0.00)
    putOptionToSellNonOptimalDelta.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
    putOptionToSellOptimalDelta.bidPrice = decimal.Decimal(0.00)
    putOptionToSellOptimalDelta.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)

    testOptionChain = [putOptionToSellNonOptimalDelta, putOptionToSellOptimalDelta]
    event = tickEvent.TickEvent()
    event.createEvent(testOptionChain)
    self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower)
    shortNakedPutObj = self.signalEventQueue.get().getData()[0]
    self.assertAlmostEqual(shortNakedPutObj.getDelta(),
                           shortNakedPutObj.getNumContracts()*putOptionToSellOptimalDelta.delta)

  def testCheckForSignalPutsWithDifferentExpirations(self):
    """Tests that no signal event is created if put options have different expirations."""
    putOptionToSell = self.optionChain.getData()[1]
    # Set expiration to be monthly and less than self.minimumDTE.
    putOptionToSell.expirationDateTime = datetime.fromisoformat('2014-09-19')
    # Set put and call delta to be the desired values.
    putOptionToSell.delta = self.optPutToSellDelta
    # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
    putOptionToSell.bidPrice = decimal.Decimal(0.00)
    putOptionToSell.askPrice = decimal.Decimal(self.maxBidAsk)
    testOptionChain = [putOptionToSell]
    event = tickEvent.TickEvent()
    event.createEvent(testOptionChain)
    self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower)
    self.assertEqual(self.signalEventQueue.qsize(), 0)

if __name__ == '__main__':
    unittest.main()
