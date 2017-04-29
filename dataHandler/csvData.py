import pandas as pd
import datetime
from dataHandler import DataHandler
from base import stock
from base import call
from base import put


class CsvData(DataHandler):
    """This class handles data from CSV files which will be used
    for backtests.  The choice of handling a CSV file is through pandas
    The purpose of this class is to get handle CSV data operations
    """

    def __init__(self, csvDir):
        """
        csvDir: input CSV directory of files used in backtesting
        curRow: current row we are processing in the CSV
        dataAvailable:  indicates the data source has been opened successfully
        dataFrame:  pandas dataframe which contains the CSV
        dataProvider:  historical data provider (e.g, provider of CSV)
        """
        self.__csvDir = csvDir
        self.__curRow = 0
        self.__dataAvailable = False
        self.__dataFrame = None
        # TODO:  need to use enum here for dataProvider
        self.__dataProvider = None

    def openDataSource(self, filename, dataProvider):
        """
        Used to connect to the data source for the first time
        In the case of a CSV, this means opening the file
        The directory used is determined on init
        
        Args:
        filename:  input CSV file which contains historical data
        dataProvider:  historical data provider -- this is needed since
        formats will different from one provider to the next

        Returns:
        pandas dataframe of loaded CSV file
        """
        #TODO:  Check that the CSV from the dataprovider has the right number of columns;
        # otherwise raise exception and quit
        try:
            self.__dataFrame = pd.read_csv(self.__csvDir + '/' + filename)
            self.__dataAvailable = True
            self.__dataProvider = dataProvider
        except IOError:
            print("Unable to open data source")
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
                return curRowData

            # Create a base data type -- stock, put, or call
            baseType = self.createBaseType(curRowData)
            if  baseType != None:
                # Increment to the next row
                self.__curRow += 1
                return baseType
            else:
                # Increment to the next row
                self.__curRow += 1
                return None

        else:
            return None

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

            #Check that underlyingTicker is a character string
            if not underlyingTicker.isalpha():
                return None

            #Check that strike price and delta is a number
            try:
                strikePrice = float(inputData['strike'])
                delta = float(inputData['delta'])
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
                return call.Call(underlyingTicker, strikePrice, delta, DTE)

            elif call_put == 'P':
                return put.Put(underlyingTicker, strikePrice, delta, DTE)

            else:
                return None

        else:
            print("Unrecognized CSV data source provider")
            raise

