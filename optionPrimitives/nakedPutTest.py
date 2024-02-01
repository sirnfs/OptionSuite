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
                       expirationDateTime=datetime.datetime.strptime('01/19/1990', "%m/%d/%Y"),
                       bidPrice=decimal.Decimal(0.438), askPrice=decimal.Decimal(0.563),
                       tradePrice=decimal.Decimal(0.5005), settlementPrice=decimal.Decimal(0.5005))
    self.__putToBuy = nakedPut.NakedPut(orderQuantity, contractMultiplier, putToBuy,
                                        optionPrimitive.TransactionType.BUY)
    self.__putToSellTradePrice = decimal.Decimal(1.125)
    putToSell = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(359.69),
                        strikePrice=decimal.Decimal(345), delta=-0.142391, vega=0.173239, theta=-0.094256,
                        gamma=0.0148523, dateTime=datetime.datetime.strptime('01/02/1990', "%m/%d/%Y"),
                        expirationDateTime=datetime.datetime.strptime('01/19/1990', "%m/%d/%Y"),
                        bidPrice=decimal.Decimal(1.0), askPrice=decimal.Decimal(1.25),
                        tradePrice=self.__putToSellTradePrice, settlementPrice=self.__putToSellTradePrice)

    self.__putToSell = nakedPut.NakedPut(orderQuantity, contractMultiplier, putToSell,
                                         optionPrimitive.TransactionType.SELL)

    # The parameters below are used to update the prices of the naked puts above.
    # We only update the underlying price and bid/ask prices. We do not touch the greeks, though they will also change.
    self.__putToBuyUpdate = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                                    strikePrice=decimal.Decimal(325), delta=-0.046858, vega=0.072881, theta=-0.066132,
                                    gamma=0.004438, dateTime=datetime.datetime.strptime('01/03/1990', "%m/%d/%Y"),
                                    expirationDateTime=datetime.datetime.strptime('01/19/1990', "%m/%d/%Y"),
                                    bidPrice=decimal.Decimal(0.375), askPrice=decimal.Decimal(0.5),
                                    tradePrice=decimal.Decimal(0.4375), settlementPrice=decimal.Decimal(0.4375))
    self.__putToSellUpdate = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                                     strikePrice=decimal.Decimal(345), delta=-0.15608, vega=0.178138, theta=-0.105865,
                                     gamma=0.015931, dateTime=datetime.datetime.strptime('01/03/1990', "%m/%d/%Y"),
                                     expirationDateTime=datetime.datetime.strptime('01/19/1990', "%m/%d/%Y"),
                                     bidPrice=decimal.Decimal(1.125), askPrice=decimal.Decimal(1.375),
                                     tradePrice=decimal.Decimal(1.25), settlementPrice=decimal.Decimal(1.25))

    # Load the JSON config for calculating commissions and fees. Test with Tastyworks as the brokerage.
    self.pricingSourceConfig = None
    self.pricingSource = 'tastyworks'
    with open('./dataHandler/pricingConfig.json') as config:
      fullConfig = json.load(config)
      self.pricingSourceConfig = fullConfig[self.pricingSource]

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
    self.__putToSell.updateValues([self.__putToSellUpdate])
    self.assertAlmostEqual(self.__putToSell.calcProfitLoss(), decimal.Decimal(-12.5))

  def testLongNakedPutCalcProfitLossWithDataUpdate(self):
    """Tests that the profit / loss is calculated correctly when new data is available."""
    self.__putToBuy.updateValues([self.__putToBuyUpdate])
    self.assertAlmostEqual(self.__putToBuy.calcProfitLoss(), decimal.Decimal(-6.3))

  def testShortNakedPutCalcProfitLossPercentage(self):
    """Tests that the profit / loss percentage is calculated correctly after update."""
    self.__putToSell.updateValues([self.__putToSellUpdate])
    self.assertAlmostEqual(self.__putToSell.calcProfitLossPercentage(), decimal.Decimal(-11.111111111))

  def testLongNakedPutCalcProfitLossPercentage(self):
    """Tests that the profit / loss percentage is calculated correctly after update."""
    self.__putToBuy.updateValues([self.__putToBuyUpdate])
    self.assertAlmostEqual(self.__putToBuy.calcProfitLossPercentage(), decimal.Decimal(-12.587412587))

  def testShortNakedPutBuyingPower(self):
    # Tests the buying power calculation for the vertical.
    self.assertAlmostEqual(self.__putToSell.getBuyingPower(), decimal.Decimal(5837.3))

  def testLongNakedPutBuyingPower(self):
    # Tests the buying power calculation for the vertical.
    self.assertAlmostEqual(self.__putToBuy.getBuyingPower(), decimal.Decimal(50.05))

  def testShortNakedPutUpdateValuesNoMatchingOptionFound(self):
    """Tests that the profit loss calculation is unchanged if no option is available to update."""
    initialProfitLoss = self.__putToSell.calcProfitLoss()
    tickData = []
    # Changed the put strike price from 345 to 355 to prevent a match.
    putToUpdate = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                          strikePrice=decimal.Decimal(355), delta=-0.15608, vega=0.178138, theta=-0.105865,
                          gamma=0.015931, dateTime=datetime.datetime.strptime('01/03/1990', "%m/%d/%Y"),
                          expirationDateTime=datetime.datetime.strptime('01/19/1990', "%m/%d/%Y"),
                          bidPrice=decimal.Decimal(1.125), askPrice=decimal.Decimal(1.375),
                          tradePrice=decimal.Decimal(1.25), settlementPrice=decimal.Decimal(1.25))
    tickData.append(putToUpdate)
    self.__putToSell.updateValues(tickData)

    # The profit / loss should be the same since the option wasn't updated.
    self.assertAlmostEqual(self.__putToSell.calcProfitLoss(), initialProfitLoss)

  def testShortNakedPutGetNumberOfDaysLeft(self):
    """Tests that we calculate the number of days between two date / times correctly."""
    self.assertEqual(self.__putToSell.getNumberOfDaysLeft(), 17)

  def testShortNakedPutGetCommissionsAndFeesOpenForTastyworksIdxOptions(self):
    """Tests that the commissions and fees are calculated correctly on trade open for TW index options."""
    indexOptionOpen = self.pricingSourceConfig['stock_options']['index_option']['open']
    secFees = indexOptionOpen['sec_fee_per_contract_wo_trade_price'] * float(self.__putToSellTradePrice)
    self.assertAlmostEqual(self.__putToSell.getCommissionsAndFees('open', self.pricingSource, self.pricingSourceConfig),
                           decimal.Decimal(self.__putToSell.getNumContracts()*(
                             indexOptionOpen['commission_per_contract'] + indexOptionOpen['clearing_fee_per_contract'] +
                             indexOptionOpen['orf_fee_per_contract'] +
                             indexOptionOpen['proprietary_index_fee_per_contract'] + secFees)))

  def testShortNakedPutGetCommissionsAndFeesCloseForTastyworksIdxOptions(self):
    """Tests that the commissions and fees are calculated correctly on trade close for TW index options."""
    indexOptionClose = self.pricingSourceConfig['stock_options']['index_option']['close']
    secFees = indexOptionClose['sec_fee_per_contract_wo_trade_price'] * float(self.__putToSellTradePrice)
    self.assertAlmostEqual(self.__putToSell.getCommissionsAndFees('close', self.pricingSource,
                                                                  self.pricingSourceConfig),
                           decimal.Decimal(self.__putToSell.getNumContracts()*(
                             indexOptionClose['commission_per_contract'] +
                             indexOptionClose['clearing_fee_per_contract'] +
                             indexOptionClose['orf_fee_per_contract'] +
                             indexOptionClose['proprietary_index_fee_per_contract'] + secFees)))

  def testShortNakedPutGetCommissionsAndFeesInvalidOpenOrCloseTypeForTastyworksIdxOptions(self):
    """Tests that an exception is raised if the type is not 'open' or 'close' for TW index options."""
    with self.assertRaisesRegex(TypeError, 'Only open or close types can be provided to getCommissionsAndFees().'):
      self.__putToSell.getCommissionsAndFees('invalid_type', self.pricingSource, self.pricingSourceConfig)

  def testShortNakedPutGetCommissionsAndFeesOpenForTastyworksFuturesOptions(self):
    """Tests that the commissions and fees are calculated correctly on trade open for TW futures options."""
    pricingSourceConfig = None
    pricingSource = 'tastyworks_futures'
    with open('./dataHandler/pricingConfig.json') as config:
      fullConfig = json.load(config)
      pricingSourceConfig = fullConfig[pricingSource]
    futuresOptionOpen = pricingSourceConfig['futures_options']['es_option']['open']
    self.assertAlmostEqual(self.__putToSell.getCommissionsAndFees('open', pricingSource, pricingSourceConfig),
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
    self.assertAlmostEqual(self.__putToSell.getCommissionsAndFees('close', pricingSource, pricingSourceConfig),
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
    with self.assertRaisesRegex(TypeError, 'Only open or close types can be provided to getCommissionsAndFees().'):
      self.__putToSell.getCommissionsAndFees('invalid_type', pricingSource, pricingSourceConfig)

if __name__ == '__main__':
    unittest.main()