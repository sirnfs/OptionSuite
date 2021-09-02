import unittest
from events import event
from events import signalEvent

class TestSignalEvent(unittest.TestCase):

  def testCreateSignalEvent(self):
    """Tests that a signal event is successfully created."""
    signalObj = signalEvent.SignalEvent()
    # Check that the data reference attribute is set to None since there has been no data passed.
    self.assertEqual(signalObj.getData(), None)
    self.assertEqual(signalObj.type, event.EventTypes.SIGNAL)

if __name__ == '__main__':
    unittest.main()
