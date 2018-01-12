import unittest
import strangle
from base import put
from base import call

class TestStrangle(unittest.TestCase):
    def testStrangleBuyingPower(self):
        """Create strangle with necessary params and test buying power calculation
           Params for creating object:
           orderQuantity:  number of strangles
           callOpt:  call option
           putOpt:  put option
           """

        daysBeforeClosing = 5
        orderQuantity = 1

        # Create put and call options
        # Create PUT option
        putOpt = put.Put('SPX', 2675, 0.15, 35, underlyingPrice=2767.56, bidPrice=7.60, askPrice=7.60)
        # Create CALL option
        callOpt = call.Call('SPX', 2850, -0.11, 35, underlyingPrice=2767.56, bidPrice=3.05, askPrice=3.05)

        # Create Strangle
        strangleObj = strangle.Strangle(orderQuantity, callOpt, putOpt, daysBeforeClosing)

        # Check buying power calc
        buyingPower = strangleObj.getBuyingPower()
        self.assertAlmostEqual(buyingPower, 48172.20, 2)

if __name__ == '__main__':
    unittest.main()
