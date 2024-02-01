import datetime
import decimal
import unittest
from base import call
from base import option

class TestCallOption(unittest.TestCase):
  def testCallOptionCreation(self):
    """Tests that a CALL option is created successfully."""
    callOption = call.Call(underlyingTicker='SPY', strikePrice=250, delta=0.3,
                           dateTime=datetime.datetime.strptime('01/01/2021', "%m/%d/%Y"),
                           expirationDateTime=datetime.datetime.strptime('01/01/2050', "%m/%d/%Y"),
                           bidPrice=decimal.Decimal(1.50), askPrice=decimal.Decimal(1.00),
                           tradePrice=decimal.Decimal(3.00), settlementPrice=decimal.Decimal(3.00))
    self.assertEqual(callOption.strikePrice, 250)
    self.assertEqual(callOption.optionType, option.OptionTypes.CALL)

if __name__ == '__main__':
    unittest.main()