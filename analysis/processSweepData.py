import decimal
import numpy as np
import pandas as pd
import os
import sys
import yaml
from typing import Dict, List, Text

def computeMaxDrawDown(netLiquidity: pd.Series) -> decimal.Decimal:
  """Compute the maximum drawn down from one backtest (sweep).

  Max drawdown is defined as the greatest distance (difference) between a peak and trough.

  Args:
    netLiquidity: Pandas series (net liquidity column).

  Returns:
    Max drawdown value.
  """
  trough = float('inf')
  peak = float('-inf')
  maxDrawDown = 0

  for _, value in netLiquidity.items():
    if value > peak:
      trough = peak
      peak = value
    elif value < trough:
      trough = value
      drawDown = peak - trough
      if drawDown > maxDrawDown:
        maxDrawDown = drawDown
  return decimal.Decimal(maxDrawDown)

def computeAverageDailyPL(netLiquidity: pd.Series, numContracts: pd.Series) -> decimal.Decimal:
  """Comptues the average P/L per day from net liquidity.

  Args:
    netLiquidity: Pandas series (net liquidity column).
    numContracts: Pandas series (num contracts column).

  Returns:
    Average daily P/L.
  """
  differences = netLiquidity.diff()

  # The first row will have a NaN -- remove it.
  differences = differences.dropna()

  # Compute the average # of contracts between rows.
  contractAverages = numContracts.rolling(2).mean()
  contractAverages = contractAverages.dropna()

  # Drop rows from differences where the mean number of contracts for two rows is zero.
  rowsToKeepIndices = contractAverages.nonzero()
  differences = differences.iloc[rowsToKeepIndices]
  contractAverages = contractAverages.iloc[rowsToKeepIndices]

  # Normalize the differences by the number of contracts.
  differences = differences / contractAverages

  # Compute the mean of the values in differences.
  return decimal.Decimal(differences.mean())

def computeStdDevDailyPL(netLiquidity: pd.Series, numContracts: pd.Series) -> decimal.Decimal:
  """Comptues the standard deviation P/L per day from net liquidity.

  Args:
    netLiquidity: Pandas series (net liquidity column).
    numContracts: Pandas series (num contracts column).

  Returns:
    Std dev of daily P/L.
  """
  # Net liquidity differences.
  differences = netLiquidity.diff()

  # The first row will have a NaN -- remove it.
  differences = differences.dropna()

  # Compute the average # of contracts between rows.
  contractAverages = contractAverages = numContracts.rolling(2).mean()
  contractAverages = contractAverages.dropna()

  # Drop rows from differences where the mean number of contracts for two rows is zero.
  rowsToKeepIndices = contractAverages.nonzero()
  differences = differences.iloc[rowsToKeepIndices]
  contractAverages = contractAverages.iloc[rowsToKeepIndices]

  # Normalize the differences by the number of contracts.
  differences = differences / contractAverages

  # Compute the std dev of the values in differences.
  return decimal.Decimal(differences.std())

def computeSweepStats(sweepData: pd.DataFrame) -> List:
  """Comptutes statistics on the dataframe for the current sweep.

  The following statistics are computed:
  (1) Max draw down.
  (2) Average P/L per day.

  Args:
    sweepData: Pandas dataframe with the following columns: {Date, UnderlyingPrice, NetLiq, RealizedCapital,
     NumPositions, TotNumContracts, BuyingPower, TotalDelta}

  Returns:
    List of statistics. [MaxDrawDown,]
  """
  maxDrawDown = computeMaxDrawDown(sweepData['NetLiq'])
  averagePLDay = computeAverageDailyPL(sweepData['NetLiq'], sweepData['TotNumContracts'])
  stdPLDay = computeStdDevDailyPL(sweepData['NetLiq'], sweepData['TotNumContracts'])
  return [maxDrawDown, averagePLDay, stdPLDay]

def getStatistics(currentSweepPath: Text) -> Dict[Text, float]:
  """For the sweep configuration, pull out the the sweep parameters from overrides.yaml and the data from
  monitoring.csv. From this data, compute the statistics for the current sweep.

  We assume that inside the currentSweepPath there is a file named monitoring.csv, and a hidden directory named
  .hydra which contains the file overrides.yaml. The dictionary key will come from the overrides.yaml file by
  combining all lines in the file, and the value will come from the statistics computed on the monitoring.csv.

  Args:
    currentSweepPath: path to the data for the current sweep.

  Returns:
    Dictionary entry keyed on the override.yaml config and with the statistics as the value array.
  """
  overrideConfigPath = os.path.join(currentSweepPath, '.hydra/overrides.yaml')
  monitoringCsvPath = os.path.join(currentSweepPath, 'monitoring.csv')

  # Create the dictionary key.
  key = ''
  with open(overrideConfigPath, 'r') as overrideStream:
    try:
      data = yaml.safe_load(overrideStream)
      # Combine list into a single string.
      key = '_'.join(element for element in data)
    except yaml.YAMLError as err:
      print(err)

  # Create the dictionary value.
  value = ''
  stats = []
  try:
    sweepData = pd.read_csv(monitoringCsvPath)

    # Compute a set of statistics on the pandas dataframe.
    stats = computeSweepStats(sweepData)

    # Get the realized capital.
    lastRow = sweepData.tail(1)
    realizedCapital = lastRow['RealizedCapital'].values[0]
    stats.append(decimal.Decimal(realizedCapital))

    # Get the win percentage.
    wins = lastRow['Wins'].values[0]
    losses = lastRow['Losses'].values[0]
    winPercentage = (wins / (wins + losses))*100
    stats.append(winPercentage)
  except:
    print('Could not read from the CSV at path: ', monitoringCsvPath)

  return {key: stats}

if __name__ == "__main__":

  # Path to the sweep directory.
  sweepPath = '/Users/msantoro/PycharmProjects/Backtester/multirun/2022-05-29/21-34-05'

  # Dictionary to hold strategy info and cumulative gain for each strategy.
  sweepStatistics = {}

  # Walk through the sweep directory path and visit all of the subdirectories.
  for entry in os.listdir(sweepPath):
    path = os.path.join(sweepPath, entry)
    if os.path.isdir(path):
      gain = getStatistics(path)
      sweepStatistics.update(gain)

  # Write out strategyGains to CSV.
  outputCsvPath = '/Users/msantoro/PycharmProjects/Backtester/sweepSummary05_30_2022_v2.csv'
  outputDataframe = pd.DataFrame.from_dict(sweepStatistics, orient='index', columns=['maxDrawDown', 'averagePLDay',
                                                                                     'stdDevPLDay', 'cumulativePL',
                                                                                     'winPercentage'])
  outputDataframe.to_csv(outputCsvPath)