import unittest
from optionPrimitives import optionPrimitive
from optionPrimitives import nakedPut
from base import put
import datetime
import decimal
import json


class TestNakedPut(unittest.TestCase):

    def setUp(self):
        orderQuantity = 1
        contractMultiplier = 100
        putToBuy = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(359.69),
                           strikePrice=decimal.Decimal(325), delta=-0.46, vega=0.07974, theta=-0.069166, gamma=0.004462,
                           dateTime=datetime.datetime.strptime('01/02/1990', "%m/%d/%Y"),
                           expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                         "%m/%d/%Y"),
                           tradeDateTime=datetime.datetime.strptime('03/09/2024',
                                                                    "%m/%d/%Y"),
                           tradePrice=decimal.Decimal(0.5005), settlementPrice=decimal.Decimal(0.5005))
        self.__putToBuy = nakedPut.NakedPut(orderQuantity, contractMultiplier, putToBuy,
                                            optionPrimitive.TransactionType.BUY)
        self.__putToSellTradePrice = decimal.Decimal(1.125)
        putToSell = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(359.69),
                            strikePrice=decimal.Decimal(345), delta=-0.142391, vega=0.173239, theta=-0.094256,
                            gamma=0.0148523, dateTime=datetime.datetime.strptime('01/02/1990',
                                                                                 "%m/%d/%Y"),
                            expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                          "%m/%d/%Y"),
                            tradeDateTime=datetime.datetime.strptime('03/09/2024',
                                                                     "%m/%d/%Y"),
                            tradePrice=self.__putToSellTradePrice, settlementPrice=self.__putToSellTradePrice)

        self.__putToSell = nakedPut.NakedPut(orderQuantity, contractMultiplier, putToSell,
                                             optionPrimitive.TransactionType.SELL)

        # The parameters below are used to update the prices of the naked puts above.
        # We only update the underlying price and bid/ask prices. We do not touch the greeks; they will also change.
        self.__putToBuyUpdate = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                                        strikePrice=decimal.Decimal(325), delta=-0.046858, vega=0.072881,
                                        theta=-0.066132,
                                        gamma=0.004438, dateTime=datetime.datetime.strptime('01/03/1990',
                                                                                            "%m/%d/%Y"),
                                        expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                                      "%m/%d/%Y"),
                                        tradeDateTime=datetime.datetime.strptime('03/09/2024',
                                                                                 "%m/%d/%Y"),
                                        tradePrice=decimal.Decimal(0.4375), settlementPrice=decimal.Decimal(0.4375))
        self.__putToSellUpdate = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                                         strikePrice=decimal.Decimal(345), delta=-0.15608, vega=0.178138,
                                         theta=-0.105865,
                                         gamma=0.015931, dateTime=datetime.datetime.strptime('01/03/1990',
                                                                                             "%m/%d/%Y"),
                                         expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                                       "%m/%d/%Y"),
                                         tradeDateTime=datetime.datetime.strptime('03/09/2024',
                                                                                  "%m/%d/%Y"),
                                         tradePrice=decimal.Decimal(1.25), settlementPrice=decimal.Decimal(1.25))

        # Load the JSON config for calculating commissions and fees. Test with Tastyworks as the brokerage.
        self.__pricingSourceConfig = None
        self.__pricingSource = 'tastyworks'
        with open('./dataHandler/pricingConfig.json') as config:
            fullConfig = json.load(config)
            self.__pricingSourceConfig = fullConfig[self.__pricingSource]

    def testGetDateTime(self):
        """Tests that the dateTime value is pulled correctly."""
        self.assertEqual(self.__putToBuy.getDateTime(), datetime.datetime.strptime('01/02/1990',
                                                                                   "%m/%d/%Y"))
        self.assertEqual(self.__putToSell.getDateTime(), datetime.datetime.strptime('01/02/1990',
                                                                                    "%m/%d/%Y"))

    def testGetTradeDateTime(self):
        """Tests that the tradeDateTime is pulled correctly."""
        self.assertEqual(self.__putToBuy.getTradeDateTime(), datetime.datetime.strptime('03/09/2024',
                                                                                        "%m/%d/%Y"))
        self.assertEqual(self.__putToSell.getTradeDateTime(), datetime.datetime.strptime('03/09/2024',
                                                                                         "%m/%d/%Y"))

    def testGetExpirationDateTime(self):
        """Tests that the expirationDateTime is pulled correctly."""
        self.assertEqual(self.__putToBuy.getExpirationDateTime(), datetime.datetime.strptime('01/19/1990',
                                                                                             "%m/%d/%Y"))
        self.assertEqual(self.__putToSell.getExpirationDateTime(), datetime.datetime.strptime(
            '01/19/1990', "%m/%d/%Y"))

    def testGetUnderlyingTicker(self):
        """Tests that the underlyingTicker symbol is pulled correctly."""
        self.assertEqual(self.__putToBuy.getUnderlyingTicker(), 'SPX')
        self.assertEqual(self.__putToSell.getUnderlyingTicker(), 'SPX')

    def testGetUnderlyingPrice(self):
        """Tests that the underlyingPrice value is pulled correctly."""
        self.assertEqual(self.__putToBuy.getUnderlyingPrice(), decimal.Decimal(359.69))
        self.assertEqual(self.__putToSell.getUnderlyingPrice(), decimal.Decimal(359.69))

    def testGetDelta(self):
        """Tests that delta values are pulled correctly for the naked puts."""
        self.assertAlmostEqual(self.__putToBuy.getDelta(), -0.46)
        self.assertAlmostEqual(self.__putToSell.getDelta(), -0.142391)

    def testGetVega(self):
        """Tests that vega values are pulled correctly for the naked puts."""
        self.assertAlmostEqual(self.__putToBuy.getVega(), 0.07974)
        self.assertAlmostEqual(self.__putToSell.getVega(), 0.173239)

    def testGetTheta(self):
        """Tests that theta values are pulled correctly for the naked puts."""
        self.assertAlmostEqual(self.__putToBuy.getTheta(), -0.069166)
        self.assertAlmostEqual(self.__putToSell.getTheta(), -0.094256)

    def testGetGamma(self):
        """Tests that gamma values pulled correctly for the naked puts."""
        self.assertAlmostEqual(self.__putToBuy.getGamma(), 0.004462)
        self.assertAlmostEqual(self.__putToSell.getGamma(), 0.0148523)

    def testGetNumContracts(self):
        """Tests that the numContracts is pulled correctly."""
        self.assertEqual(self.__putToBuy.getNumContracts(), 1)
        self.assertEqual(self.__putToSell.getNumContracts(), 1)

    def testGetContractMultiplier(self):
        """Tests that the contractMultiplier is pulled correctly."""
        self.assertEqual(self.__putToBuy.getContractMultiplier(), 100)
        self.assertEqual(self.__putToSell.getContractMultiplier(), 100)

    def testSetNumContracts(self):
        """Tests that the numContracts is set correctly."""
        self.__putToBuy.setNumContracts(2)
        self.__putToSell.setNumContracts(2)
        self.assertEqual(self.__putToBuy.getNumContracts(), 2)
        self.assertEqual(self.__putToSell.getNumContracts(), 2)

    def testSetNumContractsInvalidContractNumber(self):
        """Tests that an exception is raised if an invalid contract number is specified."""
        with self.assertRaisesRegex(ValueError,
                                    'Number of contracts must be a positive \(> 0\) number.'):
            self.__putToBuy.setNumContracts(-1)

    def testNakedPutCalcProfitLossNoDataUpdate(self):
        """Tests that the profit / loss is zero if we haven't updated the option."""
        self.assertAlmostEqual(self.__putToBuy.calcProfitLoss(), decimal.Decimal(0.0))
        self.assertAlmostEqual(self.__putToSell.calcProfitLoss(), decimal.Decimal(0.0))

    def testNakedPutCalcProfitLossPercentageNoDataUpdate(self):
        """Tests that the profit / loss is zero percent if we haven't updated the option."""
        self.assertAlmostEqual(self.__putToBuy.calcProfitLossPercentage(), decimal.Decimal(0.0))
        self.assertAlmostEqual(self.__putToSell.calcProfitLossPercentage(), decimal.Decimal(0.0))

    def testShortNakedPutCalcProfitLossWithDataUpdate(self):
        """Tests that the profit / loss is calculated correctly when new data is available."""
        # Settlement price goes from 1.125 to 1.25 (-0.125) after the update. With a short put, we want the option price
        # to decrease, so this will result in a loss.
        # (-0.125) * numContracts=1 * contractMultiplier=100 = -12.5
        self.__putToSell.updateValues([self.__putToSellUpdate])
        self.assertAlmostEqual(self.__putToSell.calcProfitLoss(), decimal.Decimal(-12.5))

    def testShortNakedPutCalcProfitLossPercentageWithDataUpdate(self):
        """Tests that the profit / loss percentage is calculated correctly after update."""
        # The totalCredit received is the tradePrice * numContracts * contractMultiplier = 1.125*1*100 = 112.5
        # (Loss / totalCredit)*100 = %, so -12.5 / 112.5 = -11.1%
        self.__putToSell.updateValues([self.__putToSellUpdate])
        self.assertAlmostEqual(self.__putToSell.calcProfitLossPercentage(), decimal.Decimal(-11.111111111))

    def testLongNakedPutCalcProfitLossWithDataUpdate(self):
        """Tests that the profit / loss is calculated correctly when new data is available."""
        # Settlement price goes from 0.5005 to 0.4375 (0.063) after the update. With a long put, we want the option
        # price to increase, so this will result in a loss.
        # -(0.063) * numContracts=1 * contractMultiplier=100 = -6.3
        self.__putToBuy.updateValues([self.__putToBuyUpdate])
        self.assertAlmostEqual(self.__putToBuy.calcProfitLoss(), decimal.Decimal(-6.3))

    def testLongNakedPutCalcProfitLossPercentageWithDataUpdate(self):
        """Tests that the profit / loss percentage is calculated correctly after update."""
        # The total debit when putting on the trade = tradePrice * numContracts * contractMultiplier = 0.5005*1*100 =
        # 50.05. (Loss / totalDebit)*100 = %, so -6.3 / 50.05 = -12.59%
        self.__putToBuy.updateValues([self.__putToBuyUpdate])
        self.assertAlmostEqual(self.__putToBuy.calcProfitLossPercentage(), decimal.Decimal(-12.587412587))

    def testShortNakedPutBuyingPowerRule1(self):
        # Tests the buying power calculation for the short put using Rule 1.
        self.assertAlmostEqual(self.__putToSell.getBuyingPower(), decimal.Decimal(5837.3))

    # When is BP2 > BP1?
    # 0.1*sp + cp > -0.8*up + sp + cp --> 0.1*sp > -0.8up + sp --> -0.9sp > -0.8up or 0.9sp < 0.8up, or sp < 0.8up/0.9,
    # sp < 0.8*50 / 0.9 = 44.4
    def testShortNakedPutBuyingPowerRule2(self):
        """Tests the buying power calculation for the short put using Rule 2."""
        # Buying power should be 0.1*strikePrice=40+settlementPrice=10.0*numContract=1*contractMultiplier=100 = 1400
        putToSell = put.Put(underlyingTicker='TEST', underlyingPrice=decimal.Decimal(50),
                            strikePrice=decimal.Decimal(40), settlementPrice=decimal.Decimal(10.0),
                            expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                          "%m/%d/%Y"),)
        putToSell = nakedPut.NakedPut(orderQuantity=1, contractMultiplier=100, putToBuyOrSell=putToSell,
                                      buyOrSell=optionPrimitive.TransactionType.SELL)
        self.assertAlmostEqual(putToSell.getBuyingPower(), decimal.Decimal(1400))

    def testLongNakedPutBuyingPowerRule(self):
        """Tests the buying power calculation for the long put."""
        self.assertAlmostEqual(self.__putToBuy.getBuyingPower(), decimal.Decimal(50.05))

    def testShortNakedPutGetCommissionsAndFeesOpenForTastyworksIdxOptions(self):
        """Tests that the commissions and fees are calculated correctly on trade open for TW index options."""
        indexOptionOpen = self.__pricingSourceConfig['stock_options']['index_option']['open']
        secFees = indexOptionOpen['sec_fee_per_contract_wo_trade_price'] * float(self.__putToSellTradePrice)
        self.assertAlmostEqual(
            self.__putToSell.getCommissionsAndFees('open', self.__pricingSource, self.__pricingSourceConfig),
            decimal.Decimal(self.__putToSell.getNumContracts() * (
                indexOptionOpen['commission_per_contract'] + indexOptionOpen['clearing_fee_per_contract'] +
                indexOptionOpen['orf_fee_per_contract'] +
                indexOptionOpen['proprietary_index_fee_per_contract'] + secFees)))

    def testShortNakedPutGetCommissionsAndFeesCloseForTastyworksIdxOptions(self):
        """Tests that the commissions and fees are calculated correctly on trade close for TW index options."""
        indexOptionClose = self.__pricingSourceConfig['stock_options']['index_option']['close']
        secFees = indexOptionClose['sec_fee_per_contract_wo_trade_price'] * float(self.__putToSellTradePrice)
        self.assertAlmostEqual(self.__putToSell.getCommissionsAndFees('close', self.__pricingSource,
                                                                      self.__pricingSourceConfig),
                               decimal.Decimal(self.__putToSell.getNumContracts() * (
                                   indexOptionClose['commission_per_contract'] +
                                   indexOptionClose['clearing_fee_per_contract'] +
                                   indexOptionClose['orf_fee_per_contract'] +
                                   indexOptionClose['proprietary_index_fee_per_contract'] + secFees)))

    def testShortNakedPutGetCommissionsAndFeesInvalidOpenOrCloseTypeForTastyworksIdxOptions(self):
        """Tests that an exception is raised if the type is not 'open' or 'close' for TW index options."""
        with self.assertRaisesRegex(TypeError,
                                    'Only open or close types can be provided to getCommissionsAndFees().'):
            self.__putToSell.getCommissionsAndFees('invalid_type', self.__pricingSource,
                                                   self.__pricingSourceConfig)

    def testShortNakedPutGetCommissionsAndFeesOpenForTastyworksFuturesOptions(self):
        """Tests that the commissions and fees are calculated correctly on trade open for TW futures options."""
        pricingSourceConfig = None
        pricingSource = 'tastyworks_futures'
        with open('./dataHandler/pricingConfig.json') as config:
            fullConfig = json.load(config)
            pricingSourceConfig = fullConfig[pricingSource]
        futuresOptionOpen = pricingSourceConfig['futures_options']['es_option']['open']
        self.assertAlmostEqual(self.__putToSell.getCommissionsAndFees('open', pricingSource,
                                                                      pricingSourceConfig),
                               decimal.Decimal(self.__putToSell.getNumContracts() * (
                                   futuresOptionOpen['commission_per_contract'] +
                                   futuresOptionOpen['clearing_fee_per_contract'] +
                                   futuresOptionOpen['nfa_fee_per_contract'] +
                                   futuresOptionOpen['exchange_fee_per_contract'])))

    def testShortNakedPutGetCommissionsAndFeesCloseForTastyworksFuturesOptions(self):
        """Tests that the commissions and fees are calculated correctly on trade close for TW futures options."""
        pricingSourceConfig = None
        pricingSource = 'tastyworks_futures'
        with open('./dataHandler/pricingConfig.json') as config:
            fullConfig = json.load(config)
            pricingSourceConfig = fullConfig[pricingSource]
        futuresOptionClose = pricingSourceConfig['futures_options']['es_option']['close']
        self.assertAlmostEqual(self.__putToSell.getCommissionsAndFees('close', pricingSource,
                                                                      pricingSourceConfig),
                               decimal.Decimal(self.__putToSell.getNumContracts() * (
                                   futuresOptionClose['commission_per_contract'] +
                                   futuresOptionClose['clearing_fee_per_contract'] +
                                   futuresOptionClose['nfa_fee_per_contract'] +
                                   futuresOptionClose['exchange_fee_per_contract'])))

    def testShortNakedPutGetCommissionsAndFeesInvalidOpenOrCloseTypeForTastyworksFuturesOptions(self):
        """Tests that an exception is raised if the type is not 'open' or 'close' for TW futures options."""
        pricingSourceConfig = None
        pricingSource = 'tastyworks_futures'
        with open('./dataHandler/pricingConfig.json') as config:
            fullConfig = json.load(config)
            pricingSourceConfig = fullConfig[pricingSource]
        with self.assertRaisesRegex(TypeError,
                                    'Only open or close types can be provided to getCommissionsAndFees().'):
            self.__putToSell.getCommissionsAndFees('invalid_type', pricingSource, pricingSourceConfig)

    def testShortNakedPutUpdateValuesNoMatchingOptionWithStrikePriceFound(self):
        """Tests that the profit loss calculation is unchanged if no option is available to update."""
        initialProfitLoss = self.__putToSell.calcProfitLoss()
        # Changed the put strike price from 345 to 355 to prevent a match.
        putToUpdate = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                              strikePrice=decimal.Decimal(355), delta=-0.15608, vega=0.178138, theta=-0.105865,
                              gamma=0.015931, dateTime=datetime.datetime.strptime('01/03/1990',
                                                                                  "%m/%d/%Y"),
                              expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                            "%m/%d/%Y"),
                              tradePrice=decimal.Decimal(1.25), settlementPrice=decimal.Decimal(1.25))

        self.assertFalse(self.__putToSell.updateValues([putToUpdate]))
        # The profit / loss should be the same since the option wasn't updated.
        self.assertAlmostEqual(self.__putToSell.calcProfitLoss(), initialProfitLoss)

    def testShortNakedPutUpdateValuesNoSettlementPrice(self):
        """Tests that the profit loss calculation is unchanged if settlement price is None."""
        initialProfitLoss = self.__putToSell.calcProfitLoss()
        # Settlement price set to None.
        putToUpdate = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                              strikePrice=decimal.Decimal(345), delta=-0.15608, vega=0.178138, theta=-0.105865,
                              gamma=0.015931, dateTime=datetime.datetime.strptime('01/03/1990',
                                                                                  "%m/%d/%Y"),
                              expirationDateTime=datetime.datetime.strptime('01/19/1990',
                                                                            "%m/%d/%Y"),
                              tradePrice=decimal.Decimal(1.25), settlementPrice=None)

        self.assertFalse(self.__putToSell.updateValues([putToUpdate]))
        # The profit / loss should be the same since the option wasn't updated.
        self.assertAlmostEqual(self.__putToSell.calcProfitLoss(), initialProfitLoss)

    def testShortNakedPutGetNumberOfDaysLeft(self):
        """Tests that we calculate the number of days between two date / times correctly."""
        self.assertEqual(self.__putToSell.getNumberOfDaysLeft(), 17)

    def testGetOpeningFees(self):
        """Tests that the opening fee value returned is correct."""
        self.__putToSell.setOpeningFees(decimal.Decimal(100.0))
        self.assertEqual(self.__putToSell.getOpeningFees(), 100)

    def testGetClosingFees(self):
        """Tests that the opening fee value returned is correct."""
        self.__putToSell.setClosingFees(decimal.Decimal(200.0))
        self.assertEqual(self.__putToSell.getClosingFees(), 200)


if __name__ == '__main__':
    unittest.main()
