import unittest
import decimal
from dataHandler import csvData
import queue

class TestCSVHandler(unittest.TestCase):

  def setUp(self):
      # Create CsvData class object.
      self._dataProvider = 'iVolatility'
      self._filename = '/Users/msantoro/PycharmProjects/Backtester/sampleData/aapl_sample_ivolatility.csv'
      self._eventQueue = queue.Queue()
      self._csvObj = csvData.CsvData(csvPath=self._filename, dataProvider=self._dataProvider,
                                     eventQueue=self._eventQueue)

  def testOpenDataSourceNoCSVFound(self):
    """Tests that an exception is raised when no CSV is found."""
    with self.assertRaisesRegex(OSError, 'Unable to open CSV at location: bad_path_name.'):
      csvData.CsvData(csvPath='bad_path_name', dataProvider=self._dataProvider,
                      eventQueue=self._eventQueue)

  def testOpenDataSourceInvalidDataProvider(self):
    """Tests that an exception is rasied if the requested data provider isn't in the config file."""
    with self.assertRaisesRegex(ValueError, ('The requested data provider: unknown_data_provider was not found in '
      'dataProviders.json')):
      csvData.CsvData(csvPath=self._filename, dataProvider='unknown_data_provider',
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
    dataProvider = 'iVolatility'
    filename = '/Users/msantoro/PycharmProjects/Backtester/sampleData/bad_column_name.csv'
    eventQueue = queue.Queue()
    csvObj = csvData.CsvData(csvPath=filename, dataProvider=dataProvider, eventQueue=eventQueue)

    with self.assertRaisesRegex(TypeError, ('The dateColumnName was not found in the CSV')):
      csvObj.getNextTick()

  def testCreateBaseType(self):
    """Tests that Put and Call objects are created successfully."""
    # First row in the sample data is a call, and second row is a put.
    eventQueue = queue.Queue()
    csvObj = csvData.CsvData(csvPath=self._filename, dataProvider=self._dataProvider, eventQueue=eventQueue)
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

if __name__ == '__main__':
    unittest.main()

