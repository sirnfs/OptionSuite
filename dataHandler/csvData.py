import pandas as pd
import datetime
import pytz
import sys
import logging
from dataHandler import DataHandler
from base import call
from base import put
from events import tickEvent

class CsvData(DataHandler):
    """This class handles data from CSV files which will be used
    for backtests.  The choice of handling a CSV file is through pandas
    The purpose of this class is to get handle CSV data operations
    """

    def __init__(self, csvDir, filename, dataProvider, eventQueue, chunkSize):
        """
        csvDir: input CSV directory of files used in backtesting
        filename:  filename of CSV to process
        curRow: current row we are processing in the CSV
        curTimeData:  the time information for the current option chain tick
        dataAvailable:  indicates the data source has been opened successfully
        dataFrame:  pandas dataframe which contains the CSV
        dataProvider:  historical data provider (e.g, provider of CSV)
        eventQueue:  location to place new data tick event
        """
        self.__csvDir = csvDir
        self.__curRow = 0
        self.__chunkSize = chunkSize
        self.__curTimeDate = None
        self.__dataAvailable = False
        self.__dataReader = None
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
        """

        try:
            self.__dataReader = pd.read_csv(self.__csvDir + '/' + filename, iterator=True)
            #Get a chunk and store it in the dataFrame
            self.__dataFrame = self.__dataReader.get_chunk(self.__chunkSize)
        except IOError:
            print("Unable to open data source")
            raise

        self.__dataAvailable = True

        #TODO:  is there a function to get the table_width?
        if self.__dataProvider == "iVolatility":
            try:
                self.__dataReader._engine._reader.table_width == 25
            except:
                print("CSV did not have right number of columns")
                raise

    def getOptionChain(self):
        """
        Used to get the option chain data for the underlying;
        The option chain consists of all of the puts and calls
        at all strikes currently listed for the underlying
        Returns true/false depending on whether or not we successfully
        were able to get the option chain data.  On success, the
        the rows of the option chain are converted into option objects,
        and the objects are put into the eventQueue as one event
        """

        #Attempt to get option chain from CSV -- the way we determine
        #which strikes / data belong to the option chain for the current
        #tick is by keeping track of the time/date

        #Used to store all rows in current option chain
        optionChain = []

        #Used to store objects created for each row of the option chain
        optionChainObjs = []

        #Potentially different data providers will have to be handled differently
        #TODO:  This should be abstracted out so that date/time maps to the right
        #column header for different data providers
        if self.__dataProvider == "iVolatility":

            #Get the first N rows with the same time/date
            #To do this, we get the time/data from the first row, and then
            #we add to this any rows with the same date/time

            #Handle first row -- add to optionChain
            try:
                optionChain.append(self.__dataFrame.iloc[self.__curRow])
                self.__curTimeDate = self.__dataFrame['date'].iloc[self.__curRow]
                self.__curRow += 1
            except:
                #Could not get the current row if we end up here; try chunking to get more data
                try:
                    self.__dataFrame = self.__dataReader.get_chunk(self.__chunkSize)
                    self.__curRow = 0
                    optionChain.append(self.__dataFrame.iloc[self.__curRow])
                    self.__curTimeDate = self.__dataFrame['date'].iloc[self.__curRow]
                    self.__curRow += 1
                except:
                    return False

            #TODO:  replace this while loop with something more efficient --
            #for example, can select all dates from dataframe and then iterate
            #through them; we would need to keep track of the curRow still so we
            #can get the next option chain.  We do it in this manner since this
            #seems that it would be faster if we had a HUGE CSV and tried to
            #do a bunch of groups for different dates
            while 1:
                try:
                    curTimeDate = self.__dataFrame['date'].iloc[self.__curRow]
                except:
                    #Try chunking to get more data  since we couldn't get current row
                    try:
                        self.__dataFrame = self.__dataReader.get_chunk(self.__chunkSize)
                        self.__curRow = 0
                        curTimeDate = self.__dataFrame['date'].iloc[self.__curRow]
                    except:
                        break

                if curTimeDate == self.__curTimeDate:
                    optionChain.append(self.__dataFrame.iloc[self.__curRow])
                    self.__curRow +=1
                else:
                    break

            #Convert option chain to base types (calls, puts)
            for row in optionChain:
                currentObj = self.createBaseType(row)
                #Make sure currentObj is not None
                if currentObj:
                    optionChainObjs.append(currentObj)

            # Create event and add to queue
            event = tickEvent.TickEvent()
            event.createEvent(optionChainObjs)
            self.__eventQueue.put(event)

            return True

    def getNextTick(self):
        """
        Used to get the next available piece of data from the data source
        For the CSV example, this would likely be the next row or option chain
        """

        # Check that data source has been opened
        if self.__dataAvailable:

            #Get option chain and create event
            if self.getOptionChain():
                return True
            else:
                return False

        else:
            #No event will be created, so nothing to do here.
            return False

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
                underlyingTradePrice = underlyingPrice
                askPrice = float(inputData['ask'])
                bidPrice = float(inputData['bid'])
                tradePrice = (askPrice + bidPrice) / 2
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

            #Convert current date and expiration date to a datetime Python object
            try:
                local = pytz.timezone('US/Eastern')
                #Convert time zone of data 'US/Eastern' to UTC time
                # Try and except here to handle two or four digit year format
                try:
                    DTE = datetime.datetime.strptime(inputData['option_expiration'], "%m/%d/%y")
                except:
                    DTE = datetime.datetime.strptime(inputData['option_expiration'], "%m/%d/%Y")

                DTE = local.localize(DTE, is_dst=None)
                DTE = DTE.astimezone(pytz.utc)

                try:
                    curDateTime = datetime.datetime.strptime(inputData['date'], "%m/%d/%y")
                except:
                    curDateTime = datetime.datetime.strptime(inputData['date'], "%m/%d/%Y")

                curDateTime = local.localize(curDateTime, is_dst=None)
                curDateTime = curDateTime.astimezone(pytz.utc)
            except:
                logging.warning('Something went wrong when trying to read the option data from the CSV')
                return None

            call_put = inputData['call/put']

            if call_put == 'C':
                return call.Call(underlyingTicker, strikePrice, delta, DTE, None, underlyingPrice, underlyingTradePrice,
                                 optionSymbol, None, bidPrice, askPrice, tradePrice, openInterest, volume, curDateTime,
                                 theta, gamma, rho, vega, impliedVol, exchange)

            elif call_put == 'P':
                return put.Put(underlyingTicker, strikePrice, delta, DTE, None, underlyingPrice, underlyingTradePrice,
                               optionSymbol, None, bidPrice, askPrice, tradePrice, openInterest, volume, curDateTime,
                               theta, gamma, rho, vega, impliedVol, exchange)

            else:
                return None

        else:
            print("Unrecognized CSV data source provider")
            sys.exit(1)

