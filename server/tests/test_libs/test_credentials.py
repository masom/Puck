import unittest
import json
from libs.credentials import Credentials

class CredentialsTest(unittest.TestCase):
    def testInit(self):
        c = Credentials()
        attrs = ['name', 'email', '_data']
        for a in attrs:
            self.assertTrue(hasattr(c, a))
        attrs = ['name', 'email']
        for a in attrs:
            self.assertIsNone(getattr(c, a))

    def testLoad(self):
        c = Credentials()
        data = {'name': 'Test', 'email': 'Test'}
        bindata = json.dumps(data)
        c._load_data(bindata)
        self.assertEqual(c._data, data)
