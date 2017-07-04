from event import EventHandler

class SignalEvent(EventHandler):
    """This class handles manages the events for signals generated off of incoming data;
    E.g. -- if the input data results in a sell strangle event, a SignalEvent will be created
    """

    def __init__(self):
        self.__data = None
        self.type = 'SIGNAL'

    def getData(self):
        return self.__data

    def createEvent(self, data):
        """
        Attributes:
            data: input data for the event. e.g., row of CSV data or buy/sell info for signal event
        """
        self.__data = data

    def deleteEvent(self):
        """
        Delete an event
        """
        pass
