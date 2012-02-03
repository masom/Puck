import unittest
from libs.controller import Controller
class ControllerTest(unittest.TestCase):
    def testInit(self):
        c = Controller(None)
        self.assertTrue(hasattr(c, '_lookup'))
        self.assertIsNone(getattr(c, '_lookup'))
