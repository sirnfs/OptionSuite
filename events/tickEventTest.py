import unittest
from events import event
from events import tickEvent

class TestTickEvent(unittest.TestCase):

  def testCreateTickEvent(self):
    """Tests that a signal event is successfully created."""
    tickObj = tickEvent.TickEvent()
    # Check that the data reference attribute is set to None since there has been no data passed.
    self.assertEqual(tickObj.getData(), None)
    self.assertEqual(tickObj.type, event.EventTypes.TICK)

if __name__ == '__main__':
    unittest.main()
