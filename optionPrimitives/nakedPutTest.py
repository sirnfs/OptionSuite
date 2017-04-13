import unittest
import nakedPut

class TestNakedPutStrategy(unittest.TestCase):
    def testNakedPutCreation(self):
        """Create naked put object and perform tests
           Params for creating object:
           underlyingTicker -- stock ticker symbol
           strikePrice - strike price of the PUT option
           longOrShort - indicates if we want to buy or sell a PUT
           delta - Greek value of PUT (negative or positive value between 0 - 1
           DTE - Days until expiration; TBD:  do we find the value closes to this in the historical data?
           numContracts -- number of PUT contracts to buy
           """

        #Create NAKED PUT strategy
        curStrategy = nakedPut.NakedPut('SPY', 200, 'Short', 0.16, 45, 2)

        self.assertEqual(curStrategy.getNumContracts(), 2)
        primitiveElement = curStrategy.getPrimitiveElements()
        self.assertEqual(primitiveElement[0].getUnderlyingPrice(), None)

if __name__ == '__main__':
    unittest.main()
