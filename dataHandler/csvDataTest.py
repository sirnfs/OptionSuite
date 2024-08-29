import unittest
import decimal
from dataHandler import csvData
import queue


class TestCSVHandler(unittest.TestCase):

    def setUp(self):
        # Create CsvData class object.
        self._dataProvider = 'iVolatility'
        self._dataProviderPath = 'dataHandler/dataProviders.json'
        self._csvPath = 'sampleData/aapl_sample_ivolatility.csv'
        self._eventQueue = queue.Queue()
        self._csvObj = csvData.CsvData(csvPath=self._csvPath, dataProviderPath=self._dataProviderPath,
                                       dataProvider=self._dataProvider, eventQueue=self._eventQueue)

    def testOpenDataSourceNoCSVFound(self):
        """Tests that an exception is raised when no CSV is found."""
        with self.assertRaisesRegex(OSError, 'Unable to open CSV at location: bad_path_name.'):
            csvData.CsvData(csvPath='bad_path_name', dataProviderPath=self._dataProviderPath,
                            dataProvider=self._dataProvider, eventQueue=self._eventQueue)

    def testOpenDataSourceNoDataProviderJSON(self):
        with self.assertRaisesRegex(
            ValueError, (
                'Failure when trying to open / load data from JSON file: %s.' % 'bad_path_name')):
            csvData.CsvData(csvPath=self._csvPath, dataProviderPath='bad_path_name',
                            dataProvider=self._dataProvider, eventQueue=self._eventQueue)

    def testOpenDataSourceInvalidDataProvider(self):
        """Tests that an exception is raised if the requested data provider isn't in the config file."""
        with self.assertRaisesRegex(ValueError, ('The requested data provider: unknown_data_provider was not found in '
                                                 'dataProviders.json')):
            csvData.CsvData(csvPath=self._csvPath, dataProviderPath=self._dataProviderPath,
                            dataProvider='unknown_data_provider', eventQueue=self._eventQueue)

    def testOpenDataSourceNumberColumnsNotSpecified(self):
        """Tests than an exception is raised if the number of columns field is not provided in dataProvider.json"""
        dataProviderPath = 'dataHandler/unitTestData/dataProvidersFakeNoColsSpecified.json'
        dataProvider = 'test_provider'
        with self.assertRaisesRegex(ValueError,
                                    'number_columns was not provided in dataProviders.json file.'):
            csvData.CsvData(csvPath=self._csvPath, dataProviderPath=dataProviderPath, dataProvider=dataProvider,
                            eventQueue=self._eventQueue)

    def testOpenDataSourceWrongNumberColumns(self):
        """Tests than an exception is raised if the wrong number of columns is specified in dataProvider.json"""
        dataProviderPath = 'dataHandler/unitTestData/dataProvidersFakeWrongNumColumns.json'
        dataProvider = 'test_provider'
        with self.assertRaisesRegex(
              ValueError, 'Number of columns in CSV and dataProviders.json do not match.'):
            csvData.CsvData(csvPath=self._csvPath, dataProviderPath=dataProviderPath, dataProvider=dataProvider,
                            eventQueue=self._eventQueue)

    def testGetOptionChain(self):
        """Tests that an option chain is successfully read from CSV file."""
        # The first and second calls to getNextTick should load one option chain into the queue and return True,
        # and the third call should return False
        self.assertTrue(self._csvObj.getNextTick())
        self.assertTrue(self._eventQueue.qsize(), 1)
        self.assertTrue(self._csvObj.getNextTick())
        self.assertTrue(self._eventQueue.qsize(), 2)
        self.assertFalse(self._csvObj.getNextTick())
        self.assertTrue(self._eventQueue.qsize(), 2)

        # Check number of option objects in the first and second queue positions.
        desiredNumObjects = 1822
        self.assertEqual(len(self._eventQueue.get().getData()), desiredNumObjects)
        self.assertEqual(len(self._eventQueue.get().getData()), desiredNumObjects)
        self.assertEqual(self._eventQueue.qsize(), 0)

    def testGetOptionChainBadColumnName(self):
        """Tests that an exception is raised if column name in the CSV doesn't match the one in dataProviders.json."""
        # Create CsvData class object.
        filename = 'sampleData/bad_column_name.csv'
        csvObj = csvData.CsvData(csvPath=filename, dataProviderPath=self._dataProviderPath,
                                 dataProvider=self._dataProvider, eventQueue=self._eventQueue)

        with self.assertRaisesRegex(TypeError, 'The dateColumnName was not found in the CSV'):
            csvObj.getNextTick()

    def testGetNextTick(self):
        """Tests that Put and Call objects are created successfully from a tick event."""
        # First row in the sample data is a call, and second row is a put.
        eventQueue = queue.Queue()
        csvObj = csvData.CsvData(csvPath=self._csvPath, dataProviderPath=self._dataProviderPath,
                                 dataProvider=self._dataProvider, eventQueue=eventQueue)
        csvObj.getNextTick()
        optionChainObjs = eventQueue.get().getData()
        desiredCallAskPrice = decimal.Decimal(40.45)
        desiredPutAskPrice = decimal.Decimal(0.01)
        desiredStrikePrice = 55
        desiredUnderlyingTicker = 'AAPL'
        self.assertEqual(optionChainObjs[0].underlyingTicker, desiredUnderlyingTicker)
        self.assertEqual(optionChainObjs[0].strikePrice, desiredStrikePrice)
        self.assertEqual(optionChainObjs[1].underlyingTicker, desiredUnderlyingTicker)
        self.assertEqual(optionChainObjs[1].strikePrice, desiredStrikePrice)
        self.assertAlmostEqual(optionChainObjs[0].askPrice, desiredCallAskPrice)
        self.assertAlmostEqual(optionChainObjs[1].askPrice, desiredPutAskPrice)

    def testGetTwoOptionChains(self):
        """Tests that we are able to read data from two different option chains (different dates)."""
        eventQueue = queue.Queue()
        csvObj = csvData.CsvData(csvPath=self._csvPath, dataProviderPath=self._dataProviderPath,
                                 dataProvider=self._dataProvider, eventQueue=eventQueue)
        lastElementIndex = 1821
        # Gets the first option chain from 8/7/2014. 1822 rows in CSV.
        csvObj.getNextTick()
        # Gets the second option chain 8/8/2014. 1822 rows in CSV.
        csvObj.getNextTick()
        optionChain1 = eventQueue.get().getData()
        optionChain2 = eventQueue.get().getData()
        self.assertEqual(optionChain1[0].dateTime, optionChain1[lastElementIndex].dateTime)
        self.assertEqual(optionChain2[0].dateTime, optionChain2[lastElementIndex].dateTime)

    def testColumnNotInCSVNotSupportedColumn(self):
        """Tests that an exception is raised if a column from dataProvider.json is not in the CSV."""
        dataProviderPath = 'dataHandler/unitTestData/dataProvidersFakeColumnNotInCSV.json'
        dataProvider = 'test_provider'
        csvObj = csvData.CsvData(csvPath=self._csvPath, dataProviderPath=dataProviderPath, dataProvider=dataProvider,
                                 eventQueue=self._eventQueue)
        with self.assertRaisesRegex(ValueError,
                                    'Column name dummy_value in dataProvider.json not found in CSV.'):
            csvObj.getNextTick()

    def testColumnNotInCSVNotSupportedDataSource(self):
        """Tests that an exception is raised if a column from dataProvider.json is not in the CSV."""
        dataProviderPath = 'dataHandler/unitTestData/dataProvidersFakeUnsupportedDataSource.json'
        dataProvider = 'test_provider'
        csvObj = csvData.CsvData(csvPath=self._csvPath, dataProviderPath=dataProviderPath,
                                 dataProvider=dataProvider,
                                 eventQueue=self._eventQueue)
        with self.assertRaisesRegex(TypeError,
                                    'data_source_type not supported.'):
            csvObj.getNextTick()

    def testCheckTradePriceIsCorrectForIndexOptions(self):
        """Tests that the trade and settlement price is correct for index options."""
        dataProvider = 'iVolatility'
        dataProviderPath = 'dataHandler/dataProviders.json'
        eventQueue = queue.Queue()
        csvObj = csvData.CsvData(csvPath=self._csvPath, dataProviderPath=dataProviderPath, dataProvider=dataProvider,
                                 eventQueue=eventQueue)
        csvObj.getNextTick()
        option = eventQueue.get().getData()[0]
        self.assertEqual(option.tradePrice, decimal.Decimal(option.askPrice + option.bidPrice) / decimal.Decimal(2.0))
        self.assertEqual(option.settlementPrice, option.tradePrice)

    def testCheckTradePriceIsCorrectForFuturesOptions(self):
        """Tests that the trade and settlement price is correct for futures options."""
        dataProvider = 'iVolatility'
        dataProviderPath = 'dataHandler/unitTestData/dataProvidersFakeWithSettlementPrice.json'
        eventQueue = queue.Queue()
        csvObj = csvData.CsvData(csvPath=self._csvPath, dataProviderPath=dataProviderPath, dataProvider=dataProvider,
                                 eventQueue=eventQueue)
        csvObj.getNextTick()
        option = eventQueue.get().getData()[0]
        # Note that the settlementPrice for the first row of the CSV is not the same as the (bidPrice + askPrice) / 2,
        # which is what allows us to carry out the test below.
        self.assertEqual(option.tradePrice, option.settlementPrice)


if __name__ == '__main__':
    unittest.main()
