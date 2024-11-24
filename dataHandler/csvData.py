import copy
import csv
import datetime
import decimal
import json
import logging
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

    def __init__(self, csvPath: Text, dataProviderPath: Text, dataProvider: Text, eventQueue: queue.Queue) -> None:
        """Initializes CSV data parameters for file reading.

        Attributes:
          csvPath: path to CSV file used in backtesting.
          dataProviderPath: path to data provider JSON file.
          dataProvider:  historical data provider (e.g, provider of CSV).
          eventQueue:  location to place new data tick event.
        """
        self.__csvPath = csvPath
        self.__dataProviderPath = dataProviderPath
        self.__curTimeDate = None
        self.__dataConfig = None
        self.__csvReader = None
        self.__csvColumnNames = None
        self.__dateColumnName = None
        self.__nextTimeDateRow = None
        self.__dataProvider = dataProvider
        self.__eventQueue = eventQueue

        # Open data source. Raises exception if failure.
        self.__dataConfig = self.__openDataSource()

    def __openDataSource(self) -> Mapping[Text, Mapping[Text, Mapping[Text, Text]]]:
        """Used to connect to the data source for the first time. In the case of a CSV, this means opening the file.
          The directory used is determined during initialization.

          :return dictionary from dataProviders.json file.
          :raises OSError: Cannot find a CSV at specified location.
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
            with open(self.__dataProviderPath) as dataProvider:
                dataConfig = json.load(dataProvider)
        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            raise ValueError('Failure when trying to open / load data from JSON file: %s.' % (
                self.__dataProviderPath)) from e

        # Check that data provider in JSON file matches the provided string in self._dataProvider
        if self.__dataProvider not in dataConfig:
            raise ValueError(
                'The requested data provider: %s was not found in dataProviders.json' % self.__dataProvider)

        # Check that the number of columns in the CSV matches the number specified by the config file.
        self.__csvReader = csv.DictReader(fileHandle)
        self.__csvColumnNames = self.__csvReader.fieldnames
        numberCsvColumns = len(self.__csvColumnNames)
        if 'number_columns' not in dataConfig[self.__dataProvider]:
            raise ValueError('number_columns was not provided in dataProviders.json file.')
        if not numberCsvColumns == dataConfig[self.__dataProvider]['number_columns']:
            raise ValueError(
                'Number of columns in CSV and dataProviders.json do not match.')
        return dataConfig

    def __getMatchingRows(self) -> Iterable[Iterable[Text]]:
        """Gets all rows in CSV that match the current time / date.

           :return List of lists of matching rows.
        """
        rowList = []
        for row in self.__csvReader:
            if datetime.datetime.strptime(row[self.__dateColumnName],
                                          self.__dataConfig[self.__dataProvider][
                                              'date_time_format']) == self.__curTimeDate:
                rowList.append(row)
            else:
                # Save the last row that doesn't match the curTimeDate, so we can use it for the next option chain.
                self.__nextTimeDateRow = row
                break
        return rowList

    def __getOptionChain(self) -> pd.DataFrame:
        """Used to get the option chain data for the underlying. The option chain consists of all the puts and calls
          at all strikes currently listed for the underlying.

          :return Pandas dataframe with option chain data.
        """
        self.__dateColumnName = self.__dataConfig[self.__dataProvider]['column_names']['dateTime']
        if not self.__dateColumnName in self.__csvColumnNames:
            raise TypeError('The dateColumnName was not found in the CSV.')

        # Get the first date from the CSV if self.__curTimeDate is None.
        if self.__curTimeDate is None:
            # Find the index of the date column in the header row of the CSV.
            rowList = []
            # Get the next row of the CSV and convert the date column to a datetime object.
            row = next(self.__csvReader)
            rowList.append(row)
            self.__curTimeDate = datetime.datetime.strptime(row[self.__dateColumnName],
                                                            self.__dataConfig[self.__dataProvider]['date_time_format'])
            # Get the rest of the rows that match the curTimeDate.
            rowList.extend(self.__getMatchingRows())

            # Create a Pandas dataframe from the rows with matching date.
            return pd.DataFrame(rowList, columns=self.__csvColumnNames)

        else:
            if self.__nextTimeDateRow is None:
                logging.warning('None was returned for the nextTimeDateRow in the CSV reader.')
                return pd.DataFrame()
            # Get the date / time from the previously stored row.
            self.__curTimeDate = datetime.datetime.strptime(self.__nextTimeDateRow[self.__dateColumnName],
                                                            self.__dataConfig[self.__dataProvider]['date_time_format'])

            # Get all the CSV rows for the curTimeDate.
            rowList = []
            rowList.append(self.__nextTimeDateRow)
            # Get the rest of the rows that match the curTimeDate.
            rowList.extend(self.__getMatchingRows())

            # If no rows were added above, it means that there's no more data to read from the CSV.
            if len(rowList) == 1:
                self.__nextTimeDateRow = None
                return pd.DataFrame()
            # Create a Pandas dataframe from the list of lists.
            return pd.DataFrame(rowList, columns=self.__csvColumnNames)

    def __createBaseType(self, optionChain: pd.DataFrame) -> Iterable[option.Option]:
        """Convert an option chain held in a dataframe to base option types (calls or puts).

          Attributes:
            optionChain: Pandas dataframe with optionChain data as rows.

          :raises ValueError: Symbol for put/call in JSON not found in dataframe column
          :raises ValueError: Dictionary sizes don't match.
          :raises ValueError: optionType not found in the dataProviders.json file.
          :raises ValueError: dataProvider.json column name not found in CSV.
          :return: List of Option base type objects (puts or calls).
        """
        optionObjects = []
        optionTypeField = 'optionType'
        dataProviderConfig = self.__dataConfig[self.__dataProvider]
        # Create a dictionary for the fields that we will read from each row of the dataframe. The fields should
        # also be specified in the dataProviders.json file.
        optionFieldDict = self.__dataConfig[self.__dataProvider]['column_names']
        optionDict = copy.deepcopy(optionFieldDict)
        # We don't need the optionTypeField in optionDict, so let's delete it.
        del optionDict[optionTypeField]
        for _, row in optionChain.iterrows():
            # Defaults to PUT (True).
            putOrCall = True
            optionTypeFound = False
            for option_column_name, dataframe_column_name in optionFieldDict.items():
                # Check that we need to look up the field (don't need field if it's blank in dataProviders.json).
                if not dataframe_column_name:
                    continue
                if dataframe_column_name not in row:
                    raise ValueError(
                        'Column name %s in dataProvider.json not found in CSV.' % dataframe_column_name)
                if option_column_name == optionTypeField:
                    optionType = row[dataframe_column_name]
                    # Convert any lowercase symbols to uppercase.
                    optionType = str(optionType).upper()
                    if optionType == dataProviderConfig['call_symbol_abbreviation']:
                        putOrCall = False
                    elif optionType == dataProviderConfig['put_symbol_abbreviation']:
                        putOrCall = True
                    else:
                        raise ValueError(
                            'Symbol for put / call in dataProviders.json not found in optionChain dataframe.')
                    # Will be used to remove optionTypeField  from the optionFieldDict to make the processing below more
                    # straightforward.
                    optionTypeFound = True
                else:
                    optionDict[option_column_name] = row[dataframe_column_name]

            if not optionTypeFound:
                raise ValueError('dataProviders.json must have an entry for optionType')

            # For futures options, we rely on settlementPrice, and for index options, we rely on tradePrice.
            # We will use one variable settlementPrice for both, so we set the settlementPrice = tradePrice for
            # index options. Let's check if settlementPrice is None or empty.
            if optionDict['settlementPrice'] is None or not optionDict[
                  'settlementPrice']:  # For index options
                if optionDict['bidPrice'] is not None and optionDict['askPrice'] is not None:
                    optionDict['tradePrice'] = (decimal.Decimal(optionDict['bidPrice']) + decimal.Decimal(
                        optionDict['askPrice'])) / decimal.Decimal(2.0)
                optionDict['settlementPrice'] = optionDict['tradePrice']
            else:  # For future options.
                optionDict['tradePrice'] = optionDict['settlementPrice']

            # Do some formatting of the entries.
            argsDict = {'underlyingTicker': optionDict['underlyingTicker'] if optionDict[
              'underlyingTicker'] else None,
                'strikePrice': decimal.Decimal(optionDict['strikePrice']) if optionDict[
                    'strikePrice'] else None,
                'delta': float(optionDict['delta']) if optionDict['delta'] else None,
                'expirationDateTime': datetime.datetime.strptime(
                    optionDict['expirationDateTime'], dataProviderConfig['date_time_format']) if optionDict[
                  'expirationDateTime'] else None,
                'underlyingPrice': decimal.Decimal(optionDict['underlyingPrice'] if optionDict[
                    'underlyingPrice'] else None),
                'optionSymbol': optionDict['optionSymbol'] if optionDict['optionSymbol'] else None,
                'bidPrice': decimal.Decimal(optionDict['bidPrice']) if optionDict[
                    'bidPrice'] else None,
                'askPrice': decimal.Decimal(optionDict['askPrice']) if optionDict[
                    'askPrice'] else None,
                'settlementPrice': decimal.Decimal(optionDict['settlementPrice']) if optionDict[
                    'settlementPrice'] else None,
                'tradePrice': decimal.Decimal(optionDict['tradePrice']) if optionDict[
                    'tradePrice'] else None,
                'openInterest': int(optionDict['openInterest']) if optionDict[
                    'openInterest'] else None,
                'volume': int(optionDict['volume']) if optionDict['volume'] else None,
                'dateTime': datetime.datetime.strptime(optionDict['dateTime'],
                                                       dataProviderConfig['date_time_format']) if optionDict[
                  'dateTime'] else None,
                'tradeDateTime': datetime.datetime.strptime(
                    optionDict['dateTime'], dataProviderConfig['date_time_format']) if optionDict[
                    'dateTime'] else None,
                'theta': float(optionDict['theta']) if optionDict['theta'] else None,
                'gamma': float(optionDict['gamma']) if optionDict['gamma'] else None,
                'rho': float(optionDict['rho']) if optionDict['rho'] else None,
                'vega': float(optionDict['vega']) if optionDict['vega'] else None,
                'impliedVol': float(optionDict['impliedVol']) if optionDict['impliedVol'] else None,
                'exchangeCode': optionDict['exchangeCode'] if optionDict['exchangeCode'] else None,
                }
            if not putOrCall:
                optionObjects.append(call.Call(**argsDict))
            else:
                optionObjects.append(put.Put(**argsDict))
        return optionObjects

    def getNextTick(self) -> bool:
        """Used to get the next available piece of data from the data source. For the CSV example, this would likely be
          the next row for a stock or group of rows for an option chain.

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
        else:
            raise TypeError('data_source_type not supported.')
