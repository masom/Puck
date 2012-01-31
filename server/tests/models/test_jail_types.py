import unittest
from collections import OrderedDict
from models.jail_types import JailType, JailTypes
from libs.model import ModelCollection, Model
class JailTypeTest(unittest.TestCase):

    def testInit(self):
        e = JailType(id="test", ip="127.0.0.1", netmask='255.255.255.0')
        for a in ['id', 'ip', 'netmask']:
            self.assertTrue(hasattr(e, a))
        self.assertEqual('test', e.id)
        self.assertEqual('127.0.0.1', e.ip)
        self.assertFalse(hasattr(e, 'derp'))
        self.assertIsInstance(e, Model)

class JailTypesTest(unittest.TestCase):
    def testInit(self):
        envs = JailTypes()
        self.assertIsInstance(envs, ModelCollection)
        self.assertGreater(envs._items, 0)
        self.assertIsInstance(envs.all(), list)

        for i in envs.all():
            self.assertIsInstance(i, JailType)

    def testFirst(self):
        envs = JailTypes()
        first =  envs._items[0]
        self.assertEqual(envs.first(), first)

    def testNew(self):
        envs = JailTypes()
        self.assertIsInstance(envs.new(), JailType)

        e = envs.new(id="lol")
        self.assertEqual(e.id, 'lol')

    def testAdd(self):
        envs = JailTypes()
        before_count = len(envs.all())
        self.assertTrue(envs.add(envs.new()))
        after_count = len(envs.all())
        self.assertGreater(after_count, before_count)
        self.assertEqual(before_count + 1, after_count)

    def testDelete(self):
        pass

    def test_GenerateSelectQuery(self):
        envs = JailTypes()
        expected = 'SELECT * FROM jail_types'
        self.assertEqual(envs._generate_select_query(), expected)

    def test_InsertQuery(self):
        envs = JailTypes()
        entity = envs.new()

        expected = OrderedDict([('id', None), ('ip', None), ('netmask', None)])
        data = envs._generate_query_data(entity)
        self.assertEqual(expected, data)

        expected = 'INSERT INTO jail_types(id,ip,netmask) VALUES (?,?,?)'
        self.assertEqual(envs._generate_insert_query(data), expected)

    def testTableDefinition(self):
        envs = JailTypes()
        expected = 'CREATE TABLE jail_types (id TEXT PRIMARY KEY,ip TEXT,netmask TEXT)'
        self.assertEqual(str(envs.table_definition()), expected)

    def testDelete(self):
        envs = JailTypes()
        entity = envs.new()

        expected = 'DELETE FROM jail_types WHERE id = ?'
        self.assertEqual(envs._generate_delete_query(entity.id), expected)

