import unittest

from models.environments import Environment, Environments
from libs.model import ModelCollection, Model
class EnvironmentTest(unittest.TestCase):

    def testInit(self):
        e = Environment(id="test", name="Test")
        for a in ['id', 'name']:
            self.assertTrue(hasattr(e, a))
        self.assertEqual('test', e.id)
        self.assertEqual('Test', e.name)
        self.assertFalse(hasattr(e, 'derp'))
        self.assertIsInstance(e, Model)

class EnvironmentsTest(unittest.TestCase):
    def testInit(self):
        envs = Environments()
        self.assertIsInstance(envs, ModelCollection)
        self.assertGreater(envs._items, 0)
        self.assertIsInstance(envs.all(), list)

        for i in envs.all():
            self.assertIsInstance(i, Environment)

    def testFirst(self):
        envs = Environments()
        first=  envs._items[0]
        self.assertEqual(envs.first(), first)

    def testNew(self):
        envs = Environments()
        self.assertIsInstance(envs.new(), Environment)

        e = envs.new(id="lol")
        self.assertEqual(e.id, 'lol')

    def testAdd(self):
        envs = Environments()
        before_count = len(envs.all())
        self.assertTrue(envs.add(envs.new()))
        after_count = len(envs.all())
        self.assertGreater(after_count, before_count)
        self.assertEqual(before_count + 1, after_count)

    def testDelete(self):
        pass
