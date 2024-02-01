from events import event
from typing import Any, Iterable

class TickEvent(event.EventHandler):
  """This class handles the events for new incoming data whether it be from historical data or from live trading."""

  def __init__(self) -> None:
    self.__data = None
    self.type = event.EventTypes.TICK

  def getData(self) -> Iterable[Any]:
    return self.__data

  def createEvent(self, data: Iterable[Any]) -> None:
    """Create a tick event.
      Attributes:
        data: input data for the event. e.g., row of CSV data.
    """
    self.__data = data