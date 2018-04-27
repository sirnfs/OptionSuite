import unittest
import put

class TestPutOption(unittest.TestCase):
    def testPutOptionCreation(self):

        # Create PUT option
        putOption = put.Put('SPY', 250, 0.3, 45)
        # Test that the strike price and underlying ticker symbol are set.
        self.assertEqual(putOption.getStrikePrice(), 250)
        self.assertEqual(putOption.getUnderlyingTicker(), 'SPY')

if __name__ == '__main__':
    unittest.main()
