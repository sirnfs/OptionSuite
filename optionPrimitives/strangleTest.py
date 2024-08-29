import unittest
from optionPrimitives import optionPrimitive
from optionPrimitives import strangle
from base import put
from base import call
import datetime
import decimal
import json


class TestStrangle(unittest.TestCase):

    def setUp(self):
        orderQuantity = 1
        self.contractMultiplier = 100
        # Load the JSON config for calculating commissions and fees. Test with Tastyworks as the brokerage.
        self.pricingSourceConfig = None
        self.pricingSource = 'tastyworks'
        with open('./dataHandler/pricingConfig.json') as config:
            fullConfig = json.load(config)
            self.pricingSourceConfig = fullConfig[self.pricingSource]

        self.__putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                                strikePrice=decimal.Decimal(2690), delta=0.15, vega=0.04, theta=-0.07, gamma=0.11,
                                dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                                expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                                tradePrice=decimal.Decimal(7.475), settlementPrice=decimal.Decimal(7.475))
        self.__callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                                   strikePrice=decimal.Decimal(2855), delta=-0.16, vega=0.05, theta=-0.06, gamma=0.12,
                                   dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                                   expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                                 "%m/%d/%Y"),
                                   tradePrice=decimal.Decimal(5.30), settlementPrice=decimal.Decimal(5.30))
        self.__strangleObj = strangle.Strangle(orderQuantity=orderQuantity, contractMultiplier=self.contractMultiplier,
                                               callOpt=self.__callOpt, putOpt=self.__putOpt,
                                               buyOrSell=optionPrimitive.TransactionType.SELL)
        # The parameters below are used to update the prices of the initial strangle above.
        self.__tickData = []
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2790.0),
                         strikePrice=decimal.Decimal(2690),
                         delta=0.13, vega=0.03, theta=-0.06, gamma=0.12,
                         dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                         settlementPrice=decimal.Decimal(7.30))
        self.__tickData.append(putOpt)
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2790.0),
                            strikePrice=decimal.Decimal(2855), delta=-0.20, vega=0.06, theta=-0.07, gamma=0.14,
                            dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                          "%m/%d/%Y"),
                            settlementPrice=decimal.Decimal(5.70))
        self.__tickData.append(callOpt)

    def testGetDateTime(self):
        """Tests that the dateTime value is pulled correctly."""
        self.assertEqual(self.__strangleObj.getDateTime(), datetime.datetime.strptime('01/01/2021',
                                                                                      "%m/%d/%Y"))

    def testGetExpirationDateTime(self):
        """Tests that the expirationDateTime is pulled correctly."""
        self.assertEqual(self.__strangleObj.getExpirationDateTime(), datetime.datetime.strptime(
            '01/20/2021', "%m/%d/%Y"))

    def testGetUnderlyingTicker(self):
        """Tests that the underlyingTicker symbol is pulled correctly."""
        self.assertEqual(self.__strangleObj.getUnderlyingTicker(), 'SPX')

    def testGetUnderlyingPrice(self):
        """Tests that the underlyingPrice is pulled correctly."""
        self.assertEqual(self.__strangleObj.getUnderlyingPrice(), decimal.Decimal(2786.24))

    def testGetDelta(self):
        """Tests that delta values are summed for the strangle."""
        self.assertAlmostEqual(self.__strangleObj.getDelta(), -0.01)

    def testGetDeltaMultipleContracts(self):
        """Tests that delta values are summed for the strangle."""
        self.__strangleObj.setNumContracts(2)
        self.assertAlmostEqual(self.__strangleObj.getDelta(), -0.02)
        self.__strangleObj.setNumContracts(1)

    def testGetDeltaNoneValue(self):
        """Tests that a value of None is returned if one of the delta is None."""
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                         strikePrice=decimal.Decimal(2690), delta=None,
                         dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                       "%m/%d/%Y"),
                         tradePrice=decimal.Decimal(7.475), settlementPrice=decimal.Decimal(7.475))
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                            strikePrice=decimal.Decimal(2855), delta=-0.16,
                            dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                          "%m/%d/%Y"),
                            tradePrice=decimal.Decimal(5.30),
                            settlementPrice=decimal.Decimal(5.30))
        strangleObj = strangle.Strangle(orderQuantity=1, contractMultiplier=self.contractMultiplier, callOpt=callOpt,
                                        putOpt=putOpt, buyOrSell=optionPrimitive.TransactionType.SELL)
        self.assertIsNone(strangleObj.getDelta())

    def testGetVega(self):
        """Tests that vega values are summed for the strangle."""
        self.assertAlmostEqual(self.__strangleObj.getVega(), 0.09)

    def testGetVegaMultipleContracts(self):
        """Tests that vega values are summed for the strangle."""
        self.__strangleObj.setNumContracts(2)
        self.assertAlmostEqual(self.__strangleObj.getVega(), 0.18)
        self.__strangleObj.setNumContracts(1)

    def testGetVegaNoneValue(self):
        """Tests that a value of None is returned if one of the vega is None."""
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                         strikePrice=decimal.Decimal(2690), delta=0.15, vega=None,
                         dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                       "%m/%d/%Y"),
                         tradePrice=decimal.Decimal(7.475), settlementPrice=decimal.Decimal(7.475))
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                            strikePrice=decimal.Decimal(2855), delta=-0.16, vega=0.05,
                            dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                          "%m/%d/%Y"),
                            tradePrice=decimal.Decimal(5.30), settlementPrice=decimal.Decimal(5.30))
        strangleObj = strangle.Strangle(orderQuantity=1, contractMultiplier=self.contractMultiplier, callOpt=callOpt,
                                        putOpt=putOpt, buyOrSell=optionPrimitive.TransactionType.SELL)
        self.assertIsNone(strangleObj.getVega())

    def testGetTheta(self):
        """Tests that theta values are summed for the strangle."""
        self.assertAlmostEqual(self.__strangleObj.getTheta(), -0.13)

    def testGetThetaMultipleContracts(self):
        """Tests that theta values are summed for the strangle."""
        self.__strangleObj.setNumContracts(2)
        self.assertAlmostEqual(self.__strangleObj.getTheta(), -0.26)
        self.__strangleObj.setNumContracts(1)

    def testGetThetaNoneValue(self):
        """Tests that a value of None is returned if one of the theta is None."""
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                         strikePrice=decimal.Decimal(2690), delta=0.15, vega=None,
                         theta=None, dateTime=datetime.datetime.strptime('01/01/2021',
                                                                         "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                       "%m/%d/%Y"),
                         tradePrice=decimal.Decimal(7.475), settlementPrice=decimal.Decimal(7.475))
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                            strikePrice=decimal.Decimal(2855), delta=-0.16, vega=0.05,
                            theta=-0.06, dateTime=datetime.datetime.strptime('01/01/2021',
                                                                             "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                          "%m/%d/%Y"),
                            tradePrice=decimal.Decimal(5.30), settlementPrice=decimal.Decimal(5.30))
        strangleObj = strangle.Strangle(orderQuantity=1, contractMultiplier=self.contractMultiplier, callOpt=callOpt,
                                        putOpt=putOpt, buyOrSell=optionPrimitive.TransactionType.SELL)
        self.assertIsNone(strangleObj.getTheta())

    def testGetGamma(self):
        """Tests that gamma values are summed for the strangle."""
        self.assertAlmostEqual(self.__strangleObj.getGamma(), 0.23)

    def testGetGammaMultipleContracts(self):
        """Tests that theta values are summed for the strangle."""
        self.__strangleObj.setNumContracts(2)
        self.assertAlmostEqual(self.__strangleObj.getGamma(), 0.46)
        self.__strangleObj.setNumContracts(1)

    def testGetGammaNoneValue(self):
        """Tests that a value of None is returned if one of the theta is None."""
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                         strikePrice=decimal.Decimal(2690), delta=0.15, vega=None,
                         theta=None, gamma=None, dateTime=datetime.datetime.strptime('01/01/2021',
                                                                                     "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                       "%m/%d/%Y"),
                         tradePrice=decimal.Decimal(7.475), settlementPrice=decimal.Decimal(7.475))
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                            strikePrice=decimal.Decimal(2855), delta=-0.16, vega=0.05,
                            theta=-0.06, gamma=0.12, dateTime=datetime.datetime.strptime('01/01/2021',
                                                                                         "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                          "%m/%d/%Y"),
                            tradePrice=decimal.Decimal(5.30), settlementPrice=decimal.Decimal(5.30))
        strangleObj = strangle.Strangle(orderQuantity=1, contractMultiplier=self.contractMultiplier, callOpt=callOpt,
                                        putOpt=putOpt, buyOrSell=optionPrimitive.TransactionType.SELL)
        self.assertIsNone(strangleObj.getGamma())

    def testGetNumContracts(self):
        """Tests that the numContracts is pulled correctly."""
        self.assertEqual(self.__strangleObj.getNumContracts(), 1)

    def testGetContractMultiplier(self):
        """Tests that the contractMultiplier is pulled correctly."""
        self.assertEqual(self.__strangleObj.getContractMultiplier(), self.contractMultiplier)

    def testSetNumContracts(self):
        """Tests that the numContracts is set correctly."""
        self.__strangleObj.setNumContracts(2)
        self.assertEqual(self.__strangleObj.getNumContracts(), 2)

    def testSetNumContractsInvalidContractNumber(self):
        """Tests that an exception is raised if an invalid contract number is specified."""
        with self.assertRaisesRegex(ValueError,
                                    'Number of contracts must be a positive \(> 0\) number.'):
            self.__strangleObj.setNumContracts(-1)

    def testStrangleCalcProfitLossNoDataUpdate(self):
        """Tests that the profit / loss is zero if we haven't updated the option."""
        self.assertAlmostEqual(self.__strangleObj.calcProfitLoss(), decimal.Decimal(0.0))

    def testStrangleCalcProfitLossWithDataUpdateSellingStrangle(self):
        """Tests that the profit / loss is calculated correctly when new data is available."""
        self.__strangleObj.updateValues(self.__tickData)
        self.assertAlmostEqual(self.__strangleObj.calcProfitLoss(), decimal.Decimal(-22.5))

    def testStrangleCalcProfitLossWithDataUpdateBuyingStrangle(self):
        """Tests that the profit / loss is calculated correctly when buying a strangle."""
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                         strikePrice=decimal.Decimal(2690),
                         dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                         tradePrice=decimal.Decimal(7.475), settlementPrice=decimal.Decimal(7.475))
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                            strikePrice=decimal.Decimal(2855),
                            dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                          "%m/%d/%Y"),
                            tradePrice=decimal.Decimal(5.30), settlementPrice=decimal.Decimal(5.30))
        strangleObj = strangle.Strangle(orderQuantity=1, contractMultiplier=self.contractMultiplier, callOpt=callOpt,
                                        putOpt=putOpt, buyOrSell=optionPrimitive.TransactionType.BUY)
        # The parameters below are used to update the prices of the initial strangle above.
        tickData = []
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2790.0),
                         strikePrice=decimal.Decimal(2690),
                         dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                         settlementPrice=decimal.Decimal(7.30))
        tickData.append(putOpt)
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2790.0),
                            strikePrice=decimal.Decimal(2855),
                            dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                          "%m/%d/%Y"),
                            settlementPrice=decimal.Decimal(5.70))
        tickData.append(callOpt)
        strangleObj.updateValues(tickData)
        self.assertAlmostEqual(strangleObj.calcProfitLoss(), decimal.Decimal(22.5))

    def testCalculateRealizedProfitLoss(self):
        """Tests that the realized profit/loss is calculated correctly."""
        # Setting an arbitrary closing fee here just for the purposes of the test.
        self.__strangleObj.updateValues(self.__tickData)
        self.__strangleObj.setClosingFees(decimal.Decimal(1.50))
        self.assertAlmostEqual(self.__strangleObj.calcRealizedProfitLoss(), self.__strangleObj.calcProfitLoss() - (
            self.__strangleObj.getClosingFees() * self.__strangleObj.getNumContracts()))

    def testStrangeCalcProfitLossPercentage(self):
        """Tests that the profit / loss percentage is calculated correctly."""
        self.__strangleObj.updateValues(self.__tickData)
        self.assertAlmostEqual(self.__strangleObj.calcProfitLossPercentage(), decimal.Decimal(-1.76125244618395))

    def testStrangleBuyingPower20PercentRulePut(self):
        # Tests the buying power calculation for the 20% rule where put side uses max buying power.
        buyingPower = self.__strangleObj.getBuyingPower()
        self.assertAlmostEqual(buyingPower, decimal.Decimal(49378.8))

    def testStrangleBuyingPower20PercentRuleCall(self):
        # Tests the buying power calculation for the 20% rule where call side uses max buying power.
        orderQuantity = 1
        self.contractMultiplier = 100
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786),
                         strikePrice=decimal.Decimal(2690), delta=0.15, vega=0.04, theta=-0.07, gamma=0.11,
                         dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                         tradePrice=decimal.Decimal(5.30), settlementPrice=decimal.Decimal(5.30))
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786),
                            strikePrice=decimal.Decimal(2882), delta=-0.16, vega=0.05, theta=-0.06, gamma=0.12,
                            dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                          "%m/%d/%Y"),
                            tradePrice=decimal.Decimal(7.50), settlementPrice=decimal.Decimal(7.50))
        strangleObj = strangle.Strangle(orderQuantity=orderQuantity, contractMultiplier=self.contractMultiplier,
                                        callOpt=callOpt, putOpt=putOpt,
                                        buyOrSell=optionPrimitive.TransactionType.SELL)
        buyingPower = strangleObj.getBuyingPower()
        self.assertAlmostEqual(buyingPower, decimal.Decimal(46870))

    def testStrangleBuyingPower10PercentRulePut(self):
        # Tests the buying power calculation for the 10% rule where put side uses max buying power.
        orderQuantity = 1
        self.contractMultiplier = 100
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(100),
                         strikePrice=decimal.Decimal(50), delta=0.15, vega=0.04, theta=-0.07, gamma=0.11,
                         dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                         tradePrice=decimal.Decimal(20.0), settlementPrice=decimal.Decimal(20.0))
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(100),
                            strikePrice=decimal.Decimal(150), delta=-0.16, vega=0.05, theta=-0.06, gamma=0.12,
                            dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                          "%m/%d/%Y"),
                            tradePrice=decimal.Decimal(5.00), settlementPrice=decimal.Decimal(5.00))
        strangleObj = strangle.Strangle(orderQuantity=orderQuantity, contractMultiplier=self.contractMultiplier,
                                        callOpt=callOpt, putOpt=putOpt,
                                        buyOrSell=optionPrimitive.TransactionType.SELL)
        buyingPower = strangleObj.getBuyingPower()
        self.assertAlmostEqual(buyingPower, decimal.Decimal(2500.0))

    def testStrangleBuyingPower10PercentRuleCall(self):
        # Tests the buying power calculation for the 10% rule where call side uses max buying power.
        orderQuantity = 1
        self.contractMultiplier = 100
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(100),
                         strikePrice=decimal.Decimal(50), delta=0.15, vega=0.04, theta=-0.07, gamma=0.11,
                         dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                         tradePrice=decimal.Decimal(5.0), settlementPrice=decimal.Decimal(5.0))
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(100),
                            strikePrice=decimal.Decimal(150), delta=-0.16, vega=0.05, theta=-0.06, gamma=0.12,
                            dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                          "%m/%d/%Y"),
                            tradePrice=decimal.Decimal(20.00), settlementPrice=decimal.Decimal(20.00))
        strangleObj = strangle.Strangle(orderQuantity=orderQuantity, contractMultiplier=self.contractMultiplier,
                                        callOpt=callOpt, putOpt=putOpt,
                                        buyOrSell=optionPrimitive.TransactionType.SELL)
        buyingPower = strangleObj.getBuyingPower()
        self.assertAlmostEqual(buyingPower, decimal.Decimal(3500.0))

    def testStrangleGetCommissionsAndFeesOpen(self):
        """Tests that the commissions and fees are calculated correctly on trade open."""
        indexOptionOpen = self.pricingSourceConfig['stock_options']['index_option']['open']
        self.assertAlmostEqual(self.__strangleObj.getCommissionsAndFees('open', self.pricingSource,
                                                                        self.pricingSourceConfig),
                               decimal.Decimal(2 * (indexOptionOpen['commission_per_contract'] + indexOptionOpen[
                                   'clearing_fee_per_contract'] + indexOptionOpen['orf_fee_per_contract'])))

    def testStrangleGetCommissionsAndFeesClose(self):
        """Tests that the commissions and fees are calculated correctly on trade close."""
        indexOptionClose = self.pricingSourceConfig['stock_options']['index_option']['close']
        putToSellMidPrice = self.__putOpt.settlementPrice
        callToSellMidPrice = self.__callOpt.settlementPrice

        secFeesPut = decimal.Decimal(
            indexOptionClose['sec_fee_per_contract_wo_trade_price'] * float(putToSellMidPrice))
        secFeesCall = decimal.Decimal(
            indexOptionClose['sec_fee_per_contract_wo_trade_price'] * float(callToSellMidPrice))
        putFees = decimal.Decimal(indexOptionClose['commission_per_contract'] +
                                  indexOptionClose['clearing_fee_per_contract'] +
                                  indexOptionClose['orf_fee_per_contract'] +
                                  indexOptionClose['finra_taf_per_contract']) + secFeesPut
        callFees = decimal.Decimal(indexOptionClose['commission_per_contract'] +
                                   indexOptionClose['clearing_fee_per_contract'] +
                                   indexOptionClose['orf_fee_per_contract'] +
                                   indexOptionClose['finra_taf_per_contract']) + secFeesCall
        self.assertAlmostEqual(self.__strangleObj.getCommissionsAndFees('close', self.pricingSource,
                                                                        self.pricingSourceConfig), putFees + callFees)

    def testStrangleGetCommissionsAndFeesInvalidOpenOrCloseType(self):
        """Tests that an exception is raised if the type is not 'open' or 'close'."""
        with self.assertRaisesRegex(
              TypeError, 'Only open or close types can be provided to getCommissionsAndFees().'):
            self.__strangleObj.getCommissionsAndFees('invalid_type', self.pricingSource,
                                                     self.pricingSourceConfig)

    def testFuturesStrangleGetCommissionsAndFeesOpen(self):
        """Tests that the commissions and fees are calculated correctly on trade open (for futures options)."""
        # Load the JSON config for calculating commissions and fees. Test with Tastyworks as the brokerage.
        pricingSourceConfig = None
        pricingSource = 'tastyworks_futures'
        with open('./dataHandler/pricingConfig.json') as config:
            fullConfig = json.load(config)
            pricingSourceConfig = fullConfig[pricingSource]
        futuresOptionOpen = pricingSourceConfig['futures_options']['es_option']['open']
        self.assertAlmostEqual(self.__strangleObj.getCommissionsAndFees('open', pricingSource,
                                                                        pricingSourceConfig),
                               decimal.Decimal(2 * (futuresOptionOpen['commission_per_contract'] + futuresOptionOpen[
                                 'clearing_fee_per_contract'] + futuresOptionOpen['nfa_fee_per_contract'] +
                                 futuresOptionOpen['exchange_fee_per_contract'])))

    def testFuturesStrangleGetCommissionsAndFeesClose(self):
        """Tests that the commissions and fees are calculated correctly on trade close (for futures options)."""
        # Load the JSON config for calculating commissions and fees. Test with Tastyworks as the brokerage.
        pricingSourceConfig = None
        pricingSource = 'tastyworks_futures'
        with open('./dataHandler/pricingConfig.json') as config:
            fullConfig = json.load(config)
            pricingSourceConfig = fullConfig[pricingSource]
        futuresOptionClose = pricingSourceConfig['futures_options']['es_option']['close']
        self.assertAlmostEqual(self.__strangleObj.getCommissionsAndFees('close', pricingSource,
                                                                        pricingSourceConfig),
                               decimal.Decimal(2 * (futuresOptionClose['commission_per_contract'] + futuresOptionClose[
                                 'clearing_fee_per_contract'] + futuresOptionClose['nfa_fee_per_contract'] +
                                 futuresOptionClose['exchange_fee_per_contract'])))

    def testFuturesStrangleGetCommissionsAndFeesInvalidOpenOrCloseType(self):
        """Tests that an exception is raised if the type is not 'open' or 'close' (for futures options)."""
        pricingSourceConfig = None
        pricingSource = 'tastyworks_futures'
        with open('./dataHandler/pricingConfig.json') as config:
            fullConfig = json.load(config)
            pricingSourceConfig = fullConfig[pricingSource]
        with self.assertRaisesRegex(
              TypeError, 'Only open or close types can be provided to getCommissionsAndFees().'):
            self.__strangleObj.getCommissionsAndFees('invalid_type', pricingSource, pricingSourceConfig)

    def testStrangleUpdateValuesNoMatchingPutOption(self):
        """Tests that updateValues returns False if no put option is available to update."""
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                         strikePrice=decimal.Decimal(2690),
                         dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                         tradePrice=decimal.Decimal(7.475), settlementPrice=decimal.Decimal(7.475))
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                            strikePrice=decimal.Decimal(2855),
                            dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                          "%m/%d/%Y"),
                            tradePrice=decimal.Decimal(5.30), settlementPrice=decimal.Decimal(5.30))
        strangleObj = strangle.Strangle(orderQuantity=1, contractMultiplier=self.contractMultiplier, callOpt=callOpt,
                                        putOpt=putOpt, buyOrSell=optionPrimitive.TransactionType.BUY)

        # Changed the PUT strike price from 2690 to 2790 to prevent a match.
        tickData = [put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2790.0),
                            strikePrice=decimal.Decimal(2790),
                            dateTime=datetime.datetime.strptime('01/02/2021', "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                            settlementPrice=decimal.Decimal(7.30))]
        self.assertFalse(strangleObj.updateValues(tickData))

    def testStrangleUpdateValuesPutOptionNoSettlementPrice(self):
        """Tests that updatesValues returns False if the put has no settlementPrice."""
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                         strikePrice=decimal.Decimal(2690),
                         dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                         tradePrice=decimal.Decimal(7.475), settlementPrice=decimal.Decimal(7.475))
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                            strikePrice=decimal.Decimal(2855),
                            dateTime=datetime.datetime.strptime('01/02/2021', "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                          "%m/%d/%Y"),
                            tradePrice=decimal.Decimal(5.30), settlementPrice=decimal.Decimal(5.30))
        strangleObj = strangle.Strangle(orderQuantity=1, contractMultiplier=self.contractMultiplier, callOpt=callOpt,
                                        putOpt=putOpt, buyOrSell=optionPrimitive.TransactionType.BUY)

        tickData = [put.Put(
            underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2790.0),
            strikePrice=decimal.Decimal(2690),
            dateTime=datetime.datetime.strptime('01/02/2021', "%m/%d/%Y"),
            expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
            settlementPrice=None)]
        self.assertFalse(strangleObj.updateValues(tickData))

    def testStrangleUpdateValuesNoMatchingCallOption(self):
        """Tests that updateValues returns False if no call option is available to update."""
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                         strikePrice=decimal.Decimal(2690),
                         dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                         tradePrice=decimal.Decimal(7.475), settlementPrice=decimal.Decimal(7.475))
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                            strikePrice=decimal.Decimal(2855),
                            dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                          "%m/%d/%Y"),
                            tradePrice=decimal.Decimal(5.30), settlementPrice=decimal.Decimal(5.30))
        strangleObj = strangle.Strangle(orderQuantity=1, contractMultiplier=self.contractMultiplier, callOpt=callOpt,
                                        putOpt=putOpt, buyOrSell=optionPrimitive.TransactionType.BUY)

        # Changed the CALL strike price from 2855 to 2860 to prevent a match.
        tickData = [put.Put(
            underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2790.0),
            strikePrice=decimal.Decimal(2690),
            dateTime=datetime.datetime.strptime('01/02/2021', "%m/%d/%Y"),
            expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
            settlementPrice=decimal.Decimal(7.30)),
                    call.Call(
            underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2790.0),
            strikePrice=decimal.Decimal(2860),
            dateTime=datetime.datetime.strptime('01/02/2021', "%m/%d/%Y"),
            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                          "%m/%d/%Y"),
            settlementPrice=decimal.Decimal(5.00))]
        self.assertFalse(strangleObj.updateValues(tickData))

    def testStrangleUpdateValuesCallOptionNoSettlementPrice(self):
        """Tests that updateValues returns False if call option has no settlementPrice."""
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                         strikePrice=decimal.Decimal(2690),
                         dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                         tradePrice=decimal.Decimal(7.475), settlementPrice=decimal.Decimal(7.475))
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                            strikePrice=decimal.Decimal(2855),
                            dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                          "%m/%d/%Y"),
                            tradePrice=decimal.Decimal(5.30), settlementPrice=decimal.Decimal(5.30))
        strangleObj = strangle.Strangle(orderQuantity=1, contractMultiplier=self.contractMultiplier, callOpt=callOpt,
                                        putOpt=putOpt, buyOrSell=optionPrimitive.TransactionType.BUY)

        tickData = [put.Put(
            underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2790.0),
            strikePrice=decimal.Decimal(2690),
            dateTime=datetime.datetime.strptime('01/02/2021', "%m/%d/%Y"),
            expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
            settlementPrice=decimal.Decimal(7.30)),
                    call.Call(
            underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2790.0),
            strikePrice=decimal.Decimal(2855),
            dateTime=datetime.datetime.strptime('01/02/2021', "%m/%d/%Y"),
            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                          "%m/%d/%Y"),
            settlementPrice=None)]
        self.assertFalse(strangleObj.updateValues(tickData))

    def testStrangleUpdateValuesSuccess(self):
        """Tests that updateValues returns True when options are updated."""
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                         strikePrice=decimal.Decimal(2690),
                         dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                         tradePrice=decimal.Decimal(7.475), settlementPrice=decimal.Decimal(7.475))
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                            strikePrice=decimal.Decimal(2855),
                            dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                          "%m/%d/%Y"),
                            tradePrice=decimal.Decimal(5.30), settlementPrice=decimal.Decimal(5.30))
        strangleObj = strangle.Strangle(orderQuantity=1, contractMultiplier=self.contractMultiplier, callOpt=callOpt,
                                        putOpt=putOpt, buyOrSell=optionPrimitive.TransactionType.BUY)

        tickData = [put.Put(
            underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2790.0),
            strikePrice=decimal.Decimal(2690),
            dateTime=datetime.datetime.strptime('01/02/2021', "%m/%d/%Y"),
            expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
            settlementPrice=decimal.Decimal(7.30)),
                    call.Call(
            underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2790.0),
            strikePrice=decimal.Decimal(2855),
            dateTime=datetime.datetime.strptime('01/02/2021', "%m/%d/%Y"),
            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                          "%m/%d/%Y"),
            settlementPrice=decimal.Decimal(5.00))]
        self.assertTrue(strangleObj.updateValues(tickData))

    def testStrangeGetNumberOfDaysLeft(self):
        """Tests that we calculate the number of days between two date / times correctly."""
        putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                         strikePrice=decimal.Decimal(2690),
                         dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                         tradePrice=decimal.Decimal(7.475), settlementPrice=decimal.Decimal(7.475))
        callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                            strikePrice=decimal.Decimal(2855),
                            dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/20/2021',
                                                                          "%m/%d/%Y"),
                            tradePrice=decimal.Decimal(5.30), settlementPrice=decimal.Decimal(5.30))
        strangleObj = strangle.Strangle(orderQuantity=1, contractMultiplier=self.contractMultiplier, callOpt=callOpt,
                                        putOpt=putOpt, buyOrSell=optionPrimitive.TransactionType.SELL)
        self.assertEqual(strangleObj.getNumberOfDaysLeft(), 19)

    def testGetOpeningFeesSuccess(self):
        """Tests that we get the opening fees successfully."""
        self.__strangleObj.setOpeningFees(decimal.Decimal(100.0))
        self.assertEqual(self.__strangleObj.getOpeningFees(), decimal.Decimal(100.0))

    def testGetOpeningFeesNoFeesSet(self):
        """Tests that an exception is raised if no opening fees were set."""
        with self.assertRaisesRegex(
              ValueError, 'Opening fees have not been populated in the respective strategyManager class.'):
            self.__strangleObj.getOpeningFees()

    def testGetClosingFeesSuccess(self):
        """Tests that we get the opening fees successfully."""
        self.__strangleObj.setClosingFees(decimal.Decimal(90.0))
        self.assertEqual(self.__strangleObj.getClosingFees(), decimal.Decimal(90.0))

    def testGetClosingFeesNoFeesSet(self):
        """Tests that an exception is raised if no opening fees were set."""
        with self.assertRaisesRegex(
              ValueError, 'Closing fees have not been populated in the respective strategyManager class.'):
            self.__strangleObj.getClosingFees()


if __name__ == '__main__':
    unittest.main()
