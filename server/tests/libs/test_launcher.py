import unittest

from libs.launcher import Launcher
from libs.instance import Instance

class MockItem(object):
    def __init__(self, **kwargs):
        [setattr(self, k, kwargs[k]) for k in kwargs]

class LauncherTest(unittest.TestCase):

    def testInit(self):
        l = Launcher()
        methods = [method for method in dir(l) if callable(getattr(l, method))]
        expected = ['create', 'status', 'start', 'stop', 'delete', 'restart', '_generate_instances']
        for m in expected:
            self.assertIn(m, methods)

    def testNotImplemented(self):

        l = Launcher()
        methods = ['create', 'status', 'start', 'stop', 'delete', 'restart']
        for m in methods:
            with self.assertRaises(NotImplementedError):
                getattr(l, m)()

    def test_GenerateInstances(self):

        l = Launcher()

        items = [MockItem(id='derp'), MockItem(id='ello')]
        instances = l._generate_instances(items)

        self.assertEqual(len(instances), len(items))
        for i in instances:
            self.assertIn(i.id, ['derp', 'ello'])
            self.assertIsInstance(i, Instance)
