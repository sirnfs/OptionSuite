from event import EventHandler

class TickEvent(EventHandler):
    """This class handles manages the events for new incoming data
    whether it be from historical data or a new tick from a live trading
    session
    """

    def __init__(self):
        self.__data = None

    def getData(self):
        return self.__data

    def createEvent(self, data):
        """
        Attributes:
            data: input data for the event. e.g., row of CSV data
            
        Create a data tick event
        TODO!!!
        Need to determine what the incoming data represents -- is it
        a stock tick, an option tick (put, call), etc.
        Call data handler to take care of this
        """
        self.__data = data

    def deleteEvent(self):
        """
        Delete an event from one of the data handlers
        """
        pass
