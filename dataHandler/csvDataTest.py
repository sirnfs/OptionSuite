import unittest
import csvData

class TestCSVHandler(unittest.TestCase):

    #Used to set up the unittest class
    def setUp(self):
        # Test CSV Handler Initialization

        # Create CsvData class object
        self.csvObj = csvData.CsvData('./sampleData')

    def testCSVHandlerInit(self):

        #Check that CSV directory is set
        self.assertEqual(self.csvObj.getCSVDir(), './sampleData')

    def testCSVLoad(self):

        #Load sample CSV file from sampleData directory into
        #pandas dataframe
        dataProvider = 'iVolatility'

        self.csvObj.openDataSource('aapl_sample_ivolatility.csv', dataProvider)

        data = self.csvObj.getNextTick()
        self.assertEqual(data.getUnderlyingPrice(), 94.48)

if __name__ == '__main__':
    unittest.main()

