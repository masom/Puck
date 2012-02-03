import unittest

from controllers.jails import JailsController
from libs.controller import Controller
from tests.base import PuckTestCase
class JailsControllerTest(PuckTestCase):
    def testInit(self):
        j = JailsController(None)
        self.assertIsInstance(j, Controller)

