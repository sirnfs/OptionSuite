import unittest
import strangle
from base import put
from base import call
import datetime
import pytz

class TestStrangle(unittest.TestCase):

    def setUp(self):
        """Create strangle with necessary params and test buying power calculation.
        Params for creating object:
        daysBeforeClosing:  Strangle must be closed if there are <= daysBeforeClosing to expiration.
        profitTargetPercent: Minimum percent profit we want in order to close strangle.
        orderQuantity:  Number of strangles.
        callOpt:  Call option
        putOpt:  Put option
        """

        daysBeforeClosing = 5
        orderQuantity = 1
        profitTargetPercent = 0.5

        # Create put and call options.
        putOpt = put.Put('SPX', 2690, 0.15, 34, underlyingPrice=2786.24, bidPrice=7.45, askPrice=7.45,
                         optionSymbol="01", tradePrice=7.45)
        callOpt = call.Call('SPX', 2855, -0.15, 34, underlyingPrice=2786.24, bidPrice=5.20, askPrice=5.20,
                            optionSymbol="02", tradePrice=5.20)

        # Create Strangle.
        self.strangleObj = strangle.Strangle(orderQuantity, callOpt, putOpt, "SELL", daysBeforeClosing,
                                              profitTargetPercent)

    def testStrangleBuyingPower(self):

        # Check buying power calculation.
        buyingPower = self.strangleObj.getBuyingPower()
        self.assertAlmostEqual(buyingPower, 64045.0, 2)

    def testStrangleUpdateValues(self):
        """Test that the option values are updated correctly by starting with a strangle and then receiving new
        option prices for the puts and calls.
        """

        # Create a list with two options matching the strangleObj except with different option prices.
        tickData = []
        putOpt = put.Put('SPX', 2690, 0.15, 34, underlyingPrice=2786.24, bidPrice=7.25, askPrice=7.25,
                         optionSymbol="01")
        tickData.append(putOpt)
        callOpt = call.Call('SPX', 2855, -0.15, 34, underlyingPrice=2786.24, bidPrice=5.00, askPrice=5.00,
                            optionSymbol="02")
        tickData.append(callOpt)

        self.strangleObj.updateValues(tickData)

        # Check that the bidPrice of the put and call options inside strangleObj have been updated.
        __putOpt = self.strangleObj.getPutOption()
        __callOpt = self.strangleObj.getCallOption()
        self.assertAlmostEqual(__putOpt.getBidPrice(), 7.25)
        self.assertAlmostEqual(__callOpt.getBidPrice(), 5.00)

    def testStrangleManagePositionProfitTargetPercent(self):
        """Test that strangle is set to be deleted from the portfolio if the option prices are such that the
        desired profit target threshold has been reached.
        """

        # Create put and call options.
        tickData = []
        putOpt = put.Put('SPX', 2690, 0.15, 34, underlyingPrice=2786.24, bidPrice=3.00, askPrice=3.00,
                         optionSymbol="01")
        tickData.append(putOpt)
        callOpt = call.Call('SPX', 2855, -0.15, 34, underlyingPrice=2786.24, bidPrice=2.00, askPrice=2.00,
                        optionSymbol = "02")
        tickData.append(callOpt)

        # Update strangle with new values.
        self.strangleObj.updateValues(tickData)

        # Check if managePosition() returns true since the combined put and call prices reflect more than a 50% profit.
        self.assertTrue(self.strangleObj.managePosition())

    def testStrangleManageDaysBeforeClosing(self):
        """Test that the strangle is set to be deleted from the portfolio if the number of days until expiration is
        less than the daysBeforeClosing threshold.
        """
        # Create put and call options.
        tickData = []

        # Set up date / time formats.
        local = pytz.timezone('US/Eastern')

        # Convert time zone of data 'US/Eastern' to UTC time.
        expDate = datetime.datetime.strptime("02/05/18", "%m/%d/%y")
        expDate = local.localize(expDate, is_dst=None)
        expDate = expDate.astimezone(pytz.utc)

        # Convert time zone of data 'US/Eastern' to UTC time.
        curDate = datetime.datetime.strptime("02/02/18", "%m/%d/%y")
        curDate = local.localize(curDate, is_dst=None)
        curDate = curDate.astimezone(pytz.utc)

        putOpt = put.Put('SPX', 2690, 0.15, expDate, underlyingPrice=2786.24, bidPrice=3.00, askPrice=3.00,
                         tradePrice=3.00, optionSymbol="01", dateTime=curDate)
        tickData.append(putOpt)
        callOpt = call.Call('SPX', 2855, -0.15, expDate, underlyingPrice=2786.24, bidPrice=2.00, askPrice=2.00,
                            tradePrice=2.00, optionSymbol="02", dateTime=curDate)
        tickData.append(callOpt)

        daysBeforeClosing = 5
        orderQuantity = 1
        strangleObj = strangle.Strangle(orderQuantity, callOpt, putOpt, "SELL", daysBeforeClosing)

        # Check if managePosition() returns true since the current dateTime and DTE are less than daysBeforeClosing = 5.
        self.assertTrue(strangleObj.managePosition())

    def testStrangleCalcProfitLossPercentage(self):

        # Set up date / time formats.
        local = pytz.timezone('US/Eastern')

        # Convert time zone of data 'US/Eastern' to UTC time.
        expDate = datetime.datetime.strptime("02/05/18", "%m/%d/%y")
        expDate = local.localize(expDate, is_dst=None)
        expDate = expDate.astimezone(pytz.utc)

        # Convert time zone of data 'US/Eastern' to UTC time.
        curDate = datetime.datetime.strptime("02/02/18", "%m/%d/%y")
        curDate = local.localize(curDate, is_dst=None)
        curDate = curDate.astimezone(pytz.utc)

        # Test the case where we sell a strangle and have a loss.
        putOpt = put.Put('SPX', 2690, 0.15, expDate, underlyingPrice=2786.24, bidPrice=6.00, askPrice=6.00,
                         tradePrice=3.00, optionSymbol="01", dateTime=curDate)
        callOpt = call.Call('SPX', 2855, -0.15, expDate, underlyingPrice=2786.24, bidPrice=4.00, askPrice=4.00,
                            tradePrice=2.00, optionSymbol="02", dateTime=curDate)

        orderQuantity = 1
        strangleObj = strangle.Strangle(orderQuantity, callOpt, putOpt, "SELL")

        # Total credit = 5.00 or 500, and total loss is -300 + -200 = -500; (-500/500) * 100 = -100%
        profitLossPercentage = strangleObj.calcProfitLossPercentage()
        self.assertAlmostEqual(profitLossPercentage, -100)

        # Test the case where we sell a strangle and have a profit.
        putOpt = put.Put('SPX', 2690, 0.15, expDate, underlyingPrice=2786.24, bidPrice=1.50, askPrice=1.50,
                         tradePrice=3.00, optionSymbol="01", dateTime=curDate)
        callOpt = call.Call('SPX', 2855, -0.15, expDate, underlyingPrice=2786.24, bidPrice=1.00, askPrice=1.00,
                            tradePrice=2.00, optionSymbol="02", dateTime=curDate)

        strangleObj = strangle.Strangle(orderQuantity, callOpt, putOpt, "SELL")

        # Total credit = 5.00 or 500, and total profit is 150 + 100 = 250; 250/500 = 0.5 * 100 = 50%
        profitLossPercentage = strangleObj.calcProfitLossPercentage()
        self.assertAlmostEqual(profitLossPercentage, 50)

        # Test the case where we buy a strangle and have a loss.
        putOpt = put.Put('SPX', 2690, 0.15, expDate, underlyingPrice=2786.24, bidPrice=1.50, askPrice=1.50,
                         tradePrice=3.00, optionSymbol="01", dateTime=curDate)
        callOpt = call.Call('SPX', 2855, -0.15, expDate, underlyingPrice=2786.24, bidPrice=1.00, askPrice=1.00,
                            tradePrice=2.00, optionSymbol="02", dateTime=curDate)

        strangleObj = strangle.Strangle(orderQuantity, callOpt, putOpt, "BUY")

        # Total debit = 5.00 or 500, and total loss is -150 + -100 = -250 / 500 = -0.5* 100 = -50%
        profitLossPercentage = strangleObj.calcProfitLossPercentage()
        self.assertAlmostEqual(profitLossPercentage, -50)

        # Test the case where we buy a strangle and have a profit.
        putOpt = put.Put('SPX', 2690, 0.15, expDate, underlyingPrice=2786.24, bidPrice=6.00, askPrice=6.00,
                         tradePrice=3.00, optionSymbol="01", dateTime=curDate)
        callOpt = call.Call('SPX', 2855, -0.15, expDate, underlyingPrice=2786.24, bidPrice=4.00, askPrice=4.00,
                            tradePrice=2.00, optionSymbol="02", dateTime=curDate)

        strangleObj = strangle.Strangle(orderQuantity, callOpt, putOpt, "BUY")

        # Total debit = 5.00 or 500, and total profit is 300 + 200 = 500 / 500 = 1 * 100 = 100%
        profitLossPercentage = strangleObj.calcProfitLossPercentage()
        self.assertAlmostEqual(profitLossPercentage, 100)

if __name__ == '__main__':
    unittest.main()
