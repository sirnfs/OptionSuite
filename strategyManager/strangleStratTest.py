import unittest
import decimal
import queue
from datetime import datetime, timedelta
from dataHandler import csvData
from events import tickEvent
from optionPrimitives import optionPrimitive
from riskManager import strangleRiskManagement
from strategyManager import StrangleStrat


class TestStrangleStrategy(unittest.TestCase):

    def setUp(self):
        """Create instance of strangle strategy
        Strangle specific attributes:
          optCallDelta:  Optimal delta for call.
          maxCallDelta:  Max delta for call.
          minCallDelta: Min delta for call
          optPutDelta:  Optimal delta for put.
          maxPutDelta:  Max delta for put.
          minPutDelta: Min delta for put.

        General strategy attributes:
          startDateTime:  Date/time to start the live trading or backtest.
          buyOrSell:  Do we buy an iron condor or sell an iron condor? 0 = buy, 1 = sell.
          underlyingTicker:  Which underlying to use for the strategy.
          orderQuantity:  Number of strangles, iron condors, etc.
          contractMultiplier: scaling factor for number of "shares" represented by an option or future. (E.g. 100 for options
                              and 50 for ES futures options).
          riskManagement: Risk management strategy (how to manage the trade; e.g., close, roll, hold to expiration).
          pricingSource -- Used to indicate which brokerage to use for commissions / fees.
          pricingSourceConfigFile -- File path to the JSON config file for commission / fees.

        Optional attributes:
          optimalDTE:  Optimal number of days before expiration to put on strategy.
          minimumDTE:  Minimum number of days before expiration to put on strategy.
          maximumDTE: Maximum days to expiration to put on strategy.
          maxBidAsk:  Maximum price to allow between bid and ask prices of option (for any strike or put/call).
          maxCapitalToUsePerTrade: percent (as a decimal) of portfolio value we want to use per trade.
        """
        # Use CSV data source to test.
        tickEventQueue = queue.Queue()
        dataProvider = 'iVolatility'
        dataProviderPath = 'dataHandler/dataProviders.json'
        csvPath = 'sampleData/aapl_sample_ivolatility.csv'
        csvObj = csvData.CsvData(csvPath=csvPath, dataProviderPath=dataProviderPath, dataProvider=dataProvider,
                                 eventQueue=tickEventQueue)
        csvObj.getNextTick()
        self.optionChain = tickEventQueue.get()

        # Set up pricing source info.
        self.pricingSource = 'tastyworks'
        self.pricingSourceConfigFile = 'dataHandler/pricingConfig.json'

        # Create strangle strategy object.
        self.signalEventQueue = queue.Queue()
        self.optCallDelta = 0.16
        self.maxCallDelta = 0.30
        self.minCallDelta = 0.10
        self.optPutDelta = -0.16
        self.maxPutDelta = -0.30
        self.minPutDelta = -0.10
        self.buyOrSell = optionPrimitive.TransactionType.SELL
        self.underlyingTicker = 'AAPL'
        self.orderQuantity = 1
        self.contractMultiplier = 100
        self.riskManagement = strangleRiskManagement.StrangleRiskManagement(
            strangleRiskManagement.StrangleManagementStrategyTypes.HOLD_TO_EXPIRATION)
        self.optimalDTE = 45
        self.minimumDTE = 25
        self.maximumDTE = 65
        self.maxBidAsk = decimal.Decimal(0.15)
        self.maxCapitalToUsePerTrade = decimal.Decimal(0.10)  # 10% max capital to use per trade / strategy.
        # This date is before we have any options data in the CSV files in sampleData.
        self.startDateTime = datetime.fromisoformat('2014-08-07')
        self.curStrategy = StrangleStrat.StrangleStrat(self.signalEventQueue, self.optCallDelta, self.maxCallDelta,
                                                       self.minCallDelta, self.optPutDelta, self.maxPutDelta,
                                                       self.minPutDelta, self.buyOrSell, self.underlyingTicker,
                                                       self.orderQuantity, self.contractMultiplier, self.riskManagement,
                                                       self.pricingSource, self.pricingSourceConfigFile,
                                                       self.optimalDTE, self.minimumDTE, self.maximumDTE,
                                                       maxBidAsk=self.maxBidAsk,
                                                       maxCapitalToUsePerTrade=self.maxCapitalToUsePerTrade,
                                                       startDateTime=self.startDateTime)
        self.portfolioNetLiquidity = decimal.Decimal(1000000)
        self.availableBuyingPower = decimal.Decimal(500000)

    def testCheckForSignalNoEventData(self):
        """Tests that nothing is returned if there was no tick event data."""
        event = tickEvent.TickEvent()
        event.createEvent(None)
        self.assertIsNone(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower))

    def testStartTimeLessThanCurrentDateTime(self):
        """Tests that nothing is returned if the start time is before the current date / time."""
        startDateTime = datetime.fromisoformat('2016-08-07')
        curStrategy = StrangleStrat.StrangleStrat(self.signalEventQueue, self.optCallDelta, self.maxCallDelta,
                                                  self.minCallDelta, self.optPutDelta, self.maxPutDelta,
                                                  self.minPutDelta, self.buyOrSell, self.underlyingTicker,
                                                  self.orderQuantity, self.contractMultiplier, self.riskManagement,
                                                  self.pricingSource, self.pricingSourceConfigFile,
                                                  self.optimalDTE, self.minimumDTE, maxBidAsk=self.maxBidAsk,
                                                  maxCapitalToUsePerTrade=self.maxCapitalToUsePerTrade,
                                                  startDateTime=startDateTime)
        callOption = self.optionChain.getData()[0]
        putOption = self.optionChain.getData()[1]
        testOptionChain = [callOption, putOption]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        self.assertIsNone(curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower))

    def testUpdateWithOptimalOptionWrongTickerSymbol(self):
        """Tests that the signal event returns WRONG_TICKER NoUpdateReason since the current option has wrong ticker."""
        callOption = self.optionChain.getData()[0]
        putOption = self.optionChain.getData()[1]
        # Change ticker symbol.
        callOption.underlyingTicker = 'FAKE'
        putOption.underlyingTicker = 'FAKE'
        testOptionChain = [callOption, putOption]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        expectedReason = {'callOption': StrangleStrat.NoUpdateReason.WRONG_TICKER,
                          'putOption': StrangleStrat.NoUpdateReason.WRONG_TICKER}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)

    def testUpdateWithOptimalOptionDeltaIsNone(self):
        """Tests that the signal event returns NO_DELTA NoUpdateReason since the current option has a None delta."""
        callOption = self.optionChain.getData()[0]
        putOption = self.optionChain.getData()[1]
        # Change delta to None.
        callOption.delta = None
        putOption.delta = None
        testOptionChain = [callOption, putOption]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        expectedReason = {'callOption': StrangleStrat.NoUpdateReason.NO_DELTA,
                          'putOption': StrangleStrat.NoUpdateReason.NO_DELTA}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)

    def testUpdateWithOptimalOptionSettlementPriceIsNone(self):
        """Tests that the signal event returns NO_SETTLEMENT_PRICE since current option has None settlement price."""
        callOption = self.optionChain.getData()[0]
        putOption = self.optionChain.getData()[1]
        # Change settlement price to None.
        callOption.settlementPrice = None
        putOption.settlementPrice = None
        testOptionChain = [callOption, putOption]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        expectedReason = {'callOption': StrangleStrat.NoUpdateReason.NO_SETTLEMENT_PRICE,
                          'putOption': StrangleStrat.NoUpdateReason.NO_SETTLEMENT_PRICE}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)

    def testUpdateWithOptimalOptionDTELessThanMinimum(self):
        """Tests that the signal event returns MIN_DTE NoUpdateReason since the current option is below MIN_DTE."""
        callOption = self.optionChain.getData()[0]
        putOption = self.optionChain.getData()[1]
        # Set the number of days such that it is less than self.minimumDTE.
        callOption.expirationDateTime = callOption.dateTime + timedelta(days=(self.minimumDTE - 1))
        putOption.expirationDateTime = putOption.dateTime + timedelta(days=(self.minimumDTE - 1))
        testOptionChain = [callOption, putOption]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        expectedReason = {'callOption': StrangleStrat.NoUpdateReason.MIN_DTE,
                          'putOption': StrangleStrat.NoUpdateReason.MIN_DTE}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)

    def testUpdateWithOptimalOptionDTEGreaterThanMaximum(self):
        """Tests that signal event returns MAX_DTE NoUpdateReason since the current option is above MAX_DTE."""
        callOption = self.optionChain.getData()[0]
        putOption = self.optionChain.getData()[1]
        # Set the number of days such that it is greater than self.maximumDTE.
        callOption.expirationDateTime = callOption.dateTime + timedelta(days=(self.maximumDTE + 1))
        putOption.expirationDateTime = putOption.dateTime + timedelta(days=(self.maximumDTE + 1))
        testOptionChain = [callOption, putOption]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        expectedReason = {'callOption': StrangleStrat.NoUpdateReason.MAX_DTE,
                          'putOption': StrangleStrat.NoUpdateReason.MAX_DTE}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)

    def testUpdateWithOptimalOptionDeltaGreaterThanMaxCallDelta(self):
        """Tests that signal event returns MIN_MAX_DELTA NoUpdateReason if call delta > max call delta."""
        callOption = self.optionChain.getData()[0]
        putOption = self.optionChain.getData()[1]
        # Set the number of days such that it is greater than self.minimumDTE.
        callOption.expirationDateTime = callOption.dateTime + timedelta(days=(self.minimumDTE + 1))
        putOption.expirationDateTime = putOption.dateTime + timedelta(days=(self.minimumDTE + 1))
        # Modify delta of call option to be greater than max delta.
        callOption.delta = self.maxCallDelta * 2
        putOption.delta = self.optPutDelta
        testOptionChain = [callOption, putOption]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        expectedReason = {'callOption': StrangleStrat.NoUpdateReason.MIN_MAX_DELTA,
                          'putOption': StrangleStrat.NoUpdateReason.OK}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)

    def testUpdateWithOptimalOptionDeltaGreaterThanMaxPutDelta(self):
        """Tests that signal event returns MIN_MAX_DELTA NoUpdateReason if put delta delta > max put delta."""
        callOption = self.optionChain.getData()[0]
        putOption = self.optionChain.getData()[1]
        # Set the number of days such that it is greater than self.minimumDTE.
        callOption.expirationDateTime = callOption.dateTime + timedelta(days=(self.minimumDTE + 1))
        putOption.expirationDateTime = putOption.dateTime + timedelta(days=(self.minimumDTE + 1))
        # Modify delta of put option to be greater than max delta.
        putOption.delta = self.maxPutDelta * 2
        callOption.delta = self.optCallDelta
        # Make sure that the call option spread isn't greater than max bid ask, or it will show a NoUpdateReason.
        callOption.bidPrice = decimal.Decimal(0.00)
        callOption.askPrice = self.maxBidAsk - decimal.Decimal(0.0001)
        testOptionChain = [callOption, putOption]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        expectedReason = {'putOption': StrangleStrat.NoUpdateReason.MIN_MAX_DELTA,
                          'callOption': StrangleStrat.NoUpdateReason.OK}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)
    def testUpdateWithOptimalOptionBidAskDiffGreaterThanMax(self):
        """Tests that no signal event is created if the bid/ask difference is greater than the max bid/ask."""
        callOption = self.optionChain.getData()[0]
        putOption = self.optionChain.getData()[1]
        # Set expiration to be monthly and less than self.minimumDTE.
        # Set expiration to greater than self.minimumDTE.
        callOption.expirationDateTime = callOption.dateTime + timedelta(days=(self.minimumDTE + 1))
        putOption.expirationDateTime = putOption.dateTime + timedelta(days=(self.minimumDTE + 1))
        # Set put and call delta to be the desired values.
        putOption.delta = self.optPutDelta
        callOption.delta = self.optCallDelta
        # Set the bidPrice and askPrice such that the difference is greater than self.maxBidAsk.
        putOption.bidPrice = decimal.Decimal(0.00)
        putOption.askPrice = self.maxBidAsk * 2
        callOption.bidPrice = decimal.Decimal(0.00)
        callOption.askPrice = self.maxBidAsk * 2
        testOptionChain = [callOption, putOption]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        expectedReason = {'callOption': StrangleStrat.NoUpdateReason.MAX_BID_ASK,
                          'putOption': StrangleStrat.NoUpdateReason.MAX_BID_ASK}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)

    def testUpdateWithOptimalOptionChooseCloserExpiration(self):
        """Tests that we choose the option with the expiration date closer to self.optimalDTE."""
        callOptionNonOptimalDTE = self.optionChain.getData()[0]
        callOptionOptimalDTE = self.optionChain.getData()[2]
        putOptionNonOptimalDTE = self.optionChain.getData()[1]
        putOptionOptimalDTE = self.optionChain.getData()[3]

        # Set expiration to be greater than self.minimumDTE.
        callOptionNonOptimalDTE.expirationDateTime = callOptionNonOptimalDTE.dateTime + timedelta(
            days=(self.minimumDTE + 1))
        callOptionOptimalDTE.expirationDateTime = callOptionOptimalDTE.dateTime + timedelta(
            days=(self.minimumDTE + 2))
        putOptionNonOptimalDTE.expirationDateTime = putOptionNonOptimalDTE.dateTime + timedelta(
            days=(self.minimumDTE + 1))
        putOptionOptimalDTE.expirationDateTime = putOptionOptimalDTE.dateTime + timedelta(
            days=(self.minimumDTE + 2))

        # Set put and call delta. We use these delta values to check that the options with the optimal DTE
        # were chosen.
        callOptionNonOptimalDTE.delta = self.maxCallDelta
        callOptionOptimalDTE.delta = self.optCallDelta
        putOptionNonOptimalDTE.delta = self.maxPutDelta
        putOptionOptimalDTE.delta = self.optPutDelta

        # We can't have the same strike prices or the code to find the optimal options will fail.
        callOptionOptimalDTE.strikePrice = 50
        putOptionOptimalDTE.strikePrice = 25

        # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
        epsilon = decimal.Decimal(0.001)
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
        # We use delta to check since we can't access the expiration date from strangleObj.
        self.assertAlmostEqual(strangleObj.getDelta(), strangleObj.getNumContracts() * (callOptionOptimalDTE.delta +
                                                                                        putOptionOptimalDTE.delta))

    def testUpdateWithOptimalOptionChooseCloserDelta(self):
        """Tests that if options have the same DTE, chose option with the delta closer to requested delta."""
        callOptionNonOptimalDelta = self.optionChain.getData()[0]
        callOptionOptimalDelta = self.optionChain.getData()[2]
        putOptionNonOptimalDelta = self.optionChain.getData()[1]
        putOptionOptimalDelta = self.optionChain.getData()[3]

        # Set expiration to be greater than self.minimumDTE.
        callOptionNonOptimalDelta.expirationDateTime = callOptionNonOptimalDelta.dateTime + timedelta(
            days=(self.minimumDTE + 1))
        callOptionOptimalDelta.expirationDateTime = callOptionOptimalDelta.dateTime + timedelta(
            days=(self.minimumDTE + 1))
        putOptionNonOptimalDelta.expirationDateTime = putOptionNonOptimalDelta.dateTime + timedelta(
            days=(self.minimumDTE + 1))
        putOptionOptimalDelta.expirationDateTime = putOptionOptimalDelta.dateTime + timedelta(
            days=(self.minimumDTE + 1))

        # Set put and call delta. We use these delta values to check that the options with the optimal DTE
        # were chosen.
        callOptionNonOptimalDelta.delta = 0.20
        callOptionOptimalDelta.delta = self.optCallDelta
        putOptionNonOptimalDelta.delta = -0.10
        putOptionOptimalDelta.delta = self.optPutDelta

        # We can't have the same strike prices or the code to find the optimal options will fail.
        callOptionOptimalDelta.strikePrice = 50
        putOptionOptimalDelta.strikePrice = 25

        # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
        epsilon = decimal.Decimal(0.001)
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
        """Tests second put[3] and call[2] options are not chosen as the optimal options because their deltas are
        further from the requested delta. All put and call options have the same expiration."""
        callOptionOptimalDelta = self.optionChain.getData()[0]
        callOptionNonOptimalDelta = self.optionChain.getData()[2]
        putOptionOptimalDelta = self.optionChain.getData()[1]
        putOptionNonOptimalDelta = self.optionChain.getData()[3]

        # Set expiration to be greater than self.minimumDTE.
        callOptionOptimalDelta.expirationDateTime = callOptionOptimalDelta.dateTime + timedelta(
            days=(self.minimumDTE + 1))
        callOptionNonOptimalDelta.expirationDateTime = callOptionNonOptimalDelta.dateTime + timedelta(
            days=(self.minimumDTE + 1))
        putOptionOptimalDelta.expirationDateTime = putOptionOptimalDelta.dateTime + timedelta(
            days=(self.minimumDTE + 1))
        putOptionNonOptimalDelta.expirationDateTime = putOptionNonOptimalDelta.dateTime + timedelta(
            days=(self.minimumDTE + 1))

        # Set put and call delta. We use these delta values to check that the options with the optimal DTE
        # were chosen.
        callOptionOptimalDelta.delta = self.optCallDelta
        callOptionNonOptimalDelta.delta = 0.05
        putOptionOptimalDelta.delta = self.optPutDelta
        putOptionNonOptimalDelta.delta = -0.1

        # We can't have the same strike prices or the code to find the optimal options will fail.
        callOptionOptimalDelta.strikePrice = 50
        putOptionOptimalDelta.strikePrice = 25

        # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
        epsilon = decimal.Decimal(0.001)
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

    def testUpdateWithOptimalOptionSuccess(self):
        """Tests that the options were found successfully according to the strategy."""
        callOption = self.optionChain.getData()[0]
        putOption = self.optionChain.getData()[1]

        # Set expiration to be the same and greater than self.minimumDTE.
        callOption.expirationDateTime = callOption.dateTime + timedelta(
            days=(self.minimumDTE + 1))
        putOption.expirationDateTime = putOption.dateTime + timedelta(
            days=(self.minimumDTE + 1))

        # Set put deltas. We use these delta values to check that the options with the optimal DTE were chosen.
        callOption.delta = self.optCallDelta
        putOption.delta = self.optPutDelta

        # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
        epsilon = decimal.Decimal(0.001)
        callOption.bidPrice = decimal.Decimal(0.00)
        callOption.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        putOption.bidPrice = decimal.Decimal(0.00)
        putOption.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)

        testOptionChain = [callOption, putOption]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        expectedReason = {'callOption': StrangleStrat.NoUpdateReason.OK,
                          'putOption': StrangleStrat.NoUpdateReason.OK}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)

    def testCheckForSignalTotalDebitCreditLessThanMinCredit(self):
        """Tests that no signal event is created when the debit/credit is less than minCreditDebit."""
        callOption = self.optionChain.getData()[0]
        putOption = self.optionChain.getData()[1]

        # Set expiration to be the same and greater than self.minimumDTE.
        callOption.expirationDateTime = callOption.dateTime + timedelta(
            days=(self.minimumDTE + 1))
        putOption.expirationDateTime = putOption.dateTime + timedelta(
            days=(self.minimumDTE + 1))

        # Set put deltas. We use these delta values to check that the options with the optimal DTE were chosen.
        callOption.delta = self.optCallDelta
        putOption.delta = self.optPutDelta

        # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
        epsilon = decimal.Decimal(0.001)
        callOption.bidPrice = decimal.Decimal(0.00)
        callOption.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        putOption.bidPrice = decimal.Decimal(0.00)
        putOption.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)

        testOptionChain = [callOption, putOption]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)

        # Set minCreditDebit to a large number to test that creation of the strategy fails.
        curStrategy = StrangleStrat.StrangleStrat(self.signalEventQueue, self.optCallDelta, self.maxCallDelta,
                                                  self.minCallDelta, self.optPutDelta, self.maxPutDelta,
                                                  self.minPutDelta, self.buyOrSell, self.underlyingTicker,
                                                  self.orderQuantity, self.contractMultiplier, self.riskManagement,
                                                  self.pricingSource, self.pricingSourceConfigFile,
                                                  self.optimalDTE, self.minimumDTE, maxBidAsk=self.maxBidAsk,
                                                  maxCapitalToUsePerTrade=self.maxCapitalToUsePerTrade,
                                                  startDateTime=self.startDateTime, minCreditDebit=1000)


        curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower)
        self.assertEqual(self.signalEventQueue.qsize(), 0)

    def testCheckForSignalNumContractLessThanOne(self):
        """Tests that no signal event is created when the number of contracts is less than one."""
        callOption = self.optionChain.getData()[0]
        putOption = self.optionChain.getData()[1]

        # Set expiration to greater than self.minimumDTE.
        callOption.expirationDateTime = callOption.dateTime + timedelta(days=(self.minimumDTE + 1))
        putOption.expirationDateTime = putOption.dateTime + timedelta(days=(self.minimumDTE + 2))

        # Set put and call delta to be the desired values.
        callOption.delta = self.optCallDelta
        putOption.delta = self.optPutDelta

        # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
        epsilon = decimal.Decimal(0.001)
        callOption.bidPrice = decimal.Decimal(0.00)
        callOption.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        putOption.bidPrice = decimal.Decimal(0.00)
        putOption.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        testOptionChain = [callOption, putOption]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)

        # The expected reason will still be OK since the filter happens later in checkForSignal.
        expectedReason = {'callOption': StrangleStrat.NoUpdateReason.OK,
                          'putOption': StrangleStrat.NoUpdateReason.OK}

        # Set available buying power to zero such that number of contracts will be less than one.
        availableBuyingPower = decimal.Decimal(0.00)
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, availableBuyingPower),
                         expectedReason)
        self.assertEqual(self.signalEventQueue.qsize(), 0)

    def testCheckForSignalCallAndPutWithDifferentExpirations(self):
        """Tests that no signal event is created if put and call options have different expirations."""
        callOption = self.optionChain.getData()[0]
        putOption = self.optionChain.getData()[1]

        # Set expiration to be greater than self.minimumDTE.
        callOption.expirationDateTime = callOption.dateTime + timedelta(days=(self.minimumDTE + 1))
        putOption.expirationDateTime = putOption.dateTime + timedelta(days=(self.minimumDTE + 2))

        # Set put and call delta to be the desired values.
        putOption.delta = self.optPutDelta
        callOption.delta = self.optCallDelta

        # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
        epsilon = decimal.Decimal(0.001)
        putOption.bidPrice = decimal.Decimal(0.00)
        putOption.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        callOption.bidPrice = decimal.Decimal(0.00)
        callOption.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        testOptionChain = [callOption, putOption]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)

        # The expected reason will still be OK since the filter happens later in checkForSignal.
        expectedReason = {'callOption': StrangleStrat.NoUpdateReason.OK,
                          'putOption': StrangleStrat.NoUpdateReason.OK}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)
        self.assertEqual(self.signalEventQueue.qsize(), 0)

    def testCheckForSignalPutsWithSameStrikePrice(self):
        """Tests that no signal event is created if put options have same strike prices."""
        callOption = self.optionChain.getData()[0]
        putOption = self.optionChain.getData()[1]

        # Set expiration to greater than self.minimumDTE.
        callOption.expirationDateTime = callOption.dateTime + timedelta(days=(self.minimumDTE + 1))
        putOption.expirationDateTime = putOption.dateTime + timedelta(days=(self.minimumDTE + 1))

        # Set put and call delta to be the desired values.
        callOption.delta = self.optCallDelta
        putOption.delta = self.optPutDelta

        # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
        epsilon = decimal.Decimal(0.001)
        callOption.bidPrice = decimal.Decimal(0.00)
        callOption.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        putOption.bidPrice = decimal.Decimal(0.00)
        putOption.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)

        # Set strike prices of puts to be the same.
        callOption.strikePrice = 1000
        putOption.strikePrice = 1000
        testOptionChain = [callOption, putOption]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)

        # The expected reason will still be OK since the filter happens later in checkForSignal.
        expectedReason = {'callOption': StrangleStrat.NoUpdateReason.OK,
                          'putOption': StrangleStrat.NoUpdateReason.OK}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)
        self.assertEqual(self.signalEventQueue.qsize(), 0)

if __name__ == '__main__':
    unittest.main()
