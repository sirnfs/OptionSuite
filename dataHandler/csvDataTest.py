import unittest
import csvData
import Queue as queue

class TestCSVHandler(unittest.TestCase):

    def testCSVLoad(self):

        #Load sample CSV file from sampleData directory into
        #pandas dataframe
        dataProvider = 'iVolatility'
        directory = './sampleData'
        filename = 'aapl_sample_ivolatility.csv'
        eventQueue = queue.Queue()

        csvObj = csvData.CsvData(directory, filename, dataProvider, eventQueue)

        #Get row of CSV data
        csvObj.getNextTick()
        event = eventQueue.get()
        dataObj = event.getData()
        self.assertEqual(dataObj.getUnderlyingPrice(), 94.48)

if __name__ == '__main__':
    unittest.main()

