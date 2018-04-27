import unittest
import nakedPut

class TestNakedPutStrategy(unittest.TestCase):

    def setUp(self):
        """Create naked put object and perform tests.
           Params for creating object:
           underlyingTicker -- stock ticker symbol
           strikePrice - strike price of the PUT option
           longOrShort - indicates if we want to buy or sell a PUT
           delta - Greek value of PUT (negative or positive value between 0 - 1
           DTE - Days until expiration; TBD:  do we find the value closes to this in the historical data?
           numContracts -- number of PUT contracts to buy

           Optional:
           underlyingPrice -- current price of stock
           bidPrice -- price at which option can be sold
           askPrice -- price at which option can be bought
           """

        # Create Naked Put.
        self.nakedPutObj = nakedPut.NakedPut('SPY', 200, 'Short', 0.16, 45, 2, underlyingPrice=210, bidPrice=0.5,
                                             askPrice=0.5)

    def testNakedPutCreation(self):

        self.assertEqual(self.nakedPutObj.getNumContracts(), 2)
        primitiveElement = self.nakedPutObj.getPrimitiveElements()
        self.assertEqual(primitiveElement[0].getUnderlyingPrice(), 210)

    def testNakedPutBuyingPower(self):

        buyingPower = self.nakedPutObj.getBuyingPower()
        self.assertAlmostEqual(buyingPower, 6500, 2)

if __name__ == '__main__':
    unittest.main()
