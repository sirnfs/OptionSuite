import unittest
import csvData
import Queue as queue
import datetime

class TestCSVHandler(unittest.TestCase):

    # Used to set up the unittest class
    def setUp(self):
        # Create CsvData class object
        self.dataProvider = 'iVolatility'
        self.directory = './sampleData'
        self.filename = 'aapl_sample_ivolatility.csv'
        self.eventQueue = queue.Queue()
        self.csvObj = csvData.CsvData(self.directory, self.filename, self.dataProvider, self.eventQueue)

    def testGetOptionChain(self):
        #Get option chain for the first time/date from CSV
        self.csvObj.getOptionChain()

        #Get event from the queue
        event = self.eventQueue.get()
        data = event.getData()

        #Check that we got the right number of rows from the csv.
        self.assertEqual(len(data), 1822)

        #Get the first object of type put/call and do some basic checks
        firstOption = data[0]

        underlyingTicker = firstOption.getUnderlyingTicker()
        self.assertEqual(underlyingTicker, 'AAPL')

        optionType = firstOption.getOptionType()
        self.assertEqual(optionType, 'CALL')

        curDateTime = firstOption.getDateTime()
        self.assertEqual(curDateTime, datetime.datetime.strptime('8/7/14', "%m/%d/%y"))

        #Get option chain for the second date/time from CSV
        self.csvObj.getOptionChain()

        # Get event from the queue
        event = self.eventQueue.get()
        data = event.getData()

        # Get the first object of type put/call and do some basic checks
        firstOption = data[0]

        underlyingTicker = firstOption.getUnderlyingTicker()
        self.assertEqual(underlyingTicker, 'SPY')

        optionType = firstOption.getOptionType()
        self.assertEqual(optionType, 'CALL')

        curDateTime = firstOption.getDateTime()
        self.assertEqual(curDateTime, datetime.datetime.strptime('8/8/14', "%m/%d/%y"))

if __name__ == '__main__':
    unittest.main()

