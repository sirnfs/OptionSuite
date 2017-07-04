import unittest
import signalEvent

class TestSignalEvent(unittest.TestCase):
    """
    To test the signal event creation, we will test that event
    creation works, and that the type of the event is correct
    """

    def testCreateSignalEvent(self):

        #Create signal event
        signalObj = signalEvent.SignalEvent()

        #Check that the data reference attribute is set to none
        self.assertEqual(signalObj.getData(), None)

        #Check that right type is set
        self.assertEqual(signalObj.type, 'SIGNAL')

if __name__ == '__main__':
    unittest.main()
