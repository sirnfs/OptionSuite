from dataHandler import DataHandler

class CsvData(DataHandler):
    """This class handles data from CSV files which will be used
    for backtests.  The choice of handling a CSV file is through pandas
    The purpose of this class is to take a row of the CSV and create an event
    based on the data in the row
    """

    def __init__(self, csvDir, eventQueue):
        """
        csvDir: input CSV directory of files used in backtesting
        eventQueue: queue which contains different events which can be used
        in the backtester or live trader; not specific to data handler -- several
        modules can create and fire off events
        """
        self.__csvDir = csvDir
        self.__eventQueue = eventQueue

    def createEvent(self):
        """Based on the incoming data, an event is created and put
        into the queue for later processing; e.g., to be used to generate
        signals
        """
        pass

    def openDataSource(self):
        """
        Used to connect to the data source for the first time
        In the case of a CSV, this means opening the file
        """
        pass

    def getNextTick(self):
        """
        Used to get the next available piece of data from the data source
        For the CSV example, this would likely be the next row of the CSV
        """
        pass
