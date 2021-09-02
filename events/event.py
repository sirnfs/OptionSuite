import abc
import enum

class EventTypes(enum.Enum):
  TICK = 0
  SIGNAL = 1

class EventHandler(abc.ABC):
  """This class is a generic type for handling all events for the backtester and for live trading."""

  @abc.abstractmethod
  def createEvent(self, data) -> None:
    """Create an event which will be used for later processing e.g., create a data tick event for an option chain read
    from the CSV data handler.
    Attributes:
        data: input data for the event. e.g., option chain.
    """
    pass