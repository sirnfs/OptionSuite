import datetime
import decimal
import unittest
from base import call
from base import option


class TestCallOption(unittest.TestCase):
    def testCallOptionCreation(self):
        """Tests that a CALL option is created successfully."""
        callOption = call.Call(underlyingTicker='SPY', strikePrice=250, expirationDateTime=datetime.datetime.strptime(
            '01/01/2050',"%m/%d/%Y"))
        # Trivial checks on the callOption object.
        self.assertEqual(callOption.strikePrice, 250)
        self.assertEqual(callOption.optionType, option.OptionTypes.CALL)


if __name__ == '__main__':
    unittest.main()
