import csv
import datetime
import decimal
import json
import pandas as pd
import queue
from dataHandler import dataHandler
from base import call
from base import put
from base import option
from events import tickEvent
from typing import Iterable, Mapping, Text

class CsvData(dataHandler.DataHandler):
  """This class handles data from CSV files which will be used for backtesting sessions."""

  def __init__(self, csvPath: Text, dataProvider: Text, eventQueue: queue.Queue) -> None:
    """Initializes CSV data parameters for file reading.

    Attributes:
      csvPath: path to CSV file used in backtesting.
      dataProvider:  historical data provider (e.g, provider of CSV).
      eventQueue:  location to place new data tick event.
    """
    self.__csvPath = csvPath
    self.__curTimeDate = None
    self.__dataConfig = None
    self.__csvReader = None
    self.__csvColumnNames = None
    self.__dateColumnIndex = None
    self.__nextTimeDateRow = None
    self.__dataProvider = dataProvider
    self.__eventQueue = eventQueue

    # Open data source. Raises exception if failure.
    self.__dataConfig = self.__openDataSource()

  def __openDataSource(self) -> Mapping[Text, int]:
    """Used to connect to the data source for the first time. In the case of a CSV, this means opening the file.
    The directory used is determined during initialization.
      :return dictionary from dataProvider.json file.
      :raises FileNotFoundError: Cannot find a CSV at specified location.
      :raises ValueError: Cannot load data as a JSON file.
      :raises ValueError: Requested data provider not found in JSON file.
      :raises ValueError: Number of CSV columns not provided in JSON file.
      :raises ValueError: Number of columns read from CSV does not match number of columns in JSON file.
    """
    try:
      fileHandle = open(self.__csvPath, 'r')
    except OSError as e:
      raise OSError('Unable to open CSV at location: %s.' % self.__csvPath) from e

    # Load data provider information from dataProviders.json file.
    try:
      with open('./dataHandler/dataProviders.json') as dataProvider:
        dataConfig = json.load(dataProvider)
    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
      raise ValueError('Failure when trying to open / load data from JSON file: %s.' % (
        'dataHandler/dataProviders.json')) from e

    # Check that data provider in JSON file matches the provided string in self._dataProvider
    if not self.__dataProvider in dataConfig:
      raise ValueError('The requested data provider: %s was not found in dataProviders.json' % self.__dataProvider)

    # Check that the number of columns in the CSV matches the number specified by the config file.
    self.__csvReader = csv.reader(fileHandle)
    self.__csvColumnNames = next(self.__csvReader)
    numberCsvColumns = len(self.__csvColumnNames)
    if 'number_columns' not in dataConfig[self.__dataProvider]:
      raise ValueError('number_columns not provided in dataProviders.json file')
    if not numberCsvColumns == dataConfig[self.__dataProvider]['number_columns']:
      raise ValueError('Number of columns read from CSV did not match the number of columns in dataProviders.json')
    return dataConfig

  def __getOptionChain(self) -> pd.DataFrame:
    """Used to get the option chain data for the underlying. The option chain consists of all of the puts and calls
    at all strikes currently listed for the underlying.
    :return Pandas dataframe with option chain data.
    """
    # Get the first date if self.__curTimeDate is None.
    dateColumnName = self.__dataConfig[self.__dataProvider]['column_names']['dateTime']
    if self.__curTimeDate is None:
      # Find the index of the date column in the header row of the CSV.
      for index, column in enumerate(self.__csvColumnNames):
        if column == dateColumnName:
          self.__dateColumnIndex = index
      if self.__dateColumnIndex is None:
        raise TypeError('The dateColumnName was not found in the CSV.')

      rowList = []
      # Get the next row of the CSV and convert the date column to a datetime object.
      row = next(self.__csvReader)
      rowList.append(row)
      self.__curTimeDate = datetime.datetime.strptime(row[self.__dateColumnIndex],
                                                      self.__dataConfig[self.__dataProvider]['date_time_format'])

      # Get the rest of the rows that match the curTimeDate.
      for row in self.__csvReader:
        if datetime.datetime.strptime(row[self.__dateColumnIndex],
                                      self.__dataConfig[self.__dataProvider]['date_time_format']) == self.__curTimeDate:
          rowList.append(row)
        else:
          # Need to save the last row that doesn't match the curTimeDate so we can use it again.
          self.__nextTimeDateRow = row
          break

      # Create a Pandas dataframe from the list of lists.
      return pd.DataFrame(rowList, columns=self.__csvColumnNames)

    else:
      if self.__nextTimeDateRow is None:
        return pd.DataFrame()
      # Get the date / time from the previously stored row.
      self.__curTimeDate = datetime.datetime.strptime(self.__nextTimeDateRow[self.__dateColumnIndex],
                                                      self.__dataConfig[self.__dataProvider]['date_time_format'])

      # Get all of the CSV rows for the curTimeDate.
      rowList = []
      rowList.append(self.__nextTimeDateRow)
      for row in self.__csvReader:
        if datetime.datetime.strptime(row[self.__dateColumnIndex],
                                      self.__dataConfig[self.__dataProvider]['date_time_format']) == self.__curTimeDate:
          rowList.append(row)
        else:
          # Need to save the last row that doesn't match the curTimeDate so we can use it again.
          self.__nextTimeDateRow = row
          break

      # If no rows were added above, it means that there's no more data to read from the CSV.
      if len(rowList) == 1:
        self.__nextTimeDateRow = None
        return pd.DataFrame()
      # Create a Pandas dataframe from the list of lists.
      return pd.DataFrame(rowList, columns=self.__csvColumnNames)

  def __createBaseType(self, optionChain: pd.DataFrame) -> Iterable[option.Option]:
    """
    Convert an option chain held in a dataframe to base option types (calls or puts).

    Attributes:
      optionChain: Pandas dataframe with optionChain data as rows.

    :raises ValueError: Symbol for put/call in JSON not found in dataframe column.
    :return: List of Option base type objects (puts or calls).
    """
    optionObjects = []
    # Create a dictionary for the fields that we will read from each row of the dataframe. The fields should also be
    # specified in the dataProviders.json file.
    # Instead of manually specifying the fields below, we could read them from the Option class.
    optionFieldDict = {'underlyingTicker': None, 'strikePrice': None, 'delta': None, 'expirationDateTime': None,
                       'underlyingPrice': None, 'optionSymbol': None, 'bidPrice': None, 'askPrice': None,
                       'tradePrice': None, 'openInterest': None, 'volume': None, 'dateTime': None, 'theta': None,
                       'gamma': None, 'rho': None, 'vega': None, 'impliedVol': None, 'exchangeCode': None,
                       'exercisePrice': None, 'assignPrice': None, 'openCost': None, 'closeCost': None,
                      }
    dataProviderConfig = self.__dataConfig[self.__dataProvider]
    for _, row in optionChain.iterrows():
      # Defaults to PUT (True).
      putOrCall = True
      for option_column_name, dataframe_column_name in dataProviderConfig['column_names'].items():
        # Check that we need to look up the field.
        if not dataframe_column_name:
          continue
        if option_column_name == 'optionType':
          optionType = row[dataframe_column_name]
          # Convert any lowercase symbols to uppercase.
          optionType = str(optionType).upper()
          if optionType == dataProviderConfig['call_symbol_abbreviation']:
            putOrCall = False
          elif optionType == dataProviderConfig['put_symbol_abbreviation']:
            putOrCall = True
          else:
            raise ValueError('Symbol for put / call in dataProviders.json not found in optionType dataframe column.')
        else:
          optionFieldDict[option_column_name] = row[dataframe_column_name]

      if optionFieldDict['bidPrice'] is not None and optionFieldDict['askPrice'] is not None:
        optionFieldDict['tradePrice'] = (decimal.Decimal(optionFieldDict['bidPrice']) + decimal.Decimal(
          optionFieldDict['askPrice'])) / decimal.Decimal(2.0)

      argsDict = {'underlyingTicker': optionFieldDict['underlyingTicker'],
                  'strikePrice': decimal.Decimal(optionFieldDict['strikePrice']),
                  'delta': float(optionFieldDict['delta']), 'expirationDateTime': datetime.datetime.strptime(
                    optionFieldDict['expirationDateTime'], dataProviderConfig['date_time_format']),
                  'underlyingPrice': decimal.Decimal(optionFieldDict['underlyingPrice']),
                  'optionSymbol': optionFieldDict['optionSymbol'],
                  'bidPrice': decimal.Decimal(optionFieldDict['bidPrice']),
                  'askPrice': decimal.Decimal(optionFieldDict['askPrice']),
                  'tradePrice': decimal.Decimal(optionFieldDict['tradePrice']),
                  'openInterest': int(optionFieldDict['openInterest']), 'volume': int(optionFieldDict['volume']),
                  'dateTime': datetime.datetime.strptime(optionFieldDict['dateTime'],
                                                         dataProviderConfig['date_time_format']),
                  'theta': float(optionFieldDict['theta']),
                  'gamma': float(optionFieldDict['gamma']), 'rho': float(optionFieldDict['rho']),
                  'vega': float(optionFieldDict['vega']), 'impliedVol': float(optionFieldDict['impliedVol']),
                  'exchangeCode': optionFieldDict['exchangeCode'],
                  'exercisePrice': decimal.Decimal(optionFieldDict['exercisePrice']) if
                    optionFieldDict['exercisePrice'] else None,
                  'assignPrice': decimal.Decimal(optionFieldDict['assignPrice']) if optionFieldDict[
                    'assignPrice'] else None,
                  'openCost': decimal.Decimal(optionFieldDict['openCost']) if optionFieldDict[
                    'openCost'] else None,
                  'closeCost': decimal.Decimal(optionFieldDict['closeCost']) if optionFieldDict[
                    'closeCost'] else None,
                  }
      if not putOrCall:
        optionObjects.append(call.Call(**argsDict))
      else:
        optionObjects.append(put.Put(**argsDict))

      # Reset all the dictionary values back to None. This is probably overkill since we can just rewrite them.
      optionFieldDict = optionFieldDict.fromkeys(optionFieldDict, None)
    return optionObjects

  def getNextTick(self) -> bool:
    """Used to get the next available piece of data from the data source. For the CSV example, this would likely be the
    next row for a stock or group of rows for an option chain.
    :return True / False indicating if there is data available.
    """
    if self.__dataConfig[self.__dataProvider]['data_source_type'] == 'options':
      # Get optionChain as a dataframe.
      optionChain = self.__getOptionChain()
      if len(optionChain.index) == 0:
        # No more data available.
        return False
      # Convert optionChain from a dataframe to Option class objects.
      optionChainObjs = self.__createBaseType(optionChain)
      # Create tick event with option chain objects.
      event = tickEvent.TickEvent()
      event.createEvent(optionChainObjs)
      self.__eventQueue.put(event)
      return True
    elif self.__dataConfig[self.__dataProvider]['data_source_type'] == 'stocks':
      pass
