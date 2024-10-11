import unittest
import decimal
import queue
from datetime import datetime, timedelta
from dataHandler import csvData
from events import tickEvent
from riskManager import putVerticalRiskManagement
from strategyManager import putVerticalStrat


class TestPutVerticalStrategy(unittest.TestCase):

    def setUp(self):
        """Create instance of put vertical strategy.

        Specific strategy attributes:
          optPutToBuyDelta:   Optimal delta for the put to buy.
          maxPutToBuyDelta:   Maximum delta for the put to buy.
          minPutToBuyDelta:   Minimum delta for the put to buy
          optPutToSellDelta:  Optimal delta for the put to sell.
          maxPutToSellDelta:  Maximum delta for the put to sell.
          minPutToSellDelta:  Minimum delta for the put to sell.

        General strategy attributes:
          startDateTime:  Date/time to start the live trading or backtest.
          underlyingTicker:  Which underlying to use for the strategy.
          orderQuantity:  Number of verticals to sell.
          contractMultiplier: scaling factor for number of "shares" represented by an option or future. (E.g. 100 for options
                              and 50 for ES futures options).
          riskManagement: Risk management strategy (how to manage the trade; e.g., close, roll, hold to expiration).
          pricingSource -- Used to indicate which brokerage to use for commissions / fees.
          pricingSourceConfigFile -- File path to the JSON config file for commission / fees.

        Optional attributes:
          optimalDTE:  Optimal number of days before expiration to put on strategy.
          minimumDTE:  Minimum number of days before expiration to put on strategy.
          maximumDTE:  Maximum number of days to expiration when putting on strategy.
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

        # Create put vertical strategy object.
        self.signalEventQueue = queue.Queue()
        self.optPutToBuyDelta = -0.10
        self.maxPutToBuyDelta = -0.12
        self.minPutToBuyDelta = -0.06
        self.optPutToSellDelta = -0.16
        self.maxPutToSellDelta = -0.18
        self.minPutToSellDelta = -0.12
        self.underlyingTicker = 'AAPL'
        self.orderQuantity = 1
        self.contractMultiplier = 100
        self.riskManagement = putVerticalRiskManagement.PutVerticalRiskManagement(
            putVerticalRiskManagement.PutVerticalManagementStrategyTypes.HOLD_TO_EXPIRATION, closeDuration=None)
        self.optimalDTE = 45
        self.minimumDTE = 25
        self.maximumDTE = 65
        self.maxBidAsk = decimal.Decimal(0.15)
        self.maxCapitalToUsePerTrade = decimal.Decimal(0.10)  # 10% max capital to use per trade / strategy.
        # This date is before we have any options data in the CSV files in sampleData.
        self.startDateTime = datetime.fromisoformat('2014-08-07')
        self.curStrategy = putVerticalStrat.PutVerticalStrat(
            self.signalEventQueue, self.optPutToBuyDelta, self.maxPutToBuyDelta, self.minPutToBuyDelta,
            self.optPutToSellDelta, self.maxPutToSellDelta, self.minPutToSellDelta, self.underlyingTicker,
            self.orderQuantity, self.contractMultiplier, self.riskManagement, self.pricingSource,
            self.pricingSourceConfigFile, self.startDateTime, self.optimalDTE, self.minimumDTE, self.maximumDTE,
            maxBidAsk=self.maxBidAsk,maxCapitalToUsePerTrade=self.maxCapitalToUsePerTrade)
        self.portfolioNetLiquidity = decimal.Decimal(100000)
        self.availableBuyingPower = decimal.Decimal(50000)

    def testCheckForSignalNoEventData(self):
        """Tests that nothing is returned if there was no tick event data."""
        event = tickEvent.TickEvent()
        event.createEvent(None)
        self.assertIsNone(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower))

    def testStartTimeLessThanCurrentDateTime(self):
        """Tests that nothing is returned if the start time is before the current date / time."""
        startDateTime = datetime.fromisoformat('2016-08-07')
        curStrategy = putVerticalStrat.PutVerticalStrat(
            self.signalEventQueue, self.optPutToBuyDelta, self.maxPutToBuyDelta, self.minPutToBuyDelta,
            self.optPutToSellDelta, self.maxPutToSellDelta, self.minPutToSellDelta, self.underlyingTicker,
            self.orderQuantity, self.contractMultiplier, self.riskManagement, self.pricingSource,
            self.pricingSourceConfigFile, startDateTime, self.optimalDTE, self.minimumDTE, self.maximumDTE,
            maxBidAsk=self.maxBidAsk, maxCapitalToUsePerTrade=self.maxCapitalToUsePerTrade)
        putOptionToSell = self.optionChain.getData()[1]
        putOptionToBuy = self.optionChain.getData()[3]
        testOptionChain = [putOptionToSell, putOptionToBuy]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        self.assertIsNone(curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower))

    def testUpdateWithOptimalOptionWrongTickerSymbol(self):
        """Tests that the signal event returns WRONG_TICKER NoUpdateReason since the current option has wrong ticker."""
        putOptionToSell = self.optionChain.getData()[1]
        putOptionToBuy = self.optionChain.getData()[3]
        # Change ticker symbol.
        putOptionToSell.underlyingTicker = 'FAKE'
        putOptionToBuy.underlyingTicker = 'FAKE'
        testOptionChain = [putOptionToSell, putOptionToBuy]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        expectedReason = {'putToBuy': putVerticalStrat.NoUpdateReason.WRONG_TICKER,
                          'putToSell': putVerticalStrat.NoUpdateReason.WRONG_TICKER}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)

    def testUpdateWithOptimalOptionDeltaIsNone(self):
        """Tests that the signal event returns NO_DELTA NoUpdateReason since the current option has a None delta."""
        putOptionToSell = self.optionChain.getData()[1]
        putOptionToBuy = self.optionChain.getData()[3]
        # Change delta to None.
        putOptionToSell.delta = None
        putOptionToBuy.delta = None
        testOptionChain = [putOptionToSell, putOptionToBuy]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        expectedReason = {'putToBuy': putVerticalStrat.NoUpdateReason.NO_DELTA,
                          'putToSell': putVerticalStrat.NoUpdateReason.NO_DELTA}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)

    def testUpdateWithOptimalOptionSettlementPriceIsNone(self):
        """Tests that the signal event returns NO_SETTLEMENT_PRICE since current option has None settlement price."""
        putOptionToSell = self.optionChain.getData()[1]
        putOptionToBuy = self.optionChain.getData()[3]
        # Change settlement price to None.
        putOptionToSell.settlementPrice = None
        putOptionToBuy.settlementPrice = None
        testOptionChain = [putOptionToSell, putOptionToBuy]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        expectedReason = {'putToBuy': putVerticalStrat.NoUpdateReason.NO_SETTLEMENT_PRICE,
                          'putToSell': putVerticalStrat.NoUpdateReason.NO_SETTLEMENT_PRICE}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)

    def testUpdateWithOptimalOptionDTELessThanMinimum(self):
        """Tests that the signal event returns MIN_DTE NoUpdateReason since the current option is below MIN_DTE."""
        putOptionToSell = self.optionChain.getData()[1]
        putOptionToBuy = self.optionChain.getData()[3]
        # Set the number of days such that it is less than self.minimumDTE.
        putOptionToSell.expirationDateTime = putOptionToSell.dateTime + timedelta(days=(self.minimumDTE - 1))
        putOptionToBuy.expirationDateTime = putOptionToBuy.dateTime + timedelta(days=(self.minimumDTE - 1))
        testOptionChain = [putOptionToSell, putOptionToBuy]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        expectedReason = {'putToBuy': putVerticalStrat.NoUpdateReason.MIN_DTE,
                          'putToSell': putVerticalStrat.NoUpdateReason.MIN_DTE}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)

    def testUpdateWithOptimalOptionDTEGreaterThanMaximum(self):
        """Tests that signal event returns MAX_DTE NoUpdateReason since the current option is above MAX_DTE."""
        putOptionToSell = self.optionChain.getData()[1]
        putOptionToBuy = self.optionChain.getData()[3]
        # Set the number of days such that it is greater than self.maximumDTE.
        putOptionToSell.expirationDateTime = putOptionToSell.dateTime + timedelta(days=(self.maximumDTE + 1))
        putOptionToBuy.expirationDateTime = putOptionToBuy.dateTime + timedelta(days=(self.maximumDTE + 1))
        testOptionChain = [putOptionToSell, putOptionToBuy]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        expectedReason = {'putToBuy': putVerticalStrat.NoUpdateReason.MAX_DTE,
                          'putToSell': putVerticalStrat.NoUpdateReason.MAX_DTE}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)

    def testUpdateWithOptimalOptionDeltaLessThanMinPutDelta(self):
        """Tests that signal event returns MIN_MAX_DELTA NoUpdateReason if delta < min put delta."""
        putOptionToSell = self.optionChain.getData()[1]
        putOptionToBuy = self.optionChain.getData()[3]
        # Set expiration to greater than self.minimumDTE.
        putOptionToSell.expirationDateTime = putOptionToSell.dateTime + timedelta(days=(self.minimumDTE + 1))
        putOptionToBuy.expirationDateTime = putOptionToBuy.dateTime + timedelta(days=(self.minimumDTE + 1))
        # Modify delta of put option to be less than min put delta.
        putOptionToSell.delta = self.minPutToSellDelta - 1
        putOptionToBuy.delta = self.minPutToBuyDelta - 1
        testOptionChain = [putOptionToSell, putOptionToBuy]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        expectedReason = {'putToBuy': putVerticalStrat.NoUpdateReason.MIN_MAX_DELTA,
                          'putToSell': putVerticalStrat.NoUpdateReason.MIN_MAX_DELTA}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)

    def testUpdateWithOptimalOptionDeltaGreaterThanMaxPutDelta(self):
        """Tests that signal event returns MIN_MAX_DELTA NoUpdateReason if delta > max put delta."""
        putOptionToSell = self.optionChain.getData()[1]
        putOptionToBuy = self.optionChain.getData()[3]
        # Set expiration to greater than self.minimumDTE.
        putOptionToSell.expirationDateTime = putOptionToSell.dateTime + timedelta(days=(self.minimumDTE + 1))
        putOptionToBuy.expirationDateTime = putOptionToBuy.dateTime + timedelta(days=(self.minimumDTE + 1))
        # Modify delta of put option to be greater than max delta.
        putOptionToSell.delta = self.maxPutToSellDelta * 2
        putOptionToBuy.delta = self.maxPutToBuyDelta * 2
        testOptionChain = [putOptionToSell, putOptionToBuy]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        expectedReason = {'putToBuy': putVerticalStrat.NoUpdateReason.MIN_MAX_DELTA,
                          'putToSell': putVerticalStrat.NoUpdateReason.MIN_MAX_DELTA}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)

    def testUpdateWithOptimalOptionBidAskDiffGreaterThanMax(self):
        """Tests that signal event returns MAX_BID_ASK if the bid/ask difference is greater than the max bid/ask."""
        putOptionToSell = self.optionChain.getData()[1]
        putOptionToBuy = self.optionChain.getData()[3]
        # Set expiration to greater than self.minimumDTE.
        putOptionToSell.expirationDateTime = putOptionToSell.dateTime + timedelta(days=(self.minimumDTE + 1))
        putOptionToBuy.expirationDateTime = putOptionToBuy.dateTime + timedelta(days=(self.minimumDTE + 1))
        # Set put deltas to be the desired values.
        putOptionToSell.delta = self.optPutToSellDelta
        putOptionToBuy.delta = self.optPutToBuyDelta
        # Set the bidPrice and askPrice such that the difference is greater than self.maxBidAsk.
        putOptionToSell.bidPrice = decimal.Decimal(0.00)
        putOptionToSell.askPrice = self.maxBidAsk * 2
        putOptionToBuy.bidPrice = decimal.Decimal(0.00)
        putOptionToBuy.askPrice = self.maxBidAsk * 2
        testOptionChain = [putOptionToBuy, putOptionToSell]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        # Note that the expectedReason should happen this way because neither the putToBuy nor the putToSell matches,
        # and the order of evaluation makes the reason happen in this manner.
        expectedReason = {'putToBuy': putVerticalStrat.NoUpdateReason.MIN_MAX_DELTA,
                          'putToSell': putVerticalStrat.NoUpdateReason.MAX_BID_ASK}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)

    def testUpdateWithOptimalOptionChooseCloserExpiration(self):
        """Tests that we choose the option with the expiration date closer to self.optimalDTE."""
        putOptionToSellNonOptimalDTE = self.optionChain.getData()[5]
        putOptionToSellOptimalDTE = self.optionChain.getData()[7]
        putOptionToBuyNonOptimalDTE = self.optionChain.getData()[1]
        putOptionToBuyOptimalDTE = self.optionChain.getData()[3]

        # Set expiration to be greater than self.minimumDTE.
        putOptionToSellNonOptimalDTE.expirationDateTime = putOptionToSellNonOptimalDTE.dateTime + timedelta(
            days=(self.minimumDTE + 1))
        putOptionToBuyNonOptimalDTE.expirationDateTime = putOptionToBuyNonOptimalDTE.dateTime + timedelta(
            days=(self.minimumDTE + 1))
        putOptionToSellOptimalDTE.expirationDateTime = putOptionToSellOptimalDTE.dateTime + timedelta(
            days=(self.minimumDTE + 2))
        putOptionToBuyOptimalDTE.expirationDateTime = putOptionToBuyOptimalDTE.dateTime + timedelta(
            days=(self.minimumDTE + 2))

        # Set put deltas. We use these delta values to check that the options with the optimal DTE were chosen.
        putOptionToSellNonOptimalDTE.delta = self.maxPutToSellDelta
        putOptionToSellOptimalDTE.delta = self.optPutToSellDelta
        putOptionToBuyNonOptimalDTE.delta = self.maxPutToBuyDelta
        putOptionToBuyOptimalDTE.delta = self.optPutToBuyDelta

        # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
        epsilon = decimal.Decimal(0.001)
        putOptionToSellNonOptimalDTE.bidPrice = decimal.Decimal(0.00)
        putOptionToSellNonOptimalDTE.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        putOptionToSellOptimalDTE.bidPrice = decimal.Decimal(0.00)
        putOptionToSellOptimalDTE.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        putOptionToBuyNonOptimalDTE.bidPrice = decimal.Decimal(0.00)
        putOptionToBuyNonOptimalDTE.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        putOptionToBuyOptimalDTE.bidPrice = decimal.Decimal(0.00)
        putOptionToBuyOptimalDTE.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)

        testOptionChain = [putOptionToSellNonOptimalDTE, putOptionToBuyNonOptimalDTE, putOptionToSellOptimalDTE,
                           putOptionToBuyOptimalDTE]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower)
        putVerticalObj = self.signalEventQueue.get().getData()[0]
        # We use delta to check since we can't access the expiration date from putVerticalObj.
        self.assertAlmostEqual(putVerticalObj.getDelta(), putVerticalObj.getNumContracts() * (
            putOptionToSellOptimalDTE.delta + putOptionToBuyOptimalDTE.delta))

    def testUpdateWithOptimalOptionChooseCloserDelta(self):
        """Tests that if options have the same DTE, chose option with the delta closer to requested delta."""
        putOptionToSellNonOptimalDelta = self.optionChain.getData()[5]
        putOptionToSellOptimalDelta = self.optionChain.getData()[7]
        putOptionToBuyNonOptimalDelta = self.optionChain.getData()[1]
        putOptionToBuyOptimalDelta = self.optionChain.getData()[3]

        # Set expiration to be greater than self.minimumDTE.
        putOptionToSellNonOptimalDelta.expirationDateTime = putOptionToSellNonOptimalDelta.dateTime + timedelta(
            days=(self.minimumDTE + 1))
        putOptionToSellOptimalDelta.expirationDateTime = putOptionToSellOptimalDelta.dateTime + timedelta(
            days=(self.minimumDTE + 1))
        putOptionToBuyNonOptimalDelta.expirationDateTime = putOptionToBuyNonOptimalDelta.dateTime + timedelta(
            days=(self.minimumDTE + 1))
        putOptionToBuyOptimalDelta.expirationDateTime = putOptionToBuyOptimalDelta.dateTime + timedelta(
            days=(self.minimumDTE + 1))

        # Set put deltas. We use these delta values to check that the options with the optimal DTE were chosen.
        putOptionToSellNonOptimalDelta.delta = -0.19
        putOptionToSellOptimalDelta.delta = self.optPutToSellDelta
        putOptionToBuyNonOptimalDelta.delta = -0.13
        putOptionToBuyOptimalDelta.delta = self.optPutToBuyDelta

        # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
        epsilon = decimal.Decimal(0.001)
        putOptionToSellNonOptimalDelta.bidPrice = decimal.Decimal(0.00)
        putOptionToSellNonOptimalDelta.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        putOptionToSellOptimalDelta.bidPrice = decimal.Decimal(0.00)
        putOptionToSellOptimalDelta.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        putOptionToBuyNonOptimalDelta.bidPrice = decimal.Decimal(0.00)
        putOptionToBuyNonOptimalDelta.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        putOptionToBuyOptimalDelta.bidPrice = decimal.Decimal(0.00)
        putOptionToBuyOptimalDelta.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)

        testOptionChain = [putOptionToSellNonOptimalDelta, putOptionToBuyNonOptimalDelta, putOptionToSellOptimalDelta,
                           putOptionToBuyOptimalDelta]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower)
        putVerticalObj = self.signalEventQueue.get().getData()[0]
        self.assertAlmostEqual(putVerticalObj.getDelta(),
                               putVerticalObj.getNumContracts() * (putOptionToSellOptimalDelta.delta +
                                                                   putOptionToBuyOptimalDelta.delta))

    def testUpdateWithOptimalOptionSuccess(self):
        """Tests that the options were found successfully according to the strategy."""
        putOptionToSellInitial = self.optionChain.getData()[7]
        putOptionToBuyInitial = self.optionChain.getData()[3]

        # Set expiration to be the same and greater than self.minimumDTE.
        putOptionToSellInitial.expirationDateTime = putOptionToSellInitial.dateTime + timedelta(
            days=(self.minimumDTE + 1))
        putOptionToBuyInitial.expirationDateTime = putOptionToBuyInitial.dateTime + timedelta(
            days=(self.minimumDTE + 1))

        # Set put deltas. We use these delta values to check that the options with the optimal DTE were chosen.
        putOptionToSellInitial.delta = self.optPutToSellDelta
        putOptionToBuyInitial.delta = self.optPutToBuyDelta

        # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
        epsilon = decimal.Decimal(0.001)
        putOptionToSellInitial.bidPrice = decimal.Decimal(0.00)
        putOptionToSellInitial.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        putOptionToBuyInitial.bidPrice = decimal.Decimal(0.00)
        putOptionToBuyInitial.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)

        testOptionChain = [putOptionToSellInitial, putOptionToBuyInitial]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)
        expectedReason = {'putToBuy': putVerticalStrat.NoUpdateReason.OK,
                          'putToSell': putVerticalStrat.NoUpdateReason.OK}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)

    def testCheckForSignalTotalDebitCreditLessThanMinCredit(self):
        """Tests that no signal event is created when the debit/credit is less than minCreditDebit."""
        putOptionToSell = self.optionChain.getData()[1]
        putOptionToBuy = self.optionChain.getData()[3]

        # Set expiration to greater than self.minimumDTE.
        putOptionToSell.expirationDateTime = putOptionToSell.dateTime + timedelta(days=(self.minimumDTE + 1))
        putOptionToBuy.expirationDateTime = putOptionToBuy.dateTime + timedelta(days=(self.minimumDTE + 2))

        # Set put and call delta to be the desired values.
        putOptionToSell.delta = self.optPutToSellDelta
        putOptionToBuy.delta = self.optPutToBuyDelta

        # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
        epsilon = decimal.Decimal(0.001)
        putOptionToSell.bidPrice = decimal.Decimal(0.00)
        putOptionToSell.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        putOptionToBuy.bidPrice = decimal.Decimal(0.00)
        putOptionToBuy.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        testOptionChain = [putOptionToSell, putOptionToBuy]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)

        # Set minCreditDebit to a large number to test that creation of the strategy fails.
        curStrategy = putVerticalStrat.PutVerticalStrat(
            self.signalEventQueue, self.optPutToBuyDelta, self.maxPutToBuyDelta, self.minPutToBuyDelta,
            self.optPutToSellDelta, self.maxPutToSellDelta, self.minPutToSellDelta, self.underlyingTicker,
            self.orderQuantity, self.contractMultiplier, self.riskManagement, self.pricingSource,
            self.pricingSourceConfigFile, self.startDateTime, self.optimalDTE, self.minimumDTE, self.maximumDTE,
            maxBidAsk=self.maxBidAsk, maxCapitalToUsePerTrade=self.maxCapitalToUsePerTrade, minCreditDebit=1000)
        curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower)

        self.assertEqual(self.signalEventQueue.qsize(), 0)

    def testCheckForSignalNumContractLessThanOne(self):
        """Tests that no signal event is created when the number of contracts is less than one."""
        putOptionToSell = self.optionChain.getData()[1]
        putOptionToBuy = self.optionChain.getData()[3]

        # Set expiration to greater than self.minimumDTE.
        putOptionToSell.expirationDateTime = putOptionToSell.dateTime + timedelta(days=(self.minimumDTE + 1))
        putOptionToBuy.expirationDateTime = putOptionToBuy.dateTime + timedelta(days=(self.minimumDTE + 2))

        # Set put and call delta to be the desired values.
        putOptionToSell.delta = self.optPutToSellDelta
        putOptionToBuy.delta = self.optPutToBuyDelta

        # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
        epsilon = decimal.Decimal(0.001)
        putOptionToSell.bidPrice = decimal.Decimal(0.00)
        putOptionToSell.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        putOptionToBuy.bidPrice = decimal.Decimal(0.00)
        putOptionToBuy.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        testOptionChain = [putOptionToSell, putOptionToBuy]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)

        # The expected reason will still be OK since the filter happens later in checkForSignal.
        expectedReason = {'putToBuy': putVerticalStrat.NoUpdateReason.OK,
                          'putToSell': putVerticalStrat.NoUpdateReason.OK}

        # Set available buying power to zero such that number of contracts will be less than one.
        availableBuyingPower = decimal.Decimal(0.00)
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, availableBuyingPower),
                         expectedReason)
        self.assertEqual(self.signalEventQueue.qsize(), 0)

    def testCheckForSignalPutsWithDifferentExpirations(self):
        """Tests that no signal event is created if put options have different expirations."""
        putOptionToSell = self.optionChain.getData()[1]
        putOptionToBuy = self.optionChain.getData()[3]

        # Set expiration to greater than self.minimumDTE.
        putOptionToSell.expirationDateTime = putOptionToSell.dateTime + timedelta(days=(self.minimumDTE + 1))
        putOptionToBuy.expirationDateTime = putOptionToBuy.dateTime + timedelta(days=(self.minimumDTE + 2))

        # Set put and call delta to be the desired values.
        putOptionToSell.delta = self.optPutToSellDelta
        putOptionToBuy.delta = self.optPutToBuyDelta

        # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
        epsilon = decimal.Decimal(0.001)
        putOptionToSell.bidPrice = decimal.Decimal(0.00)
        putOptionToSell.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        putOptionToBuy.bidPrice = decimal.Decimal(0.00)
        putOptionToBuy.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        testOptionChain = [putOptionToSell, putOptionToBuy]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)

        # The expected reason will still be OK since the filter happens later in checkForSignal.
        expectedReason = {'putToBuy': putVerticalStrat.NoUpdateReason.OK,
                          'putToSell': putVerticalStrat.NoUpdateReason.OK}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)
        self.assertEqual(self.signalEventQueue.qsize(), 0)

    def testCheckForSignalPutsWithSameStrikePrice(self):
        """Tests that no signal event is created if put options have same strike prices."""
        putOptionToSell = self.optionChain.getData()[1]
        putOptionToBuy = self.optionChain.getData()[3]

        # Set expiration to greater than self.minimumDTE.
        putOptionToSell.expirationDateTime = putOptionToSell.dateTime + timedelta(days=(self.minimumDTE + 1))
        putOptionToBuy.expirationDateTime = putOptionToBuy.dateTime + timedelta(days=(self.minimumDTE + 1))

        # Set put and call delta to be the desired values.
        putOptionToSell.delta = self.optPutToSellDelta
        putOptionToBuy.delta = self.optPutToBuyDelta

        # Set the bidPrice and askPrice such that the difference is less than self.maxBidAsk.
        epsilon = decimal.Decimal(0.001)
        putOptionToSell.bidPrice = decimal.Decimal(0.00)
        putOptionToSell.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)
        putOptionToBuy.bidPrice = decimal.Decimal(0.00)
        putOptionToBuy.askPrice = decimal.Decimal(self.maxBidAsk - epsilon)

        # Set strike prices of puts to be the same.
        putOptionToSell.strikePrice = 1000
        putOptionToBuy.strikePrice = 1000
        testOptionChain = [putOptionToSell, putOptionToBuy]
        event = tickEvent.TickEvent()
        event.createEvent(testOptionChain)

        # The expected reason will still be OK since the filter happens later in checkForSignal.
        expectedReason = {'putToBuy': putVerticalStrat.NoUpdateReason.OK,
                          'putToSell': putVerticalStrat.NoUpdateReason.OK}
        self.assertEqual(self.curStrategy.checkForSignal(event, self.portfolioNetLiquidity, self.availableBuyingPower),
                         expectedReason)
        self.assertEqual(self.signalEventQueue.qsize(), 0)


if __name__ == '__main__':
    unittest.main()
