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
        self.csvObj = csvData.CsvData('../sampleData')
        df = self.csvObj.openDataSource('aapl_sample_ivolatility.csv')
        #Grab a single row from the dataframe, df
        self.data = df.ix[0]

    def testCreateTickEvent(self):

        #Create tick event
        tickObj = tickEvent.TickEvent()

        #Check that the data reference attribute is set to none
        self.assertEqual(tickObj.getDataRef(), None)

if __name__ == '__main__':
    unittest.main()

