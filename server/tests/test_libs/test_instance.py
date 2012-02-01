import unittest

from libs.instance import Instance

class InstanceTest(unittest.TestCase):
    def testInit(self):
        i = Instance()
        attrs = ['id', 'backend', 'launch_time', 'ip', 'state']
        for a in attrs:
            self.assertTrue(hasattr(i, a))
            self.assertEqual(getattr(i, a), None)

        i = Instance(id='test', launch_time='now')
        self.assertEqual(i.id, 'test')
        self.assertEqual(i.launch_time, 'now')

