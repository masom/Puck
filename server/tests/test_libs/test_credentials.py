import unittest
import pickle
from libs.credentials import Credentials

class CredentialsTest(unittest.TestCase):
    def testInit(self):
        c = Credentials()
        attrs = ['name', 'email', 'password', '_data']
        for a in attrs:
            self.assertTrue(hasattr(c, a))
        attrs = ['name', 'email', 'password']
        for a in attrs:
            self.assertIsNone(getattr(c, a))

    def testLoad(self):
        c = Credentials()
        data = {'name': 'Test', 'email': 'Test'}
        bindata = pickle.dumps(data)
        c._load_data(bindata)
        self.assertEqual(c._data, data)
