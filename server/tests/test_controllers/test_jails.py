import unittest

from controllers.jails import Jails
from libs.controller import Controller
from tests.base import PuckTestCase
class JailsControllerTest(PuckTestCase):
    def testInit(self):
        j = Jails(None)
        self.assertIsInstance(j, Controller)

