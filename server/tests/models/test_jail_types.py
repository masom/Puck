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
        jail_types = JailTypes()
        self.assertIsInstance(jail_types, ModelCollection)
        self.assertGreater(jail_types._items, 0)
        self.assertIsInstance(jail_types.all(), list)

        for i in jail_types.all():
            self.assertIsInstance(i, JailType)

    def testFirst(self):
        jail_types = JailTypes()
        first =  jail_types._items[0]
        self.assertEqual(jail_types.first(), first)

    def testNew(self):
        jail_types = JailTypes()
        self.assertIsInstance(jail_types.new(), JailType)

        e = jail_types.new(id="lol")
        self.assertEqual(e.id, 'lol')

    def testAdd(self):
        jail_types = JailTypes()
        before_count = len(jail_types.all())
        self.assertTrue(jail_types.add(jail_types.new()))
        after_count = len(jail_types.all())
        self.assertGreater(after_count, before_count)
        self.assertEqual(before_count + 1, after_count)

    def testDelete(self):
        pass

    def test_GenerateSelectQuery(self):
        jail_types = JailTypes()
        expected = 'SELECT * FROM jail_types'
        self.assertEqual(jail_types._generate_select_query(), expected)

    def test_InsertQuery(self):
        jail_types = JailTypes()
        entity = jail_types.new()

        expected = OrderedDict([('id', None), ('ip', None), ('netmask', None)])
        data = jail_types._generate_query_data(entity)
        self.assertEqual(expected, data)

        expected = 'INSERT INTO jail_types(id,ip,netmask) VALUES (?,?,?)'
        self.assertEqual(jail_types._generate_insert_query(data), expected)

    def testTableDefinition(self):
        jail_types = JailTypes()
        expected = 'CREATE TABLE jail_types (id TEXT PRIMARY KEY,ip TEXT,netmask TEXT)'
        self.assertEqual(str(jail_types.table_definition()), expected)

    def testDelete(self):
        jail_types = JailTypes()
        entity = jail_types.new()

        expected = 'DELETE FROM jail_types WHERE id = ?'
        self.assertEqual(jail_types._generate_delete_query(entity.id), expected)

