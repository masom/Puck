import unittest
from collections import OrderedDict
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
        self.assertIsNone(envs.first())

        envs.add(envs.new(), persist=False)
        first =  envs._items[0]
        self.assertEqual(envs.first(), first)

    def testNew(self):
        envs = Environments()
        self.assertIsInstance(envs.new(), Environment)

        e = envs.new(id="lol")
        self.assertEqual(e.id, 'lol')

    def testAdd(self):
        envs = Environments()
        before_count = len(envs.all())
        self.assertTrue(envs.add(envs.new(), persist=False))
        after_count = len(envs.all())
        self.assertGreater(after_count, before_count)
        self.assertEqual(before_count + 1, after_count)

    def testDelete(self):
        pass

    def test_GenerateSelectQuery(self):
        envs = Environments()
        expected = 'SELECT * FROM environments'
        self.assertEqual(envs._generate_select_query(), expected)

    def test_InsertQuery(self):
        envs = Environments()
        entity = envs.new()

        expected = OrderedDict([('id', None), ('code', None), ('name', None)])
        data = envs._generate_query_data(entity)
        self.assertEqual(expected, data)

        expected = 'INSERT INTO environments(id,code,name) VALUES (?,?,?)'
        self.assertEqual(envs._generate_insert_query(data), expected)

    def testTableDefinition(self):
        envs = Environments()
        expected = 'CREATE TABLE environments (id TEXT PRIMARY KEY,code TEXT,name TEXT)'
        self.assertEqual(str(envs.table_definition()), expected)

    def testDelete(self):
        envs = Environments()
        entity = envs.new()

        expected = 'DELETE FROM environments WHERE id = ?'
        self.assertEqual(envs._generate_delete_query(entity.id), expected)
