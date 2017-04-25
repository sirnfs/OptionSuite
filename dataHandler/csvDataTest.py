import unittest

import csvData


class TestCSVHandler(unittest.TestCase):

    #Used to set up the unittest class
    def setUp(self):
        # Test CSV Handler Initialization

        # Create CsvData class object
        self.csvObj = csvData.CsvData('../sampleData')

    def testCSVHandlerInit(self):

        #Check that CSV directory is set
        self.assertEqual(self.csvObj.getCSVDir(), '../sampleData')

    #def testCSVLoad(self):

        #Load sample CSV file from sampleData directory into
        #pandas dataframe
        #dataProvider = 'iVolatility'
        #df = self.csvObj.openDataSource('aapl_sample_ivolatility.csv', dataProvider)

        #Check that the first element in 'ask' column is 40.450
        #self.assertEqual(df['ask'].iloc[0], 40.450)

if __name__ == '__main__':
    unittest.main()

