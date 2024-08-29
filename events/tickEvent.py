from events import event
from typing import Any, Iterable


class TickEvent(event.EventHandler):
    """This class handles the events for new incoming data."""

    def __init__(self) -> None:
        self.__data = None
        self.type = event.EventTypes.TICK

    def getData(self) -> Iterable[Any]:
        return self.__data

    def createEvent(self, data: Iterable[Any]) -> None:
        """Creates a tick event.

          Attributes:
            data: input data for the event. e.g., a row of CSV data.
        """
        self.__data = data
