import unittest
from dataHandler import csvData
import tickEvent

class TestTickEvent(unittest.TestCase):
    """
    To test the tick event creation, we will test two things:
    1)  Create a simple empty tick event to make sure creation works
    2)  Create an event which uses a row of CSV data 
    """

    #Used to set up the unittest class
    def setUp(self):

        # Create CsvData class object
        dataProvider = 'iVolatility'
        directory = '../sampleData'
        filename = 'aapl_sample_ivolatility.csv'

        csvObj = csvData.CsvData(directory, filename, dataProvider)
        #Grab a row of data from the csv
        self.data = csvObj.getNextTick()

    def testCreateTickEvent(self):

        #Create tick event
        tickObj = tickEvent.TickEvent()

        #Check that the data reference attribute is set to none
        self.assertEqual(tickObj.getData(), None)

    def testCreateTickCSVEvent(self):

        tickObj = tickEvent.TickEvent()

        #Create an event and pass in the row of data
        tickObj.createEvent(self.data)

        #Get data from the first row of CSV
        data = tickObj.getData()

        #Check the underlying price
        self.assertTrue(data.getUnderlyingPrice(), 94.48)

if __name__ == '__main__':
    unittest.main()
