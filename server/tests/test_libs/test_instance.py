import unittest

from libs.instance import Instance

class InstanceTest(unittest.TestCase):
    def testInit(self):
        i = Instance()
        attrs = ['id', 'backend', 'name', 'addresses', 'status']
        for a in attrs:
            self.assertTrue(hasattr(i, a))
            self.assertEqual(getattr(i, a), None)

        i = Instance(id='test', status='now')
        self.assertEqual(i.id, 'test')
        self.assertEqual(i.status, 'now')

