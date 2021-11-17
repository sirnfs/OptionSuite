import datetime
import unittest
from optionPrimitives import optionPrimitive
from strategyManager import strategy

class TestStrategyClass(unittest.TestCase):

  def testStrategyClassCreation(self):
    """Tests than an exception is raised when class is instantiated."""
    with self.assertRaisesRegex(TypeError, 'Cannot instantiate class.'):
      strategy.Strategy(startDateTime=datetime.datetime.now(), buyOrSell=optionPrimitive.TransactionType.SELL,
                        underlyingTicker='SPY', orderQuantity=1)

if __name__ == '__main__':
  unittest.main()
