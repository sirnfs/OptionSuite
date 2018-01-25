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
        putOpt = put.Put('SPX', 2690, 0.15, 34, underlyingPrice=2786.24, bidPrice=7.45, askPrice=7.45)
        # Create CALL option
        callOpt = call.Call('SPX', 2855, -0.15, 34, underlyingPrice=2786.24, bidPrice=5.20, askPrice=5.20)

        # Create Strangle
        strangleObj = strangle.Strangle(orderQuantity, callOpt, putOpt, daysBeforeClosing)

        # Check buying power calc
        buyingPower = strangleObj.getBuyingPower()
        self.assertAlmostEqual(buyingPower, 64045.0, 2)

if __name__ == '__main__':
    unittest.main()
