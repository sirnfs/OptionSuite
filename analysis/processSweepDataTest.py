from analysis import processSweepData
import decimal
import numpy as np
import pandas as pd
import unittest


class TestProcessSweepData(unittest.TestCase):

  def testComputeMaxDrawDown(self):
    """Tests that the max draw down is computed correctly."""
    # Create some curves / lines.
    segmentOne = np.linspace(0, 100, 50)
    segmentTwo = np.linspace(100, -20, 50)
    segmentThree = np.linspace(-20, 80, 50)
    segmentFour = np.linspace(80, -40, 50)
    allSegments = pd.Series(np.append(np.append(segmentOne, segmentTwo), np.append(segmentThree, segmentFour)))
    self.assertEqual(processSweepData.computeMaxDrawDown(allSegments), 140.0)

  def testComputeAverageDailyPL(self):
    netLiquidityData = pd.Series([1000, 2000, 1500, 3000])
    numContractsData = pd.Series([2, 2, 2, 4])
    self.assertAlmostEqual(processSweepData.computeAverageDailyPL(netLiquidityData, numContractsData),
                           decimal.Decimal(250))

  def testComputeStdDevDailyPL(self):
    netLiquidityData = pd.Series([1000, 2000, 1500, 3000])
    numContractsData = pd.Series([2, 2, 2, 4])
    self.assertAlmostEqual(processSweepData.computeStdDevDailyPL(netLiquidityData, numContractsData),
                           decimal.Decimal('433.01270189'))

if __name__ == '__main__':
  unittest.main()
