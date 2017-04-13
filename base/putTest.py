import unittest
import put

class TestCallOption(unittest.TestCase):
    def testCallOptionCreation(self):

        #Create PUT option
        callOption = put.Put('SPY', 250, 'Long', 0.3, 45)

        self.assertEqual(callOption.getStrikePrice(), 250)
        self.assertEqual(callOption.getUnderlyingTicker(), 'SPY')

if __name__ == '__main__':
    unittest.main()
