import unittest
from optionPrimitives import optionPrimitive
from optionPrimitives import strangle
from base import put
from base import call
import datetime
import decimal

class TestStrangle(unittest.TestCase):

  def setUp(self):
    orderQuantity = 1
    self.contractMultiplier = 100
    putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                     strikePrice=decimal.Decimal(2690), delta=0.15, vega=0.04, theta=-0.07, gamma=0.11,
                     dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                     expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                     bidPrice=decimal.Decimal(7.45), askPrice=decimal.Decimal(7.50), tradePrice=decimal.Decimal(7.475),
                     settlementPrice=decimal.Decimal(7.475))
    callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                        strikePrice=decimal.Decimal(2855), delta=-0.16, vega=0.05, theta=-0.06, gamma=0.12,
                        dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                        expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                        bidPrice=decimal.Decimal(5.20), askPrice=decimal.Decimal(5.40),
                        tradePrice=decimal.Decimal(5.30), settlementPrice=decimal.Decimal(5.30))
    self.__strangleObj = strangle.Strangle(orderQuantity=orderQuantity, contractMultiplier=self.contractMultiplier,
                                           callOpt=callOpt, putOpt=putOpt,
                                           buyOrSell=optionPrimitive.TransactionType.SELL)
    # The parameters below are used to update the prices of the initial strangle above.
    self.__tickData = []
    putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2790.0), strikePrice=decimal.Decimal(2690),
                     delta=0.13, vega=0.03, theta=-0.06, gamma=0.12,
                     dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                     expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                     bidPrice=decimal.Decimal(7.25), askPrice=decimal.Decimal(7.350),
                     settlementPrice=decimal.Decimal(7.30))
    self.__tickData.append(putOpt)
    callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2790.0),
                        strikePrice=decimal.Decimal(2855), delta=-0.20, vega=0.06, theta=-0.07, gamma=0.14,
                        dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                        expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                        bidPrice=decimal.Decimal(5.60), askPrice=decimal.Decimal(5.80),
                        settlementPrice=decimal.Decimal(5.70))
    self.__tickData.append(callOpt)

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
    putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=2786.24, strikePrice=2690, delta=None,
                     dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                     expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"), bidPrice=7.45,
                     askPrice=7.50, tradePrice=7.475, settlementPrice=7.475)
    callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=2786.24, strikePrice=2855, delta=-0.16,
                        dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                        expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"), bidPrice=5.20,
                        askPrice=5.40, tradePrice=5.30, settlementPrice=5.30)
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
    putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=2786.24, strikePrice=2690, delta=0.15, vega=None,
                     dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                     expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"), bidPrice=7.45,
                     askPrice=7.50, tradePrice=7.475, settlementPrice=7.475)
    callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=2786.24, strikePrice=2855, delta=-0.16, vega=0.05,
                        dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                        expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"), bidPrice=5.20,
                        askPrice=5.40, tradePrice=5.30, settlementPrice=5.30)
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
    putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=2786.24, strikePrice=2690, delta=0.15, vega=None,
                     theta=None, dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                     expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"), bidPrice=7.45,
                     askPrice=7.50, tradePrice=7.475, settlementPrice=7.475)
    callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=2786.24, strikePrice=2855, delta=-0.16, vega=0.05,
                        theta=-0.06, dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                        expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"), bidPrice=5.20,
                        askPrice=5.40, tradePrice=5.30, settlementPrice=5.30)
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
    putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=2786.24, strikePrice=2690, delta=0.15, vega=None,
                     theta=None, gamma=None, dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                     expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"), bidPrice=7.45,
                     askPrice=7.50, tradePrice=7.475, settlementPrice=7.475)
    callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=2786.24, strikePrice=2855, delta=-0.16, vega=0.05,
                        theta=-0.06, gamma=0.12, dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                        expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"), bidPrice=5.20,
                        askPrice=5.40, tradePrice=5.30, settlementPrice=5.30)
    strangleObj = strangle.Strangle(orderQuantity=1, contractMultiplier=self.contractMultiplier, callOpt=callOpt,
                                    putOpt=putOpt, buyOrSell=optionPrimitive.TransactionType.SELL)
    self.assertIsNone(strangleObj.getGamma())

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
                     bidPrice=decimal.Decimal(7.45), askPrice=decimal.Decimal(7.50), tradePrice=decimal.Decimal(7.475),
                     settlementPrice=decimal.Decimal(7.475))
    callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                        strikePrice=decimal.Decimal(2855),
                        dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                        expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                        bidPrice=decimal.Decimal(5.20), askPrice=decimal.Decimal(5.40),
                        tradePrice=decimal.Decimal(5.30), settlementPrice=decimal.Decimal(5.30))
    strangleObj = strangle.Strangle(orderQuantity=1, contractMultiplier=self.contractMultiplier, callOpt=callOpt,
                                    putOpt=putOpt, buyOrSell=optionPrimitive.TransactionType.BUY)
    # The parameters below are used to update the prices of the initial strangle above.
    tickData = []
    putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2790.0),
                     strikePrice=decimal.Decimal(2690),
                     dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                     expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                     bidPrice=decimal.Decimal(7.25), askPrice=decimal.Decimal(7.350),
                     settlementPrice=decimal.Decimal(7.30))
    tickData.append(putOpt)
    callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2790.0),
                        strikePrice=decimal.Decimal(2855),
                        dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                        expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                        bidPrice=decimal.Decimal(5.60), askPrice=decimal.Decimal(5.80),
                        settlementPrice=decimal.Decimal(5.70))
    tickData.append(callOpt)
    strangleObj.updateValues(tickData)
    self.assertAlmostEqual(strangleObj.calcProfitLoss(), decimal.Decimal(22.5))

  def testStrangeCalcProfitLossPercentage(self):
    """Tests that the profit / loss percentage is calculated correctly."""
    self.__strangleObj.updateValues(self.__tickData)
    self.assertAlmostEqual(self.__strangleObj.calcProfitLossPercentage(), decimal.Decimal(-1.76125244618395))

  def testStrangleBuyingPower25PercentRule(self):
    # Tests the buying power calculation for the 25% rule.
    buyingPower = self.__strangleObj.getBuyingPower()
    self.assertAlmostEqual(buyingPower, decimal.Decimal(63309.99999999997))

  def testStrangleBuyingPower15PercentRule(self):
    # Tests the buying power calculation for the 15% rule.
    putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                     strikePrice=decimal.Decimal(2500), delta=0.01,
                     dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                     expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                     bidPrice=decimal.Decimal(1.45), askPrice=decimal.Decimal(1.50), tradePrice=decimal.Decimal(1.475),
                     settlementPrice=decimal.Decimal(1.475))
    callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                        strikePrice=decimal.Decimal(3200), delta=-0.01,
                        dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                        expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                        bidPrice=decimal.Decimal(1.20), askPrice=decimal.Decimal(1.40),
                        tradePrice=decimal.Decimal(1.30), settlementPrice=decimal.Decimal(1.30))
    strangleObj = strangle.Strangle(orderQuantity=1, contractMultiplier=self.contractMultiplier, callOpt=callOpt,
                                    putOpt=putOpt, buyOrSell=optionPrimitive.TransactionType.SELL)
    buyingPower = strangleObj.getBuyingPower()
    self.assertAlmostEqual(buyingPower, decimal.Decimal(48130.0))

  def testStrangleUpdateValuesNoMatchingOption(self):
    """Tests that the profit loss calculation is unchanged if no option is available to update."""
    putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                     strikePrice=decimal.Decimal(2690),
                     dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                     expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                     bidPrice=decimal.Decimal(7.45), askPrice=decimal.Decimal(7.50), tradePrice=decimal.Decimal(7.475),
                     settlementPrice=decimal.Decimal(7.475))
    callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2786.24),
                        strikePrice=decimal.Decimal(2855),
                        dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                        expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                        bidPrice=decimal.Decimal(5.20), askPrice=decimal.Decimal(5.40),
                        tradePrice=decimal.Decimal(5.30), settlementPrice=decimal.Decimal(5.30))
    strangleObj = strangle.Strangle(orderQuantity=1, contractMultiplier=self.contractMultiplier, callOpt=callOpt,
                                    putOpt=putOpt, buyOrSell=optionPrimitive.TransactionType.BUY)
    initialProfitLoss = strangleObj.calcProfitLoss()

    tickData = []
    # Changed the PUT strike price from 2690 to 2790 to prevent a match.
    putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2790.0), strikePrice=decimal.Decimal(2790),
                     dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                     expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                     bidPrice=decimal.Decimal(7.25), askPrice=decimal.Decimal(7.350),
                     settlementPrice=decimal.Decimal(7.30))
    tickData.append(putOpt)
    callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=decimal.Decimal(2790.0),
                        strikePrice=decimal.Decimal(2855),
                        dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                        expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"),
                        bidPrice=decimal.Decimal(5.60), askPrice=decimal.Decimal(5.80),
                        settlementPrice=decimal.Decimal(5.70))
    tickData.append(callOpt)
    strangleObj.updateValues(tickData)

    # The profit / loss should be the same since the option wasn't updated.
    self.assertAlmostEqual(strangleObj.calcProfitLoss(), initialProfitLoss)

  def testStrangeGetNumberOfDaysLeft(self):
    """Tests that we calculate the number of days between two date / times correctly."""
    putOpt = put.Put(underlyingTicker='SPX', underlyingPrice=2786.24, strikePrice=2690, delta=0.15, vega=None,
                     theta=None, gamma=None, dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                     expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"), bidPrice=7.45,
                     askPrice=7.50, tradePrice=7.475, settlementPrice=decimal.Decimal(7.475))
    callOpt = call.Call(underlyingTicker='SPX', underlyingPrice=2786.24, strikePrice=2855, delta=-0.16, vega=0.05,
                        theta=-0.06, gamma=0.12, dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                        expirationDateTime=datetime.datetime.strptime('01/20/2021', "%m/%d/%Y"), bidPrice=5.20,
                        askPrice=5.40, tradePrice=5.30, settlementPrice=decimal.Decimal(5.30))
    strangleObj = strangle.Strangle(orderQuantity=1, contractMultiplier=self.contractMultiplier, callOpt=callOpt,
                                    putOpt=putOpt, buyOrSell=optionPrimitive.TransactionType.SELL)
    self.assertEqual(strangleObj.getNumberOfDaysLeft(), 19)

if __name__ == '__main__':
    unittest.main()
