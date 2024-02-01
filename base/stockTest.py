import unittest
import decimal
from base import stock

class TestStockClass(unittest.TestCase):
  def testStockClassCreation(self):
    # Test Stock class creation and getter methods
    stockObj = stock.Stock(underlyingTicker='SPY', underlyingPrice=decimal.Decimal(250))
    # Test that the underlying ticker, direction, and underlying price are populated correctly.
    self.assertEqual(stockObj.underlyingTicker, 'SPY')
    self.assertEqual(stockObj.underlyingPrice, decimal.Decimal(250))

if __name__ == '__main__':
    unittest.main()

