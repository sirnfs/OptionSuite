import unittest
import tickEvent

class TestTickEvent(unittest.TestCase):
    """
    To test the tick event creation, we will test that event
    creation works, and that the type of the event is correct.
    """

    def testCreateTickEvent(self):

        # Create tick event.
        tickObj = tickEvent.TickEvent()

        # Check that the data reference attribute is set to None.
        self.assertEqual(tickObj.getData(), None)

        # Check that right type is set.
        self.assertEqual(tickObj.type, 'TICK')

if __name__ == '__main__':
    unittest.main()
