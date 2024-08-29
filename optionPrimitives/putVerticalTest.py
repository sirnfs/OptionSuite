import unittest
from optionPrimitives import optionPrimitive
from optionPrimitives import putVertical
from base import put
import datetime
import decimal
import json


class TestPutVertical(unittest.TestCase):

    def setUp(self):
        orderQuantity = 1
        self.contractMultiplier = 100
        # For short put vertical
        self.__putToBuy = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(359.69),
                                  strikePrice=decimal.Decimal(325), delta=-0.46, vega=0.07974, theta=-0.069166,
                                  gamma=0.004462, dateTime=datetime.datetime.strptime('01/02/1990',
                                                                                      "%m/%d/%Y"),
                                  expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                                "%m/%d/%Y"),
                                  tradeDateTime=datetime.datetime.strptime('03/09/2024',
                                                                           "%m/%d/%Y"),
                                  tradePrice=decimal.Decimal(0.5005), settlementPrice=decimal.Decimal(0.5005))
        self.__putToSell = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(359.69),
                                   strikePrice=decimal.Decimal(345), delta=-0.142391, vega=0.173239, theta=-0.094256,
                                   gamma=0.0148523, dateTime=datetime.datetime.strptime('01/02/1990',
                                                                                        "%m/%d/%Y"),
                                   expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                                 "%m/%d/%Y"),
                                   tradeDateTime=datetime.datetime.strptime('03/09/2024',
                                                                            "%m/%d/%Y"),
                                   tradePrice=decimal.Decimal(1.125), settlementPrice=decimal.Decimal(1.125))
        self.__shortPutVertical = putVertical.PutVertical(orderQuantity, self.contractMultiplier, self.__putToBuy,
                                                          self.__putToSell, optionPrimitive.TransactionType.SELL)
        # For long put vertical.
        self.__longPutVertical = putVertical.PutVertical(orderQuantity, self.contractMultiplier, self.__putToSell,
                                                         self.__putToBuy, optionPrimitive.TransactionType.BUY)

        # The parameters below are used to update the prices of the put verticals above.
        # Update prices of short put vertical. We only updated the underlying price and bid/ask prices We did not touch
        # the Greeks, though they will also change.
        self.__shortPutVerticalTickData = []
        putToBuyUpdate = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                                 strikePrice=decimal.Decimal(325),
                                 expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                               "%m/%d/%Y"),
                                 tradePrice=decimal.Decimal(0.4375), settlementPrice=decimal.Decimal(0.4375))
        self.__shortPutVerticalTickData.append(putToBuyUpdate)
        putToSellUpdate = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                                  strikePrice=decimal.Decimal(345),
                                  expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                                "%m/%d/%Y"),
                                  tradePrice=decimal.Decimal(1.25), settlementPrice=decimal.Decimal(1.25))
        self.__shortPutVerticalTickData.append(putToSellUpdate)

        # Load the JSON config for calculating commissions and fees. Test with Tastyworks as the brokerage.
        self.pricingSourceConfig = None
        self.pricingSource = 'tastyworks'
        with open('./dataHandler/pricingConfig.json') as config:
            fullConfig = json.load(config)
            self.pricingSourceConfig = fullConfig[self.pricingSource]

    def testThatObjectCreationFailsForDifferentExpirations(self):
        """Tests that object creation fails when puts have different expiration cycles."""
        putToBuy = put.Put(underlyingTicker='SPX', strikePrice=decimal.Decimal(325),
                           expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                         "%m/%d/%Y"))
        putToSell = put.Put(underlyingTicker='SPX', strikePrice=decimal.Decimal(345),
                            expirationDateTime=datetime.datetime.strptime('01/20/1990',
                                                                          "%m/%d/%Y"))
        orderQuantity = 1
        with self.assertRaisesRegex(ValueError, 'Both put options must have the same expiration.'):
            putVertical.PutVertical(orderQuantity, self.contractMultiplier, putToBuy, putToSell,
                                    optionPrimitive.TransactionType.SELL)

    def testGetDateTime(self):
        """Tests that the dateTime value is pulled correctly."""
        self.assertEqual(self.__shortPutVertical.getDateTime(), datetime.datetime.strptime('01/02/1990',
                                                                                           "%m/%d/%Y"))
        self.assertEqual(self.__longPutVertical.getDateTime(), datetime.datetime.strptime('01/02/1990',
                                                                                          "%m/%d/%Y"))

    def testGetExpirationDateTime(self):
        """Tests that the expirationDateTime is pulled correctly."""
        self.assertEqual(self.__shortPutVertical.getExpirationDateTime(), datetime.datetime.strptime(
            '01/19/1990', "%m/%d/%Y"))
        self.assertEqual(self.__longPutVertical.getExpirationDateTime(), datetime.datetime.strptime(
            '01/19/1990', "%m/%d/%Y"))

    def testGetUnderlyingTicker(self):
        """Tests that the underlyingTicker symbol is pulled correctly."""
        self.assertEqual(self.__shortPutVertical.getUnderlyingTicker(), 'SPX')
        self.assertEqual(self.__longPutVertical.getUnderlyingTicker(), 'SPX')

    def testGetDelta(self):
        """Tests that delta values are summed for the verticals."""
        self.assertAlmostEqual(self.__shortPutVertical.getDelta(), -0.602391)
        self.assertAlmostEqual(self.__longPutVertical.getDelta(), -0.602391)

    def testGetDeltaNoneValue(self):
        """Tests that a value of None is returned if one of the delta is None."""
        putToBuy = put.Put(underlyingTicker='SPX', strikePrice=decimal.Decimal(325), delta=None,
                           expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                         "%m/%d/%Y"))
        putToSell = put.Put(underlyingTicker='SPX', strikePrice=decimal.Decimal(345), delta=-0.142391,
                            expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                          "%m/%d/%Y"))
        putVerticalObj = putVertical.PutVertical(orderQuantity=1, contractMultiplier=self.contractMultiplier,
                                                 putToBuy=putToBuy, putToSell=putToSell,
                                                 buyOrSell=optionPrimitive.TransactionType.BUY)
        self.assertIsNone(putVerticalObj.getDelta())

    def testGetVega(self):
        """Tests that vega values are summed for the verticals."""
        self.assertAlmostEqual(self.__shortPutVertical.getVega(), 0.252979)

    def testGetVegaNoneValue(self):
        """Tests that a value of None is returned if one of the vega is None."""
        putToBuy = put.Put(underlyingTicker='SPX', strikePrice=decimal.Decimal(325), vega=0.07974,
                           expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                         "%m/%d/%Y"))
        putToSell = put.Put(underlyingTicker='SPX', strikePrice=decimal.Decimal(345), vega=None,
                            expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                          "%m/%d/%Y"))
        putVerticalObj = putVertical.PutVertical(orderQuantity=1, contractMultiplier=self.contractMultiplier,
                                                 putToBuy=putToBuy, putToSell=putToSell,
                                                 buyOrSell=optionPrimitive.TransactionType.BUY)
        self.assertIsNone(putVerticalObj.getVega())

    def testGetTheta(self):
        """Tests that theta values are summed for the verticals."""
        self.assertAlmostEqual(self.__shortPutVertical.getTheta(), -0.163422)

    def testGetThetaNoneValue(self):
        """Tests that a value of None is returned if one of the theta is None."""
        putToBuy = put.Put(underlyingTicker='SPX', strikePrice=decimal.Decimal(325), theta=None,
                           expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                         "%m/%d/%Y"))
        putToSell = put.Put(underlyingTicker='SPX',
                            strikePrice=decimal.Decimal(345), theta=-0.094256,
                            expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                          "%m/%d/%Y"))
        orderQuantity = 1
        shortPutVertical = putVertical.PutVertical(orderQuantity, self.contractMultiplier, putToBuy, putToSell,
                                                   optionPrimitive.TransactionType.SELL)
        self.assertIsNone(shortPutVertical.getTheta())

    def testGetGamma(self):
        """Tests that gamma values are summed for the verticals."""
        self.assertAlmostEqual(self.__shortPutVertical.getGamma(), 0.0193143)

    def testGetGammaNoneValue(self):
        """Tests that a value of None is returned if one of the theta is None."""
        putToBuy = put.Put(underlyingTicker='SPX', strikePrice=decimal.Decimal(325), gamma=None,
                           expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                         "%m/%d/%Y"))
        putToSell = put.Put(underlyingTicker='SPX', strikePrice=decimal.Decimal(345), gamma=0.0148523,
                            expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                          "%m/%d/%Y"))
        orderQuantity = 1
        shortPutVertical = putVertical.PutVertical(orderQuantity, self.contractMultiplier, putToBuy, putToSell,
                                                   optionPrimitive.TransactionType.SELL)
        self.assertIsNone(shortPutVertical.getGamma())

    def testGetNumContracts(self):
        """Tests that the numContracts is pulled correctly."""
        self.assertEqual(self.__shortPutVertical.getNumContracts(), 1)
        self.assertEqual(self.__longPutVertical.getNumContracts(), 1)

    def testGetContractMultiplier(self):
        """Tests that the contractMultiplier is pulled correctly."""
        self.assertEqual(self.__shortPutVertical.getContractMultiplier(), 100)
        self.assertEqual(self.__longPutVertical.getContractMultiplier(), 100)

    def testSetNumContracts(self):
        """Tests that the numContracts is set correctly."""
        self.__shortPutVertical.setNumContracts(2)
        self.__longPutVertical.setNumContracts(2)
        self.assertEqual(self.__shortPutVertical.getNumContracts(), 2)
        self.assertEqual(self.__longPutVertical.getNumContracts(), 2)

    def testSetNumContractsInvalidContractNumber(self):
        """Tests that an exception is raised if an invalid contract number is specified."""
        with self.assertRaisesRegex(ValueError,
                                    'Number of contracts must be a positive \(> 0\) number.'):
            self.__shortPutVertical.setNumContracts(-1)

    def testPutVerticalCalcProfitLossNoDataUpdate(self):
        """Tests that the profit / loss is zero if we haven't updated the option."""
        self.assertAlmostEqual(self.__shortPutVertical.calcProfitLoss(), decimal.Decimal(0.0))

    def testPutVerticalCalcProfitLossPercentageNoDataUpdate(self):
        """Tests that the profit / loss is zero percent if we haven't updated the option."""
        self.assertAlmostEqual(self.__shortPutVertical.calcProfitLossPercentage(), decimal.Decimal(0.0))

    def testVerticalCalcProfitLossWithDataUpdate(self):
        """Tests that the profit / loss is calculated correctly when new data is available."""
        # short put value goes from 1.125 to 1.25; a loss. Diff = -0.125
        # long put values goes from 0.5005 to 0.4375; a loss. Diff = -0.063
        # total loss = -0.125 + -0.063 = -0.188 * numContracts=1 * contractMultiplier=100 = -18.8
        self.__shortPutVertical.updateValues(self.__shortPutVerticalTickData)
        self.assertAlmostEqual(self.__shortPutVertical.calcProfitLoss(), decimal.Decimal(-18.8))

    def testCalcRealizedProfitLossWithDataUpdate(self):
        """Tests that the realized profit / loss is calculated correctly."""
        self.__shortPutVertical.updateValues(self.__shortPutVerticalTickData)
        self.__shortPutVertical.setClosingFees(decimal.Decimal(1.00))
        self.assertAlmostEqual(self.__shortPutVertical.calcRealizedProfitLoss(), decimal.Decimal(-19.8))

    def testVerticalCalcProfitLossPercentage(self):
        """Tests that the profit / loss percentage is calculated correctly."""
        # shortPutCredit = 1.125
        # longPutDebit = -0.5005
        # totalCreditDebit = 1.125 - 0.5005 = 0.6245 * numContracts=1 * contractMultiplier=100 = 62.45
        # total loss = -0.125 + -0.063 = -0.188 * numContracts=1 * contractMultiplier=100 = -18.8
        # percentProfitLoss = (-18.8 / 62.45) * 100 = -30.104%
        self.__shortPutVertical.updateValues(self.__shortPutVerticalTickData)
        self.assertAlmostEqual(self.__shortPutVertical.calcProfitLossPercentage(), decimal.Decimal(-30.1040832666))

    def testShortPutVerticalBuyingPower(self):
        # Tests the buying power calculation for the short put vertical.
        # (putToSellStrikePrice = 345 - putToBuyStrikePrice = 325) - (putToSellPrice=1.125 - putToBuyPrice=0.5005) *
        # numContracts=1 * contractMultiplier=100 = ((20) - (0.6245)) * 1 * 100 = 1937.55
        self.assertAlmostEqual(self.__shortPutVertical.getBuyingPower(), decimal.Decimal(1937.55))

    def testLongPutVerticalBuyingPower(self):
        # Tests the buying power calculation for the long put vertical.
        # (putToBuyPrice=1.125 - putToSellPrice=0.5005) * numContracts=1 * contractMultiplier=100 =
        # (0.6245) * 1 * 100 = 62.45
        self.assertAlmostEqual(self.__longPutVertical.getBuyingPower(), decimal.Decimal(62.45))

    def testVerticalGetCommissionsAndFeesOpen(self):
        """Tests that the commissions and fees are calculated correctly on trade open."""
        indexOptionOpen = self.pricingSourceConfig['stock_options']['index_option']['open']
        putToSellMidPrice = self.__putToSell.settlementPrice
        secFees = indexOptionOpen['sec_fee_per_contract_wo_trade_price'] * float(putToSellMidPrice)
        self.assertAlmostEqual(self.__shortPutVertical.getCommissionsAndFees('open', self.pricingSource,
                                                                             self.pricingSourceConfig),
                               decimal.Decimal(2 * self.__shortPutVertical.getNumContracts() * (
                                   indexOptionOpen['commission_per_contract'] + indexOptionOpen[
                                     'clearing_fee_per_contract'] +
                                   indexOptionOpen['orf_fee_per_contract'] +
                                   indexOptionOpen['proprietary_index_fee_per_contract']) +
                                               self.__shortPutVertical.getNumContracts() * secFees))

    def testVerticalGetCommissionsAndFeesClose(self):
        """Tests that the commissions and fees are calculated correctly on trade close."""
        indexOptionClose = self.pricingSourceConfig['stock_options']['index_option']['close']
        putToBuyMidPrice = self.__putToBuy.settlementPrice
        secFees = indexOptionClose['sec_fee_per_contract_wo_trade_price'] * float(putToBuyMidPrice)
        self.assertAlmostEqual(self.__shortPutVertical.getCommissionsAndFees('close', self.pricingSource,
                                                                             self.pricingSourceConfig),
                               decimal.Decimal(2 * self.__shortPutVertical.getNumContracts() * (
                                   indexOptionClose['commission_per_contract'] +
                                   indexOptionClose['clearing_fee_per_contract'] + indexOptionClose[
                                       'orf_fee_per_contract'] +
                                   indexOptionClose['proprietary_index_fee_per_contract']) +
                                               self.__shortPutVertical.getNumContracts() * secFees))

    def testVerticalGetCommissionsAndFeesInvalidOpenOrCloseType(self):
        """Tests that an exception is raised if the type is not 'open' or 'close'."""
        with self.assertRaisesRegex(
              TypeError,
              'Only open or close types can be provided to getCommissionsAndFees().'):
            self.__shortPutVertical.getCommissionsAndFees('invalid_type', self.pricingSource,
                                                          self.pricingSourceConfig)

    def testFuturesOptionsVerticalGetCommissionsAndFeesOpen(self):
        """Tests that the commissions and fees are calculated correctly on trade open for futures options."""
        # Load the JSON config for calculating commissions and fees. Test with Tastyworks Futures as the brokerage.
        pricingSourceConfig = None
        pricingSource = 'tastyworks_futures'
        with open('./dataHandler/pricingConfig.json') as config:
            fullConfig = json.load(config)
            pricingSourceConfig = fullConfig[pricingSource]

        esOptionConfig = pricingSourceConfig['futures_options']['es_option']['open']
        self.assertAlmostEqual(
            self.__shortPutVertical.getCommissionsAndFees('open', pricingSource, pricingSourceConfig),
            decimal.Decimal(2 * self.__shortPutVertical.getNumContracts() * (
                esOptionConfig['commission_per_contract'] + esOptionConfig['clearing_fee_per_contract'] +
                esOptionConfig['nfa_fee_per_contract'] + esOptionConfig['exchange_fee_per_contract'])))

    def testFuturesOptionsVerticalGetCommissionsAndFeesClose(self):
        """Tests that the commissions and fees are calculated correctly on trade close for futures options."""
        # Load the JSON config for calculating commissions and fees. Test with Tastyworks Futures as the brokerage.
        pricingSourceConfig = None
        pricingSource = 'tastyworks_futures'
        with open('./dataHandler/pricingConfig.json') as config:
            fullConfig = json.load(config)
            pricingSourceConfig = fullConfig[pricingSource]

        esOptionConfig = pricingSourceConfig['futures_options']['es_option']['close']
        self.assertAlmostEqual(
            self.__shortPutVertical.getCommissionsAndFees('close', pricingSource, pricingSourceConfig),
            decimal.Decimal(2 * self.__shortPutVertical.getNumContracts() * (
                esOptionConfig['commission_per_contract'] + esOptionConfig['clearing_fee_per_contract'] +
                esOptionConfig['nfa_fee_per_contract'] + esOptionConfig['exchange_fee_per_contract'])))

    def testFuturesOptionsVerticalGetCommissionsAndFeesInvalidOpenOrCloseType(self):
        """Tests that an exception is raised if the type is not 'open' or 'close'."""
        pricingSourceConfig = None
        pricingSource = 'tastyworks_futures'
        with open('./dataHandler/pricingConfig.json') as config:
            fullConfig = json.load(config)
            pricingSourceConfig = fullConfig[pricingSource]

        with self.assertRaisesRegex(
              TypeError, 'Only open or close types can be provided to getCommissionsAndFees().'):
            self.__shortPutVertical.getCommissionsAndFees('invalid_type', pricingSource,
                                                          pricingSourceConfig)

    def testIndexOptionsVerticalGetCommissionsAndFeesOpen(self):
        """Tests that the commissions and fees are calculated correctly on trade open for index options."""
        # Load the JSON config for calculating commissions and fees. Test with Tastyworks as the brokerage.
        pricingSourceConfig = None
        pricingSource = 'tastyworks'
        with open('./dataHandler/pricingConfig.json') as config:
            fullConfig = json.load(config)
            pricingSourceConfig = fullConfig[pricingSource]

        indexOptionConfig = pricingSourceConfig['stock_options']['index_option']['open']
        putToSellSettlementPrice = self.__putToSell.settlementPrice
        secFees = indexOptionConfig['sec_fee_per_contract_wo_trade_price'] * float(putToSellSettlementPrice)
        self.assertAlmostEqual(
            self.__shortPutVertical.getCommissionsAndFees('open', pricingSource, pricingSourceConfig),
            decimal.Decimal(2 * (indexOptionConfig['commission_per_contract'] +
                                 indexOptionConfig['clearing_fee_per_contract'] +
                                 indexOptionConfig['orf_fee_per_contract'] +
                                 indexOptionConfig['proprietary_index_fee_per_contract']) + secFees))

    def testIndexOptionsVerticalGetCommissionsAndFeesClose(self):
        """Tests that the commissions and fees are calculated correctly on trade close for index options."""
        # Load the JSON config for calculating commissions and fees. Test with Tastyworks as the brokerage.
        pricingSourceConfig = None
        pricingSource = 'tastyworks'
        with open('./dataHandler/pricingConfig.json') as config:
            fullConfig = json.load(config)
            pricingSourceConfig = fullConfig[pricingSource]

        indexOptionConfig = pricingSourceConfig['stock_options']['index_option']['close']
        putToBuySettlementPrice = self.__putToBuy.settlementPrice
        secFees = indexOptionConfig['sec_fee_per_contract_wo_trade_price'] * float(putToBuySettlementPrice)
        self.assertAlmostEqual(
            self.__shortPutVertical.getCommissionsAndFees('close', pricingSource, pricingSourceConfig),
            decimal.Decimal(2 * (indexOptionConfig['commission_per_contract'] +
                                 indexOptionConfig['clearing_fee_per_contract'] +
                                 indexOptionConfig['orf_fee_per_contract'] +
                                 indexOptionConfig['proprietary_index_fee_per_contract']) + secFees))

    def testIndexOptionsVerticalGetCommissionsAndFeesInvalidOpenOrCloseType(self):
        """Tests that an exception is raised if the type is not 'open' or 'close'."""
        pricingSourceConfig = None
        pricingSource = 'tastyworks'
        with open('./dataHandler/pricingConfig.json') as config:
            fullConfig = json.load(config)
            pricingSourceConfig = fullConfig[pricingSource]

        with self.assertRaisesRegex(
              TypeError, 'Only open or close types can be provided to getCommissionsAndFees().'):
            self.__shortPutVertical.getCommissionsAndFees('invalid_type', pricingSource,
                                                          pricingSourceConfig)

    def testVerticalUpdateValuesNoMatchingPutToBuyOptionFound(self):
        """Tests that the profit loss calculation is unchanged if no putToBuy option is available to update."""
        initialProfitLoss = self.__shortPutVertical.calcProfitLoss()
        tickData = []
        # Changed the putToBuy strike price from 325 to 327 to prevent a match.
        putToBuy = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                           strikePrice=decimal.Decimal(327),
                           expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                         "%m/%d/%Y"),
                           tradePrice=decimal.Decimal(0.4375), settlementPrice=decimal.Decimal(0.4375))
        tickData.append(putToBuy)
        putToSell = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                            strikePrice=decimal.Decimal(345),
                            expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                          "%m/%d/%Y"),
                            tradePrice=decimal.Decimal(1.25), settlementPrice=decimal.Decimal(1.25))
        tickData.append(putToSell)
        self.assertFalse(self.__shortPutVertical.updateValues(tickData))

        # The profit / loss should be the same since the option wasn't updated.
        self.assertAlmostEqual(self.__shortPutVertical.calcProfitLoss(), initialProfitLoss)

    def testVerticalUpdateValuesNoMatchingPutToSellOptionFound(self):
        """Tests that the profit loss calculation is unchanged if no putToSell option is available to update."""
        initialProfitLoss = self.__shortPutVertical.calcProfitLoss()
        tickData = []
        putToBuy = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                           strikePrice=decimal.Decimal(325),
                           expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                         "%m/%d/%Y"),
                           tradePrice=decimal.Decimal(0.4375), settlementPrice=decimal.Decimal(0.4375))
        tickData.append(putToBuy)
        # Changed the putToBuy strike price from 345 to 350 to prevent a match.
        putToSell = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                            strikePrice=decimal.Decimal(350),
                            expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                          "%m/%d/%Y"),
                            tradePrice=decimal.Decimal(1.25), settlementPrice=decimal.Decimal(1.25))
        tickData.append(putToSell)
        self.assertFalse(self.__shortPutVertical.updateValues(tickData))

        # The profit / loss should be the same since the option wasn't updated.
        self.assertAlmostEqual(self.__shortPutVertical.calcProfitLoss(), initialProfitLoss)

    def testVerticalUpdateValuesNoUpdatePutToBuySettlementPriceIsNone(self):
        """Tests that the putVertical can't be updated since the settlement price of the putToBuy is None."""
        tickData = []
        putToBuy = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                           strikePrice=decimal.Decimal(325),
                           expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                         "%m/%d/%Y"),
                           tradePrice=decimal.Decimal(0.4375), settlementPrice=None)
        tickData.append(putToBuy)
        # Changed the putToBuy strike price from 345 to 350 to prevent a match.
        putToSell = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                            strikePrice=decimal.Decimal(345),
                            expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                          "%m/%d/%Y"),
                            tradePrice=decimal.Decimal(1.25), settlementPrice=decimal.Decimal(1.25))
        tickData.append(putToSell)
        self.assertFalse(self.__shortPutVertical.updateValues(tickData))

    def testVerticalUpdateValuesNoUpdatePutToSellSettlementPriceIsNone(self):
        """Tests that the putVertical can't be updated since the settlement price of the putToSell is None."""
        tickData = []
        putToBuy = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                           strikePrice=decimal.Decimal(325),
                           expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                         "%m/%d/%Y"),
                           tradePrice=decimal.Decimal(0.4375), settlementPrice=decimal.Decimal(0.4375))
        tickData.append(putToBuy)
        # Changed the putToBuy strike price from 345 to 350 to prevent a match.
        putToSell = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                            strikePrice=decimal.Decimal(345),
                            expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                          "%m/%d/%Y"),
                            tradePrice=decimal.Decimal(1.25), settlementPrice=None)
        tickData.append(putToSell)
        self.assertFalse(self.__shortPutVertical.updateValues(tickData))

    def testVerticalGetNumberOfDaysLeft(self):
        """Tests that we calculate the number of days between two date / times correctly."""
        self.assertEqual(self.__shortPutVertical.getNumberOfDaysLeft(), 17)

    def testGetOpeningFeesSuccess(self):
        """Tests that we get the opening fees successfully."""
        self.__shortPutVertical.setOpeningFees(decimal.Decimal(100.0))
        self.assertEqual(self.__shortPutVertical.getOpeningFees(), decimal.Decimal(100.0))

    def testGetOpeningFeesNoFeesSet(self):
        """Tests that an exception is raised if no opening fees were set."""
        with self.assertRaisesRegex(
              ValueError, 'Opening fees have not been populated in the respective strategyManager class.'):
            self.__shortPutVertical.getOpeningFees()

    def testGetClosingFeesSuccess(self):
        """Tests that we get the opening fees successfully."""
        self.__shortPutVertical.setClosingFees(decimal.Decimal(90.0))
        self.assertEqual(self.__shortPutVertical.getClosingFees(), decimal.Decimal(90.0))

    def testGetClosingFeesNoFeesSet(self):
        """Tests that an exception is raised if no opening fees were set."""
        with self.assertRaisesRegex(
              ValueError, 'Closing fees have not been populated in the respective strategyManager class.'):
            self.__shortPutVertical.getClosingFees()


if __name__ == '__main__':
    unittest.main()
