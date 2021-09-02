import datetime
import decimal
import unittest
from base import put

class TestPutOption(unittest.TestCase):
  def setUp(self):
    self._putOptionToTest = put.Put(underlyingTicker='SPY', strikePrice=decimal.Decimal(250), delta=0.3,
                                    dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                                    expirationDateTime=datetime.datetime.strptime('01/01/2050', "%m/%d/%Y"),
                                    bidPrice=decimal.Decimal(1.50), askPrice=decimal.Decimal(1.00),
                                    tradePrice=decimal.Decimal(3.00))

  def testCalcOptionPriceDiff(self):
    """Tests that the difference between current price and trade price is calculated correctly."""
    expectedPriceDiff = 175
    self.assertEqual(self._putOptionToTest.calcOptionPriceDiff(), expectedPriceDiff)

  def testNumberDaysUntilExpiration(self):
    """Tests that the number of days to expiration is computed correctly."""
    expectedDays = 10592
    self.assertEqual(self._putOptionToTest.getNumDaysLeft(), expectedDays)

  def testUpdateOptionSuccess(self):
    """Tests that option values are successfully updated with latest data."""
    updatedPut = put.Put(underlyingTicker='SPY', strikePrice=250, delta=0.3,
                         dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/01/2050', "%m/%d/%Y"), bidPrice=0.50,
                         askPrice=0.75, tradePrice=3.00)
    self._putOptionToTest.updateOption(updatedPut)
    self.assertEqual(self._putOptionToTest.bidPrice, 0.50)
    self.assertEqual(self._putOptionToTest.askPrice, 0.75)

  def testUpdateOptionInvalidOptionStrikePrice(self):
    """Tests that error is raised if we update an option with different parameters (wrong strike price)."""
    updatedPut = put.Put(underlyingTicker='SPY', strikePrice=255, delta=0.3,
                         dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                         expirationDateTime=datetime.datetime.strptime('01/01/2050', "%m/%d/%Y"), bidPrice=0.50,
                         askPrice=0.75, tradePrice=3.00)
    with self.assertRaisesRegex(ValueError, ('Cannot update option; this option appears to be from a different option '
      'chain.')):
      self._putOptionToTest.updateOption(updatedPut)

if __name__ == '__main__':
    unittest.main()
