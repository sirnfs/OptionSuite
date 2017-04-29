import unittest
import option

class TestOptionsClass(unittest.TestCase):
    def testOptionClassCreation(self):

        #Below we test if an exception is thrown when try to instantiate the class
        #We should not be able to instantitate the Option class
        failed = False
        try:
            classObj = option.Option('SPY', 250, 'PUT', 0.3, 45)
        except NotImplementedError:
            failed = True

        #This should pass if an exception is raised above
        self.assertEqual(failed, True)

if __name__ == '__main__':
    unittest.main()
