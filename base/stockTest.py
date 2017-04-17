import unittest
import stock

class TestStockClass(unittest.TestCase):
    def testStockClassCreation(self):

        #Test Stock class creation and getter methods
        classObj = stock.Stock('SPY', 'Long', 250)

        self.assertEqual(classObj.getUnderlyingTicker(), 'SPY')
        self.assertEqual(classObj.getLongOrShort(), 'Long')
        self.assertEqual(classObj.getUnderlyingPrice(), 250)

if __name__ == '__main__':
    unittest.main()

