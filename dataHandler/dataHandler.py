from abc import ABCMeta, abstractmethod

class DataHandler(object):
    """This class is a generic type for handling incoming data
    Incoming data sources could be historical data in the form of
    a CSV or a database, or it could be live tick data coming from
    an exchange
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def createEvent(self):
        """Based on the incoming data, an event is created and put
        into the queue for later processing; e.g., to be used to generate
        signals
        """
        pass

    @abstractmethod
    def openDataSource(self):
        """
        Used to connect to the data source for the first time
        In the case of a CSV, this means opening the file
        """
        pass

    @abstractmethod
    def getNextTick(self):
        """
        Used to get the next available piece of data from the data source
        For the CSV example, this would likely be the next row of the CSV
        """
        pass