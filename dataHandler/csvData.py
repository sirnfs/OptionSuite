import pandas as pd
import datetime
from dataHandler import DataHandler
from base import stock
from base import call
from base import put
from event import tickEvent


class CsvData(DataHandler):
    """This class handles data from CSV files which will be used
    for backtests.  The choice of handling a CSV file is through pandas
    The purpose of this class is to get handle CSV data operations
    """

    def __init__(self, csvDir, filename, dataProvider, eventQueue):
        """
        csvDir: input CSV directory of files used in backtesting
        filename:  filename of CSV to process
        curRow: current row we are processing in the CSV
        dataAvailable:  indicates the data source has been opened successfully
        dataFrame:  pandas dataframe which contains the CSV
        dataProvider:  historical data provider (e.g, provider of CSV)
        eventQueue:  location to place new data tick event
        """
        self.__csvDir = csvDir
        self.__curRow = 0
        self.__dataAvailable = False
        self.__dataFrame = None
        self.__dataProvider = dataProvider
        self.__eventQueue = eventQueue

        self.openDataSource(filename)

    def openDataSource(self, filename):
        """
        Used to connect to the data source for the first time
        In the case of a CSV, this means opening the file
        The directory used is determined on init
        
        Args:
        filename:  input CSV file which contains historical data

        Returns:
        pandas dataframe of loaded CSV file
        """

        try:
            self.__dataFrame = pd.read_csv(self.__csvDir + '/' + filename)
            self.__dataAvailable = True
        except IOError:
            print("Unable to open data source")
            raise

        if len(self.__dataFrame.columns) != 24:
            print("CSV did not have right number of columns")
            raise

    def getNextTick(self):
        """
        Used to get the next available piece of data from the data source
        For the CSV example, this would likely be the next row of the CSV
        """

        # Check that data source has been opened
        if self.__dataAvailable:

            # Attempt to get data from CSV at row __curRow
            try:
                curRowData = self.__dataFrame.ix[self.__curRow]
            except:
                curRowData = None
                #return curRowData

            # Create a base data type -- stock, put, or call
            baseType = self.createBaseType(curRowData)
            if  baseType != None:

                #Create event and add to queue
                event = tickEvent.TickEvent()
                event.createEvent(baseType)
                self.__eventQueue.put(event)

                # Increment to the next row
                self.__curRow += 1

                #return baseType
            else:
                # Increment to the next row
                self.__curRow += 1
                #TODO:  need to do some action here
                #return None

        else:
            #TODO:  Need to do something here
            pass
            #return None

    def getCSVDir(self):
        """
        Used to get the name of the CSV directory 
        """
        return self.__csvDir

    def createBaseType(self, inputData):
        """
        Used to take a tick (e.g., row from CSV) and create a base type 
        such as a stock or option (call or put)
        """
        if self.__dataProvider == "iVolatility":
            #CSV header
            #symbol, exchange, company_name, date, stock_price_close, option_symbol, expiration_date, strike,
            #call_put, style, ask, bid, mean_price, settlement, iv, volume, open_interest, stock_price_for_iv,
            #isinterpolated, delta, vega, gamma, theta, rho

            #Do type checking on fields
            underlyingTicker = inputData['symbol']

            exchange = inputData['exchange']
            optionSymbol = inputData['option_symbol']

            #Check if style is American or European
            style = inputData['style']
            if style != 'A' and style != 'E':
                return None

            #Check that underlyingTicker is a character string
            if not underlyingTicker.isalpha():
                return None

            #Check that fields below are floating point numbers
            try:
                strikePrice = float(inputData['strike'])
                underlyingPrice = float(inputData['stock_price_close'])
                askPrice = float(inputData['ask'])
                bidPrice = float(inputData['bid'])
                impliedVol = float(inputData['iv'])
                volume = float(inputData['volume'])
                openInterest = int(inputData['open_interest'])
                delta = float(inputData['delta'])
                theta = float(inputData['theta'])
                vega = float(inputData['vega'])
                gamma = float(inputData['gamma'])
                rho = float(inputData['rho'])

            except:
                return None

            #Convert expiration date to a datetime Python object
            try:
                DTE = datetime.datetime.strptime(inputData['expiration_date'], "%m/%d/%Y")
            except:
                return None

            call_put = inputData['call_put']

            if call_put == 'C':
                #def __init__(self, underlyingTicker, strikePrice, delta, DTE, longOrShort=None, underlyingPrice=None,
                # optionSymbol=None, optionAlias=None, bidPrice=None, askPrice=None, openInterest=None,
                # volume=None, dateTime=None, theta=None, gamma=None, rho=None, vega=None, impliedVol=None,
                # exchangeCode=None, exercisePrice=None, assignPrice=None, openCost=None, closeCost=None, tradeID=None)
                return call.Call(underlyingTicker, strikePrice, delta, DTE, None, underlyingPrice, optionSymbol,
                                 None, bidPrice, askPrice, openInterest, volume, None, theta, gamma, rho, vega,
                                 impliedVol, exchange, None, None, None, None, None)

            elif call_put == 'P':
                return put.Put(underlyingTicker, strikePrice, delta, DTE, None, underlyingPrice, optionSymbol,
                               None, bidPrice, askPrice, openInterest, volume, None, theta, gamma, rho, vega,
                               impliedVol, exchange, None, None, None, None, None)

            else:
                return None

        else:
            print("Unrecognized CSV data source provider")
            raise

