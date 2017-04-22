import pandas as pd

from dataHandler import DataHandler


class CsvData(DataHandler):
    """This class handles data from CSV files which will be used
    for backtests.  The choice of handling a CSV file is through pandas
    The purpose of this class is to take a row of the CSV and create an event
    based on the data in the row
    """

    def __init__(self, csvDir):
        """
        csvDir: input CSV directory of files used in backtesting
        """
        self.__csvDir = csvDir

    def createEvent(self):
        """Based on the incoming data, an event is created and put
        into the queue for later processing; e.g., to be used to generate
        signals
        """
        pass

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

        df = pd.read_csv(self.__csvDir + '/' + filename)

        return df

    def getNextTick(self):
        """
        Used to get the next available piece of data from the data source
        For the CSV example, this would likely be the next row of the CSV
        """
        pass

    def getCSVDir(self):
        """
        Used to get the name of the CSV directory 
        """
        return self.__csvDir
