import unittest
import decimal
import pytz
import queue
from datetime import datetime
from dataHandler import csvData
from events import tickEvent
from optionPrimitives import optionPrimitive
from riskManager import strangleRiskManagement
from strategyManager import StrangleStrat

class TestStrangleStrategy(unittest.TestCase):

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
      riskManagement: Risk management strategy (how to manage the trade; e.g., close, roll, hold to expiration).
      pricingSource -- Used to indicate which brokerage to use for commissions / fees.
      pricingSourceConfigFile -- File path to the JSON config file for commission / fees.

    Optional attributes:
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

    # Create strangle strategy object.
    self.signalEventQueue = queue.Queue()
    self.optCallDelta = 0.16
    self.maxCallDelta = 0.30
    self.optPutDelta = -0.16
    self.maxPutDelta = -0.30
    self.startDateTime = None
    self.buyOrSell = optionPrimitive.TransactionType.SELL
    self.underlyingTicker = 'AAPL'
    self.orderQuantity = 1
    self.contractMultiplier = 100
    self.riskManagement = strangleRiskManagement.StrangleRiskManagement(
      strangleRiskManagement.StrangleManagementStrategyTypes.HOLD_TO_EXPIRATION)
    self.expCycle = StrangleStrat.strategy.ExpirationTypes.MONTHLY
    self.optimalDTE = 45
    self.minimumDTE = 25
    self.minimumROC = 0.001
    self.minCredit = 0.5
    self.maxBidAsk = 0.15
    self.minBuyingPower = None
    self.curStrategy = StrangleStrat.StrangleStrat(self.signalEventQueue, self.optCallDelta, self.maxCallDelta,
                                                   self.optPutDelta, self.maxPutDelta, self.buyOrSell,
                                                   self.underlyingTicker, self.orderQuantity, self.contractMultiplier,
                                                   self.riskManagement, self.pricingSource,
                                                   self.pricingSourceConfigFile, self.expCycle, self.optimalDTE,
                                                   self.minimumDTE, minimumROC=self.minimumROC,
                                                   minCredit=self.minCredit, maxBidAsk=self.maxBidAsk,
                                                   maxCapitalToUsePerTrade=self.minBuyingPower,
                                                   startDateTime=self.startDateTime)
    self.portfolioNetLiquidity = decimal.Decimal(100000)
    self.availableBuyingPower = decimal.Decimal(50000)

  # def testUpdateWithOptimalOptionNonSupportedExpiration(self):
  #   """Tests that no signal event is created if we choose an unsupported expiration."""
  #   expCycle = StrangleStrat.strategy.ExpirationTypes.QUARTERLY
  #   curStrategy = StrangleStrat.StrangleStrat(self.signalEventQueue, self.optCallDelta, self.maxCallDelta,
  #                                             self.optPutDelta, self.maxPutDelta, self.buyOrSell, self.underlyingTicker,
  #                                             self.orderQuantity, self.contractMultiplier, self.riskManagement,
  #                                             self.pricingSource, self.pricingSourceConfigFile, expCycle,
  #                                             self.optimalDTE, self.minimumDTE, minimumROC=self.minimumROC,
  #                                             minCredit=self.minCredit, maxBidAsk=self.maxBidAsk,
  #                                             maxCapitalToUsePerTrade=self.minBuyingPower,
  #                                             startDateTime=self.startDateTime)
  #   curStrategy.checkForSignal(self.optionChain, self.portfolioNetLiquidity, self.availableBuyingPower)
  #   self.assertEqual(self.signalEventQueue.qsize(), 0)

  # def testUpdateWithOptimalOptionNotMonthlyExpiration(self):
  #   """Tests that no signal event is created if we do not have a monthly expiration."""
  #   # These options do not have a monthly expiration.
  #   testOptionChain = [self.optionChain.getData()[0], self.optionChain.getData()[1]]
  #   event = tickEvent.TickEvent()
  #   event.createEvent(testOptionChain)
  #   self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower)
  #   self.assertEqual(self.signalEventQueue.qsize(), 0)

  def testUpdateWithOptimalOptionDTELessThanMinimum(self):
    """Tests that no signal event is created if the number of days to expiration is less than minimum."""
    callOption = self.optionChain.getData()[0]
    putOption = self.optionChain.getData()[1]
    # Modify expiration to be a monthly expiration, but set the number of days such that it is less than
    # self.minimumDTE.
    callOption.expirationDateTime = datetime.fromisoformat('2014-08-15')
    putOption.expirationDateTime = datetime.fromisoformat('2014-08-15')
    testOptionChain = [callOption, putOption]
    event = tickEvent.TickEvent()
    event.createEvent(testOptionChain)
    self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower)
    self.assertEqual(self.signalEventQueue.qsize(), 0)

  def testUpdateWithOptimalOptionDeltaGreaterThanMaxCallDelta(self):
    """Tests that no signal event is created if the call delta is greater than the max delta."""
    callOption = self.optionChain.getData()[0]
    putOption = self.optionChain.getData()[1]
    # Set expiration to be monthly and less than self.minimumDTE.
    callOption.expirationDateTime = datetime.fromisoformat('2014-09-19')
    putOption.expirationDateTime = datetime.fromisoformat('2014-09-19')
    # Modify delta of call option to be greater than max delta.
    callOption.delta = self.maxCallDelta*2
    putOption.delta = self.optPutDelta
    testOptionChain = [callOption, putOption]
    event = tickEvent.TickEvent()
    event.createEvent(testOptionChain)
    self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower)
    self.assertEqual(self.signalEventQueue.qsize(), 0)

  def testUpdateWithOptimalOptionDeltaGreaterThanMaxPutDelta(self):
    """Tests that no signal event is created if the put delta is greater than the max delta."""
    callOption = self.optionChain.getData()[0]
    putOption = self.optionChain.getData()[1]
    # Set expiration to be monthly and less than self.minimumDTE.
    callOption.expirationDateTime = datetime.fromisoformat('2014-09-19')
    putOption.expirationDateTime = datetime.fromisoformat('2014-09-19')
    # Modify delta of put option to be greater than max delta.
    putOption.delta = self.maxPutDelta * 2
    callOption.delta = self.optCallDelta
    testOptionChain = [callOption, putOption]
    event = tickEvent.TickEvent()
    event.createEvent(testOptionChain)
    self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower)
    self.assertEqual(self.signalEventQueue.qsize(), 0)

  def testUpdateWithOptimalOptionBidAskDiffGreaterThanMax(self):
    """Tests that no signal event is created if the bid/ask difference is greater than the max bid/ask."""
    callOption = self.optionChain.getData()[0]
    putOption = self.optionChain.getData()[1]
    # Set expiration to be monthly and less than self.minimumDTE.
    callOption.expirationDateTime = datetime.fromisoformat('2014-09-19')
    putOption.expirationDateTime = datetime.fromisoformat('2014-09-19')
    # Set put and call delta to be the desired values.
    putOption.delta = self.optPutDelta
    callOption.delta = self.optCallDelta
    # Set the bidPrice and askPrice such that the difference is greater than self.maxBidAsk.
    putOption.bidPrice = 0.00
    putOption.askPrice = self.maxBidAsk*2
    callOption.bidPrice = 0.00
    callOption.askPrice = self.maxBidAsk
    testOptionChain = [callOption, putOption]
    event = tickEvent.TickEvent()
    event.createEvent(testOptionChain)
    self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower)
    self.assertEqual(self.signalEventQueue.qsize(), 0)

  def testUpdateWithOptimalOptionChooseCloserExpiration(self):
    """Tests that we choose the option with the expiration date closer to self.optimalDTE."""
    callOptionNonOptimalDTE = self.optionChain.getData()[0]
    callOptionOptimalDTE = self.optionChain.getData()[2]
    putOptionNonOptimalDTE = self.optionChain.getData()[1]
    putOptionOptimalDTE = self.optionChain.getData()[3]

    # Set expiration to be monthly and less than self.minimumDTE.
    callOptionNonOptimalDTE.expirationDateTime = datetime.fromisoformat('2014-10-17')
    callOptionOptimalDTE.expirationDateTime = datetime.fromisoformat('2014-09-19')
    putOptionNonOptimalDTE.expirationDateTime = datetime.fromisoformat('2014-10-17')
    putOptionOptimalDTE.expirationDateTime = datetime.fromisoformat('2014-09-19')

    # Set put and call delta. We use these delta values to check that the options with the optimal DTE
    # were chosen.
    callOptionNonOptimalDTE.delta = self.optCallDelta
    callOptionOptimalDTE.delta = 0.20
    putOptionNonOptimalDTE.delta = self.optPutDelta
    putOptionOptimalDTE.delta = -0.10

    # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
    epsilon = 0.001
    callOptionNonOptimalDTE.bidPrice = decimal.Decimal(0.00)
    callOptionNonOptimalDTE.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
    callOptionOptimalDTE.bidPrice = decimal.Decimal(0.00)
    callOptionOptimalDTE.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
    putOptionNonOptimalDTE.bidPrice = decimal.Decimal(0.00)
    putOptionNonOptimalDTE.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
    putOptionOptimalDTE.bidPrice = decimal.Decimal(0.00)
    putOptionOptimalDTE.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)

    testOptionChain = [callOptionNonOptimalDTE, putOptionNonOptimalDTE, callOptionOptimalDTE, putOptionOptimalDTE]
    event = tickEvent.TickEvent()
    event.createEvent(testOptionChain)
    self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower)
    strangleObj = self.signalEventQueue.get().getData()[0]
    expectedNumContracts = 5
    self.assertAlmostEqual(strangleObj.getDelta(), expectedNumContracts*(callOptionOptimalDTE.delta +
                                                                         putOptionOptimalDTE.delta))

  def testUpdateWithOptimalOptionChooseCloserDelta(self):
    """Tests that if options have the same DTE, chose option with the delta closer to requested delta."""
    callOptionNonOptimalDelta = self.optionChain.getData()[0]
    callOptionOptimalDelta = self.optionChain.getData()[2]
    putOptionNonOptimalDelta = self.optionChain.getData()[1]
    putOptionOptimalDelta = self.optionChain.getData()[3]

    # Set expiration to be the same, monthly, and less than self.minimumDTE.
    callOptionNonOptimalDelta.expirationDateTime = datetime.fromisoformat('2014-09-19')
    callOptionOptimalDelta.expirationDateTime = datetime.fromisoformat('2014-09-19')
    putOptionNonOptimalDelta.expirationDateTime = datetime.fromisoformat('2014-09-19')
    putOptionOptimalDelta.expirationDateTime = datetime.fromisoformat('2014-09-19')

    # Set put and call delta. We use these delta values to check that the options with the optimal DTE
    # were chosen.
    callOptionNonOptimalDelta.delta = 0.20
    callOptionOptimalDelta.delta = self.optCallDelta
    putOptionNonOptimalDelta.delta = -0.10
    putOptionOptimalDelta.delta = self.optPutDelta

    # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
    epsilon = 0.001
    callOptionNonOptimalDelta.bidPrice = decimal.Decimal(0.00)
    callOptionNonOptimalDelta.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
    callOptionOptimalDelta.bidPrice = decimal.Decimal(0.00)
    callOptionOptimalDelta.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
    putOptionNonOptimalDelta.bidPrice = decimal.Decimal(0.00)
    putOptionNonOptimalDelta.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
    putOptionOptimalDelta.bidPrice = decimal.Decimal(0.00)
    putOptionOptimalDelta.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)

    testOptionChain = [callOptionNonOptimalDelta, putOptionNonOptimalDelta, callOptionOptimalDelta,
                       putOptionOptimalDelta]
    event = tickEvent.TickEvent()
    event.createEvent(testOptionChain)
    self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower)
    strangleObj = self.signalEventQueue.get().getData()[0]
    self.assertAlmostEqual(strangleObj.getDelta(), callOptionOptimalDelta.delta + putOptionOptimalDelta.delta)

  def testUpdateWithOptimalOptionCurrentOptionHasFurtherDTE(self):
    """Tests second put[3] and call[2] options are not chosen as the optimal options because their deltas are further
    from the requested delta. All put and call options have the same expiration."""
    callOptionOptimalDelta = self.optionChain.getData()[0]
    callOptionNonOptimalDelta = self.optionChain.getData()[2]
    putOptionOptimalDelta = self.optionChain.getData()[1]
    putOptionNonOptimalDelta = self.optionChain.getData()[3]

    # Set expiration to be the same, monthly, and less than self.minimumDTE.
    callOptionOptimalDelta.expirationDateTime = datetime.fromisoformat('2014-09-19')
    callOptionNonOptimalDelta.expirationDateTime = datetime.fromisoformat('2014-09-19')
    putOptionOptimalDelta.expirationDateTime = datetime.fromisoformat('2014-09-19')
    putOptionNonOptimalDelta.expirationDateTime = datetime.fromisoformat('2014-09-19')

    # Set put and call delta. We use these delta values to check that the options with the optimal DTE
    # were chosen.
    callOptionOptimalDelta.delta = self.optCallDelta
    callOptionNonOptimalDelta.delta = 0.05
    putOptionOptimalDelta.delta = self.optPutDelta
    putOptionNonOptimalDelta.delta = -0.1

    # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
    epsilon = 0.001
    callOptionOptimalDelta.bidPrice = decimal.Decimal(0.00)
    callOptionOptimalDelta.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
    callOptionNonOptimalDelta.bidPrice = decimal.Decimal(0.00)
    callOptionNonOptimalDelta.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
    putOptionOptimalDelta.bidPrice = decimal.Decimal(0.00)
    putOptionOptimalDelta.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
    putOptionNonOptimalDelta.bidPrice = decimal.Decimal(0.00)
    putOptionNonOptimalDelta.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)

    testOptionChain = [callOptionOptimalDelta, putOptionOptimalDelta, callOptionNonOptimalDelta,
                       putOptionNonOptimalDelta]
    event = tickEvent.TickEvent()
    event.createEvent(testOptionChain)
    self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower)
    strangleObj = self.signalEventQueue.get().getData()[0]
    self.assertAlmostEqual(strangleObj.getDelta(), callOptionOptimalDelta.delta + putOptionOptimalDelta.delta)

  def testCheckForSignalCallAndPutWithDifferentExpirations(self):
    """Tests that no signal event is created if put and call options have different expirations."""
    callOption = self.optionChain.getData()[0]
    putOption = self.optionChain.getData()[1]
    # Set expiration to be monthly and less than self.minimumDTE.
    callOption.expirationDateTime = datetime.fromisoformat('2014-09-19')
    putOption.expirationDateTime = datetime.fromisoformat('2014-10-17')
    # Set put and call delta to be the desired values.
    putOption.delta = self.optPutDelta
    callOption.delta = self.optCallDelta
    # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
    putOption.bidPrice = 0.00
    putOption.askPrice = self.maxBidAsk
    callOption.bidPrice = 0.00
    callOption.askPrice = self.maxBidAsk
    testOptionChain = [callOption, putOption]
    event = tickEvent.TickEvent()
    event.createEvent(testOptionChain)
    self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower)
    self.assertEqual(self.signalEventQueue.qsize(), 0)

if __name__ == '__main__':
    unittest.main()
