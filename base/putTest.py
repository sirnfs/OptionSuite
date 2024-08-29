import datetime
import decimal
import unittest
from base import put


class TestPutOption(unittest.TestCase):
    def setUp(self):
        self._putOptionToTest = put.Put(underlyingTicker='SPY', strikePrice=decimal.Decimal(250),
                                        dateTime=datetime.datetime.strptime('01/01/2021',
                                                                            "%m/%d/%Y"),
                                        expirationDateTime=datetime.datetime.strptime('01/01/2050',
                                                                                      "%m/%d/%Y"),
                                        tradePrice=decimal.Decimal(3.00), settlementPrice=decimal.Decimal(1.25))

    def testCalcOptionPriceDiff(self):
        """Tests that the difference between current price and trade price is calculated correctly."""
        expectedPriceDiff = self._putOptionToTest.tradePrice - self._putOptionToTest.settlementPrice
        self.assertEqual(self._putOptionToTest.calcOptionPriceDiff(), expectedPriceDiff)

    def testNumberDaysUntilExpiration(self):
        """Tests that the number of days to expiration is computed correctly."""
        expectedDays = self._putOptionToTest.expirationDateTime - self._putOptionToTest.dateTime
        self.assertEqual(self._putOptionToTest.getNumDaysLeft(), expectedDays.days)

    def testUpdateOptionSuccess(self):
        """Tests that option values are successfully updated with latest data."""
        updatedPut = put.Put(underlyingTicker='SPY', strikePrice=250, delta=0.3,
                             expirationDateTime=datetime.datetime.strptime('01/01/2050',
                                                                           "%m/%d/%Y"),
                             bidPrice=decimal.Decimal(0.50), askPrice=decimal.Decimal(0.75))
        self._putOptionToTest.updateOption(updatedPut)
        self.assertEqual(self._putOptionToTest.bidPrice, decimal.Decimal(0.50))
        self.assertEqual(self._putOptionToTest.askPrice, decimal.Decimal(0.75))

    def testUpdateOptionInvalidOptionStrikePrice(self):
        """Tests that error is raised if we update an option with different parameters (wrong strike price)."""
        updatedPut = put.Put(underlyingTicker='SPY', strikePrice=255,
                             expirationDateTime=datetime.datetime.strptime('01/01/2050',
                                                                           "%m/%d/%Y"))
        with self.assertRaisesRegex(ValueError,
                                    ('Cannot update option; this option appears to be from a different option chain.')):
            self._putOptionToTest.updateOption(updatedPut)


if __name__ == '__main__':
    unittest.main()
