from events import event
from typing import Any, Iterable

class SignalEvent(event.EventHandler):
  """This class handles the events for signals to carry out on tick data."""

  def __init__(self) -> None:
    self.__data = None
    self.type = event.EventTypes.SIGNAL

  def getData(self) -> Iterable[Any]:
    return self.__data

  def createEvent(self, data: Iterable[Any]) -> None:
    """Create a signal event.
    Attributes:
        data: input data for the event.
    """
    self.__data = data
