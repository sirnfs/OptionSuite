import datetime
import unittest
from base import option

class TestOptionsClass(unittest.TestCase):

  def testOptionClassCreation(self):
    """Tests than an exception is raised when class is instantiated."""
    with self.assertRaisesRegex(TypeError, "Cannot instantiate abstract class."):
      option.Option(underlyingTicker='SPY', strikePrice=250, delta=0.3, expirationDateTime=datetime.datetime.now())

if __name__ == '__main__':
    unittest.main()
