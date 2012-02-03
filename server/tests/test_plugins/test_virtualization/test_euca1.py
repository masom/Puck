import unittest

import pickle
from plugins.virtualization.euca1 import EucaCredentials, Euca1
class EucaCredentialsTest(unittest.TestCase):
    def testInit(self):
        ec = EucaCredentials()
        attrs = ['name', 'email', 'password', '_data']
        for a in attrs:
            self.assertTrue(hasattr(ec,a))

        data = {'ec2_url': 'http://google.ca'}
        ec = EucaCredentials(data=pickle.dumps(data))
        self.assertTrue(hasattr(ec, 'ec2_url'))
        self.assertEqual(ec._data, data)
        self.assertEqual(ec.ec2_url, data['ec2_url'])

        ec = EucaCredentials()
        params = ['ec2_url', 's3_url', 'ec2_user_access_key',
            'ec2_user_secret_key', 'ec2_cert', 'ec2_private_key',
            'eucalyptus_cert', 'ec2_user_id'
        ]
        for a in params:
            self.assertTrue(hasattr(ec, a))
            self.assertEqual(getattr(ec,a), None)

        data = dict((a, 'test') for a in params)
        ec = EucaCredentials(data=pickle.dumps(data))
        for a in params:
            self.assertTrue(hasattr(ec, a))
            self.assertEqual(getattr(ec, a), 'test')


