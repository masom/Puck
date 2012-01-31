import unittest

from controllers.api import *

class ApiTest(unittest.TestCase):
    def testInit(self):
        api = Api(None)
        attrs = [
            'registration', 'keys', 'status', 'config', 'environments',
            'jails', 'yum_repo'
        ]
        for a in attrs:
            self.assertTrue(hasattr(api, a))

class ApiRegistrationTest(unittest.TestCase):
    def testInit(self):
        ar = ApiRegistration()
        vm = ar.POST()
        self.assertIsInstance(vm, dict)

