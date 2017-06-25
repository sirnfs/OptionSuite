import unittest
import csvData
import Queue as queue
import pandas as pd

class TestCSVHandler(unittest.TestCase):

    # Used to set up the unittest class
    def setUp(self):
        # Create CsvData class object
        self.dataProvider = 'iVolatility'
        self.directory = './sampleData'
        self.filename = 'aapl_sample_ivolatility.csv'
        self.eventQueue = queue.Queue()
        self.csvObj = csvData.CsvData(self.directory, self.filename, self.dataProvider, self.eventQueue)

    def testCSVLoad(self):

        #Load sample CSV file from sampleData directory into
        #pandas dataframe

        #Get row of CSV data
        self.csvObj.getNextTick()
        event = self.eventQueue.get()
        dataObj = event.getData()
        self.assertEqual(dataObj.getUnderlyingPrice(), 94.48)

    def testGetOptionChain(self):
        #Get the option chain for each time/date from CSV
        self.csvObj.getOptionChain()


if __name__ == '__main__':
    unittest.main()

