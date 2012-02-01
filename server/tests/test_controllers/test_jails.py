import unittest

from controllers.jails import Jails
from libs.controller import Controller

class JailsControllerTest(unittest.TestCase):
    def testInit(self):
        j = Jails(None)
        self.assertIsInstance(j, Controller)

