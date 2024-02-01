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
                              gamma=0.004462, dateTime=datetime.datetime.strptime('01/02/1990', "%m/%d/%Y"),
                              expirationDateTime=datetime.datetime.strptime('01/19/1990', "%m/%d/%Y"),
                              bidPrice=decimal.Decimal(0.438), askPrice=decimal.Decimal(0.563),
                              tradePrice=decimal.Decimal(0.5005), settlementPrice=decimal.Decimal(0.5005))
    self.__putToSell = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(359.69),
                               strikePrice=decimal.Decimal(345), delta=-0.142391, vega=0.173239, theta=-0.094256,
                               gamma=0.0148523, dateTime=datetime.datetime.strptime('01/02/1990', "%m/%d/%Y"),
                               expirationDateTime=datetime.datetime.strptime('01/19/1990', "%m/%d/%Y"),
                               bidPrice=decimal.Decimal(1.0), askPrice=decimal.Decimal(1.25),
                               tradePrice=decimal.Decimal(1.125), settlementPrice=decimal.Decimal(1.125))
    self.__shortPutVertical = putVertical.PutVertical(orderQuantity, self.contractMultiplier, self.__putToBuy,
                                                      self.__putToSell, optionPrimitive.TransactionType.SELL)
    # For long put vertical.
    temp = self.__putToSell
    putToSell = self.__putToBuy
    putToBuy = temp
    self.__longPutVertical = putVertical.PutVertical(orderQuantity, self.contractMultiplier, putToBuy, putToSell,
                                                     optionPrimitive.TransactionType.BUY)

    # The parameters below are used to update the prices of the put verticals above.
    # Update prices of short put vertical. We only updated the underlying price and bid/ask prices We did not touch the
    # Greeks, though they will also change.
    self.__shortPutVerticalTickData = []
    putToBuyUpdate = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                             strikePrice=decimal.Decimal(325), delta=-0.046858, vega=0.072881, theta=-0.066132,
                             gamma=0.004438, dateTime=datetime.datetime.strptime('01/03/1990', "%m/%d/%Y"),
                             expirationDateTime=datetime.datetime.strptime('01/19/1990', "%m/%d/%Y"),
                             bidPrice=decimal.Decimal(0.375), askPrice=decimal.Decimal(0.5),
                             tradePrice=decimal.Decimal(0.4375), settlementPrice=decimal.Decimal(0.4375))
    self.__shortPutVerticalTickData.append(putToBuyUpdate)
    putToSellUpdate = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                              strikePrice=decimal.Decimal(345), delta=-0.15608, vega=0.178138, theta=-0.105865,
                              gamma=0.015931, dateTime=datetime.datetime.strptime('01/03/1990', "%m/%d/%Y"),
                              expirationDateTime=datetime.datetime.strptime('01/19/1990', "%m/%d/%Y"),
                              bidPrice=decimal.Decimal(1.125), askPrice=decimal.Decimal(1.375),
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
    putToBuy = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(359.69),
                       strikePrice=decimal.Decimal(325), delta=-0.46, vega=0.07974, theta=-0.069166, gamma=0.004462,
                       dateTime=datetime.datetime.strptime('01/02/1990', "%m/%d/%Y"),
                       expirationDateTime=datetime.datetime.strptime('01/19/1990', "%m/%d/%Y"),
                       bidPrice=decimal.Decimal(0.438), askPrice=decimal.Decimal(0.563),
                       tradePrice=decimal.Decimal(0.5005), settlementPrice=decimal.Decimal(0.5005))
    putToSell = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(359.69),
                        strikePrice=decimal.Decimal(345), delta=-0.142391, vega=0.173239, theta=-0.094256,
                        gamma=0.0148523, dateTime=datetime.datetime.strptime('01/02/1990', "%m/%d/%Y"),
                        expirationDateTime=datetime.datetime.strptime('01/20/1990', "%m/%d/%Y"),
                        bidPrice=decimal.Decimal(1.0), askPrice=decimal.Decimal(1.25),
                        tradePrice=decimal.Decimal(1.125), settlementPrice=decimal.Decimal(1.125))
    orderQuantity = 1
    with self.assertRaisesRegex(ValueError, ('Both put options must have the same expiration.')):
      putVertical.PutVertical(orderQuantity, self.contractMultiplier, putToBuy, putToSell,
                              optionPrimitive.TransactionType.SELL)

  def testGetDelta(self):
    """Tests that delta values are summed for the verticals."""
    self.assertAlmostEqual(self.__shortPutVertical.getDelta(), -0.602391)
    self.assertAlmostEqual(self.__longPutVertical.getDelta(), -0.602391)

  def testGetDeltaNoneValue(self):
    """Tests that a value of None is returned if one of the delta is None."""
    putToBuy = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(359.69),
                       strikePrice=decimal.Decimal(325), delta=None, vega=0.07974, theta=-0.069166, gamma=0.004462,
                       dateTime=datetime.datetime.strptime('01/02/1990', "%m/%d/%Y"),
                       expirationDateTime=datetime.datetime.strptime('01/19/1990', "%m/%d/%Y"),
                       bidPrice=decimal.Decimal(0.438), askPrice=decimal.Decimal(0.563),
                       tradePrice=decimal.Decimal(0.5005), settlementPrice=decimal.Decimal(0.5005))
    putToSell = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(359.69),
                        strikePrice=decimal.Decimal(345), delta=-0.142391, vega=0.173239, theta=-0.094256,
                        gamma=0.0148523, dateTime=datetime.datetime.strptime('01/02/1990', "%m/%d/%Y"),
                        expirationDateTime=datetime.datetime.strptime('01/19/1990', "%m/%d/%Y"),
                        bidPrice=decimal.Decimal(1.0), askPrice=decimal.Decimal(1.25),
                        tradePrice=decimal.Decimal(1.125), settlementPrice=decimal.Decimal(1.125))
    putVerticalObj = putVertical.PutVertical(orderQuantity=1, contractMultiplier=self.contractMultiplier,
                                             putToBuy=putToBuy, putToSell=putToSell,
                                             buyOrSell=optionPrimitive.TransactionType.BUY)
    self.assertIsNone(putVerticalObj.getDelta())

  def testGetVega(self):
    """Tests that vega values are summed for the verticals."""
    self.assertAlmostEqual(self.__shortPutVertical.getVega(), 0.252979)

  def testGetVegaNoneValue(self):
    """Tests that a value of None is returned if one of the vega is None."""
    putToBuy = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(359.69),
                       strikePrice=decimal.Decimal(325), delta=-0.46, vega=0.07974, theta=-0.069166, gamma=0.004462,
                       dateTime=datetime.datetime.strptime('01/02/1990', "%m/%d/%Y"),
                       expirationDateTime=datetime.datetime.strptime('01/19/1990', "%m/%d/%Y"),
                       bidPrice=decimal.Decimal(0.438), askPrice=decimal.Decimal(0.563),
                       tradePrice=decimal.Decimal(0.5005), settlementPrice=decimal.Decimal(0.5005))
    putToSell = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(359.69),
                        strikePrice=decimal.Decimal(345), delta=-0.142391, vega=None, theta=-0.094256,
                        gamma=0.0148523, dateTime=datetime.datetime.strptime('01/02/1990', "%m/%d/%Y"),
                        expirationDateTime=datetime.datetime.strptime('01/19/1990', "%m/%d/%Y"),
                        bidPrice=decimal.Decimal(1.0), askPrice=decimal.Decimal(1.25),
                        tradePrice=decimal.Decimal(1.125), settlementPrice=decimal.Decimal(1.125))
    putVerticalObj = putVertical.PutVertical(orderQuantity=1, contractMultiplier=self.contractMultiplier,
                                             putToBuy=putToBuy, putToSell=putToSell,
                                             buyOrSell=optionPrimitive.TransactionType.BUY)
    self.assertIsNone(putVerticalObj.getVega())

  def testGetTheta(self):
    """Tests that theta values are summed for the verticals."""
    self.assertAlmostEqual(self.__shortPutVertical.getTheta(), -0.163422)

  def testGetThetaNoneValue(self):
    """Tests that a value of None is returned if one of the theta is None."""
    putToBuy = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(359.69),
                       strikePrice=decimal.Decimal(325), delta=-0.46, vega=0.07974, theta=None, gamma=0.004462,
                       dateTime=datetime.datetime.strptime('01/02/1990', "%m/%d/%Y"),
                       expirationDateTime=datetime.datetime.strptime('01/19/1990', "%m/%d/%Y"),
                       bidPrice=decimal.Decimal(0.438), askPrice=decimal.Decimal(0.563),
                       tradePrice=decimal.Decimal(0.5005), settlementPrice=decimal.Decimal(0.5005))
    putToSell = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(359.69),
                        strikePrice=decimal.Decimal(345), delta=-0.142391, vega=0.173239, theta=-0.094256,
                        gamma=0.0148523, dateTime=datetime.datetime.strptime('01/02/1990', "%m/%d/%Y"),
                        expirationDateTime=datetime.datetime.strptime('01/19/1990', "%m/%d/%Y"),
                        bidPrice=decimal.Decimal(1.0), askPrice=decimal.Decimal(1.25),
                        tradePrice=decimal.Decimal(1.125), settlementPrice=decimal.Decimal(1.125))
    orderQuantity = 1
    shortPutVertical = putVertical.PutVertical(orderQuantity, self.contractMultiplier, putToBuy, putToSell,
                                               optionPrimitive.TransactionType.SELL)
    self.assertIsNone(shortPutVertical.getTheta())

  def testGetGamma(self):
    """Tests that gamma values are summed for the verticals."""
    self.assertAlmostEqual(self.__shortPutVertical.getGamma(), 0.0193143)

  def testGetGammaNoneValue(self):
    """Tests that a value of None is returned if one of the theta is None."""
    putToBuy = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(359.69),
                       strikePrice=decimal.Decimal(325), delta=-0.46, vega=0.07974, theta=-0.069166, gamma=None,
                       dateTime=datetime.datetime.strptime('01/02/1990', "%m/%d/%Y"),
                       expirationDateTime=datetime.datetime.strptime('01/19/1990', "%m/%d/%Y"),
                       bidPrice=decimal.Decimal(0.438), askPrice=decimal.Decimal(0.563),
                       tradePrice=decimal.Decimal(0.5005), settlementPrice=decimal.Decimal(0.5005))
    putToSell = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(359.69),
                        strikePrice=decimal.Decimal(345), delta=-0.142391, vega=0.173239, theta=-0.094256,
                        gamma=0.0148523, dateTime=datetime.datetime.strptime('01/02/1990', "%m/%d/%Y"),
                        expirationDateTime=datetime.datetime.strptime('01/19/1990', "%m/%d/%Y"),
                        bidPrice=decimal.Decimal(1.0), askPrice=decimal.Decimal(1.25),
                        tradePrice=decimal.Decimal(1.125), settlementPrice=decimal.Decimal(1.125))
    orderQuantity = 1
    shortPutVertical = putVertical.PutVertical(orderQuantity, self.contractMultiplier, putToBuy, putToSell,
                                               optionPrimitive.TransactionType.SELL)
    self.assertIsNone(shortPutVertical.getGamma())

  def testPutVerticalCalcProfitLossNoDataUpdate(self):
    """Tests that the profit / loss is zero if we haven't updated the option."""
    self.assertAlmostEqual(self.__shortPutVertical.calcProfitLoss(), decimal.Decimal(0.0))

  def testPutVerticalCalcProfitLossPercentageNoDataUpdate(self):
    """Tests that the profit / loss is zero percent if we haven't updated the option."""
    self.assertAlmostEqual(self.__shortPutVertical.calcProfitLossPercentage(), decimal.Decimal(0.0))

  def testVerticalCalcProfitLossWithDataUpdate(self):
    """Tests that the profit / loss is calculated correctly when new data is available."""
    self.__shortPutVertical.updateValues(self.__shortPutVerticalTickData)
    self.assertAlmostEqual(self.__shortPutVertical.calcProfitLoss(), decimal.Decimal(-18.8))

  def testVerticalCalcProfitLossPercentage(self):
    """Tests that the profit / loss percentage is calculated correctly."""
    self.__shortPutVertical.updateValues(self.__shortPutVerticalTickData)
    self.assertAlmostEqual(self.__shortPutVertical.calcProfitLossPercentage(), decimal.Decimal(-30.1040832666))

  def testVerticalBuyingPower(self):
    # Tests the buying power calculation for the vertical.
    self.assertAlmostEqual(self.__shortPutVertical.getBuyingPower(), decimal.Decimal(1937.55))

  def testVerticalUpdateValuesNoMatchingOptionFound(self):
    """Tests that the profit loss calculation is unchanged if no option is available to update."""
    initialProfitLoss = self.__shortPutVertical.calcProfitLoss()
    tickData = []
    # Changed the putToBuy strike price from 325 to 327 to prevent a match.
    putToBuy = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                       strikePrice=decimal.Decimal(327), delta=-0.046858, vega=0.072881, theta=-0.066132,
                       gamma=0.004438, dateTime=datetime.datetime.strptime('01/03/1990', "%m/%d/%Y"),
                       expirationDateTime=datetime.datetime.strptime('01/19/1990', "%m/%d/%Y"),
                       bidPrice=decimal.Decimal(0.375), askPrice=decimal.Decimal(0.5),
                       tradePrice=decimal.Decimal(0.4375), settlementPrice=decimal.Decimal(0.4375))
    tickData.append(putToBuy)
    putToSell = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(358.76),
                        strikePrice=decimal.Decimal(345), delta=-0.15608, vega=0.178138, theta=-0.105865,
                        gamma=0.015931, dateTime=datetime.datetime.strptime('01/03/1990', "%m/%d/%Y"),
                        expirationDateTime=datetime.datetime.strptime('01/19/1990', "%m/%d/%Y"),
                        bidPrice=decimal.Decimal(1.125), askPrice=decimal.Decimal(1.375),
                        tradePrice=decimal.Decimal(1.25), settlementPrice=decimal.Decimal(1.25))
    tickData.append(putToSell)
    self.__shortPutVertical.updateValues(tickData)

    # The profit / loss should be the same since the option wasn't updated.
    self.assertAlmostEqual(self.__shortPutVertical.calcProfitLoss(), initialProfitLoss)

  def testVerticalGetNumberOfDaysLeft(self):
    """Tests that we calculate the number of days between two date / times correctly."""
    self.assertEqual(self.__shortPutVertical.getNumberOfDaysLeft(), 17)

  def testVerticalGetCommissionsAndFeesOpen(self):
    """Tests that the commissions and fees are calculated correctly on trade open."""
    indexOptionOpen = self.pricingSourceConfig['stock_options']['index_option']['open']
    putToSellMidPrice = self.__putToSell.settlementPrice
    secFees = indexOptionOpen['sec_fee_per_contract_wo_trade_price'] * float(putToSellMidPrice)
    self.assertAlmostEqual(self.__shortPutVertical.getCommissionsAndFees('open', self.pricingSource,
                                                                         self.pricingSourceConfig),
                           decimal.Decimal(2*self.__shortPutVertical.getNumContracts()*(
                             indexOptionOpen['commission_per_contract'] + indexOptionOpen['clearing_fee_per_contract'] +
                             indexOptionOpen['orf_fee_per_contract'] +
                             indexOptionOpen['proprietary_index_fee_per_contract']) +
                           self.__shortPutVertical.getNumContracts()*secFees))

  def testVerticalGetCommissionsAndFeesClose(self):
    """Tests that the commissions and fees are calculated correctly on trade close."""
    indexOptionClose = self.pricingSourceConfig['stock_options']['index_option']['close']
    putToBuyMidPrice = self.__putToBuy.settlementPrice
    secFees = indexOptionClose['sec_fee_per_contract_wo_trade_price'] * float(putToBuyMidPrice)
    self.assertAlmostEqual(self.__shortPutVertical.getCommissionsAndFees('close', self.pricingSource,
                                                                         self.pricingSourceConfig),
                           decimal.Decimal(2 * self.__shortPutVertical.getNumContracts() * (
                             indexOptionClose['commission_per_contract'] +
                             indexOptionClose['clearing_fee_per_contract'] + indexOptionClose['orf_fee_per_contract'] +
                             indexOptionClose['proprietary_index_fee_per_contract']) +
                                           self.__shortPutVertical.getNumContracts() * secFees))

  def testVerticalGetCommissionsAndFeesInvalidOpenOrCloseType(self):
    """Tests that an exception is raised if the type is not 'open' or 'close'."""
    with self.assertRaisesRegex(TypeError, 'Only open or close types can be provided to getCommissionsAndFees().'):
      self.__shortPutVertical.getCommissionsAndFees('invalid_type', self.pricingSource, self.pricingSourceConfig)

  def testFuturesOptionsVerticalGetCommissionsAndFeesOpen(self):
    """Tests that the commissions and fees are calculated correctly on trade open for futures options."""
    # Load the JSON config for calculating commissions and fees. Test with Tastyworks Futures as the brokerage.
    pricingSourceConfig = None
    pricingSource = 'tastyworks_futures'
    with open('./dataHandler/pricingConfig.json') as config:
      fullConfig = json.load(config)
      pricingSourceConfig = fullConfig[pricingSource]

    esOptionConfig = pricingSourceConfig['futures_options']['es_option']['open']
    self.assertAlmostEqual(self.__shortPutVertical.getCommissionsAndFees('open', pricingSource, pricingSourceConfig),
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
    self.assertAlmostEqual(self.__shortPutVertical.getCommissionsAndFees('close', pricingSource, pricingSourceConfig),
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

    with self.assertRaisesRegex(TypeError, 'Only open or close types can be provided to getCommissionsAndFees().'):
      self.__shortPutVertical.getCommissionsAndFees('invalid_type', pricingSource, pricingSourceConfig)

if __name__ == '__main__':
    unittest.main()