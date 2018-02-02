import unittest
import pandas as pd

class TestChunks(unittest.TestCase):

    def testChunkReadsFromCSV(self):
      #Open CSV with a reader iterator
      reader = pd.read_csv('/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_2011_2017/RawIV.csv',
                           iterator=True)
      #print(reader._engine._reader.table_width)

      try:
          curChunk = reader.get_chunk(1)
      except:
          print("Could not get data")
      pass

if __name__ == '__main__':
    unittest.main()

