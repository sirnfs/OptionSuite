import abc

class DataHandler(abc.ABC):
  """This class is a generic type for handling incoming data. Incoming data sources could be historical data in the
  form of a CSV or a database, or it could be live tick data coming from an exchange."""

  @abc.abstractmethod
  def getNextTick(self) -> bool:
    """Used to get the next available piece of data from the data source. For the CSV example, this would likely be the
    next row of the CSV.
    :return True / False indicating if data is available.
    """
    pass