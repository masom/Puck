import unittest

from controllers.jail_types import JailTypesController
from libs.controller import Controller
from tests.base import PuckTestCase

class JailTypesControllerTest(PuckTestCase):
    def testInit(self):
        j = JailTypesController(None)
        self.assertIsInstance(j, Controller)
        j.render = dict
        
    
    def testAdd(self):
        