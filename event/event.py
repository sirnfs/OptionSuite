from abc import ABCMeta, abstractmethod

class EventHandler(object):
    """This class is a generic type for handling all events for the
    backtester and for live trading
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def createEvent(self, data):
        """
        Attributes:
            data: input data for the event. e.g., row of CSV data
            
        Create an event which will be used for later processing
        e.g., create a data tick event for a row which was just
        read from the CSV handler
        """
        pass

    @abstractmethod
    def deleteEvent(self):
        """
        Delete an event 
        e.g., delete a data tick event from the CSV handler
        """
        pass



 #Check if queue is empty
 #       self.assertEqual(self.eventQ.empty(), True)