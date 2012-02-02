import unittest

from collections import OrderedDict
from libs.model import ModelCollection, Model, Migration, TableDefinition

class MockCollection(object):
    def __init__(self, columns = []):
        self.columns = OrderedDict()
        for c in columns:
            self.columns[c] = None

    def table_definition(self):
        return self

class MockModel(Model):
    def __init__(self, **kwargs):
        for i in kwargs:
            setattr(self, i, kwargs[i])

class ModelCollectionNoExecQuery(ModelCollection):
    def _execute_query(self, query, data):
        return True

class ModelTest(unittest.TestCase):
    def testToDict(self):
        e = MockModel(id="test", name="test")
        e._collection = MockCollection(['id', 'name'])
        data = e.to_dict()
        expected = {'id': 'test', 'name': 'test'}
        self.assertEqual(data,expected)

class ModelCollectionTest(unittest.TestCase):
    def testInit(self):
        mc = ModelCollection()
        self.assertIsNone(mc._model)
        self.assertIsNone(mc._table_name)
        self.assertIsNone(mc._table_definition)

    def test_MockModel(self):
        entity = MockModel(name="ent")
        self.assertTrue(hasattr(entity, "name"))

    def test_AfterInit(self):
        mc = ModelCollection()
        mc._after_init()

    def test_BeforeAdd(self):
        mc = ModelCollection()
        self.assertTrue(mc._before_add(None))

    def testTableDefinition(self):
        mc = ModelCollection()
        self.assertIsNone(mc._table_definition)
        self.assertIsNone(mc.table_definition())

    def test_GenerateTableDefinition(self):
        mc = ModelCollection()
        self.assertIsNone(mc._generate_table_definition())

    def testAll(self):
        mc = ModelCollection()
        self.assertEqual(mc.all(), [])

    def test_FindMatch(self):
        mc = ModelCollection()
        item = MockModel(name="derp")
        self.assertTrue(mc._find_match(item, "name", "derp"))

        item = MockModel(ello="World")
        self.assertFalse(mc._find_match(item, "name", "derp"))
        self.assertTrue(mc._find_match(item, "ello", "World"))

    def test_Find(self):
        mc = ModelCollection()
        item = MockModel(name="world", ip="local")
        self.assertTrue(mc._find(item, {'name': 'world'}))
        self.assertTrue(mc._find(item, {'name': 'world', 'ip': 'local'}))
        self.assertTrue(mc._find(item, {'ip': 'local'}))
        self.assertFalse(mc._find(item, {'name': 'Chocolate', 'ip': 'local'}))
        self.assertFalse(mc._find(item, {'echo': 'Nope'}))
        self.assertTrue(mc._find(item, {}))

    def testFind(self):
        mc = ModelCollection()
        self.assertEqual(mc.find(name="derp"), [])

        expected = [MockModel(name="test")]
        mc._items = expected
        self.assertEqual(mc.find(name="test"), expected)
        self.assertEqual(mc.find(name="civic"), [])

        items = [MockModel(name="ello"), MockModel(name="ello", ip="world")]
        mc._items = items
        expected = [items[1]]
        self.assertEqual(mc.find(ip="world"), expected)
        self.assertEqual(mc.find(name="ello", ip="world"), expected)

    def testFirst(self):
        mc = ModelCollection()

        self.assertIsNone(mc.first())
        self.assertIsNone(mc.first(name="test"))

        items = [MockModel(name="ello"), MockModel(name="ello")]
        mc._items = items
        self.assertEqual(mc.first(), items[0])
        self.assertIsNone(mc.first(outlook="thunderbird"))
        self.assertEqual(mc.first(name="ello"), items[0])

    def testNew(self):
        mc = ModelCollection()

        with self.assertRaises(TypeError):
            mc.new()

        mc._model = MockModel
        self.assertIsInstance(mc.new(), MockModel)

    def testAdd(self):
        mc = ModelCollection()

        entity = MockModel()
        mc._before_add = lambda x: False
        self.assertFalse(mc.add(entity, persist=False))

        mc._before_add = lambda x: True
        self.assertTrue(mc.add(entity, persist=False))
        self.assertEqual(mc._items, [entity])

    def testDelete(self):
        pass

    def test_Build(self):
        mc = ModelCollection()
        items = [{'name':"hello"}, {'name':"world"}]

        with self.assertRaises(TypeError):
            mc._build(items)
        mc._model = MockModel
        entities = mc._build(items)

        for entity in entities:
            self.assertTrue(hasattr(entity, 'name'))
            self.assertTrue(entity.name in ['hello', 'world'])

    def test_GenerateQueryData(self):
        mc = ModelCollection()
        mc._table_name = 'test'
        mc._table_definition = TableDefinition('test', {'id': 'TEXT', 'name': 'TEXT'})

        entity = MockModel(id='test')
        expected = OrderedDict()
        expected['id'] = 'test'
        data = mc._generate_query_data(entity)
        self.assertEqual(data, expected)

        entity = MockModel(id='test', bad_column='trololol')
        expected = OrderedDict()
        expected['id'] = 'test'
        data = mc._generate_query_data(entity)
        self.assertEqual(data, expected)

        entity = MockModel(id='test', bad_column='trololol', name='ello')
        expected = OrderedDict()
        expected['id'] = 'test'
        expected['name'] = 'ello'
        data = mc._generate_query_data(entity)
        self.assertEqual(data, expected)

        # Whitelist test
        entity = MockModel(id='test', bad_column='trololol', name='ello')
        expected = OrderedDict()
        expected['name'] = 'ello'
        data = mc._generate_query_data(entity, ['name'])
        self.assertEqual(data, expected)

    def test_GenerateSelectQuery(self):
        mc = ModelCollection()
        mc._table_name = 'test'
        mc._table_definition = TableDefinition('test', {'id': 'TEXT', 'name': 'TEXT'})
        query = mc._generate_select_query()
        expected = 'SELECT * FROM test'
        self.assertEqual(query, expected)

    def test_GenerateInsertQuery(self):
        mc = ModelCollection()
        mc._table_name = 'test'
        mc._table_definition = TableDefinition('test', {'id': 'TEXT', 'name': 'TEXT'})
        insert_data = {'id': 'derp', 'name': 'ello'}
        query = mc._generate_insert_query(insert_data)
        expected = 'INSERT INTO test(id,name) VALUES (?,?)'
        self.assertEqual(query, expected)

    def test_GenerateUpdateQuery(self):
        mc = ModelCollection()
        mc._table_name = 'test'
        mc._table_definition = TableDefinition('test', {'id': 'TEXT', 'name': 'TEXT'})

        update_data = {'id': 'lol', 'name': 'ello'}
        query = mc._generate_update_query(['lol'], update_data)
        expected = 'UPDATE test SET name = ? WHERE id IN (?)'
        self.assertEqual(query, expected)

        query = mc._generate_update_query(['lol', 'ello', 'derp'], update_data)
        expected = 'UPDATE test SET name = ? WHERE id IN (?,?,?)'
        self.assertEqual(query, expected)

        update_data = {'id': 'lol', 'name': 'ello', 'desc': 'Nope'}
        query = mc._generate_update_query(['lol'], update_data)
        expected = 'UPDATE test SET desc = ?,name = ? WHERE id IN (?)'
        self.assertEqual(query, expected)

    def test_GenerateDeleteQuery(self):
        mc = ModelCollection()
        mc._table_name = 'test'
        mc._table_definition = TableDefinition('test', {'id': 'TEXT', 'name': 'TEXT'})

        query = mc._generate_delete_query(['lol'])
        expected = 'DELETE FROM test WHERE id = ?'
        self.assertEqual(query, expected)


    def testUpdate(self):
        mc = ModelCollectionNoExecQuery()
        mc._table_name = 'test'
        mc._table_definition = TableDefinition('test', {'id': 'TEXT', 'name': 'TEXT'})

        entity = MockModel(id='test', name='lol')
        self.assertTrue(mc.update(entity, ['name']))
        self.assertFalse(mc.update(entity, ['id']))
        self.assertTrue(mc.update(entity, ['name', 'id']))

    def test_Insert(self):
        mc = ModelCollectionNoExecQuery()
        mc._table_name = 'test'
        mc._table_definition = TableDefinition('test', {'id': 'TEXT', 'name': 'TEXT'})

        entity = MockModel(id='test', name='lol')
        self.assertTrue(mc._insert(entity))
        self.assertIsNotNone(entity.id)

        entity = MockModel()
        self.assertFalse(mc._insert(entity))

    def test_Delete(self):
        mc = ModelCollectionNoExecQuery()
        mc._table_name = 'test'
        mc._table_definition = TableDefinition('test', {'id': 'TEXT', 'name': 'TEXT'})

        entity = MockModel(id='ello')
        self.assertTrue(mc._delete(entity))
        self.assertFalse(mc._delete(MockModel()))
        self.assertFalse(mc._delete(MockModel(name="derp")))

class MigrationTest(unittest.TestCase):
    def testInit(self):
        m = Migration(None, [])
        attrs = ['_connection', '_tables']
        for a in attrs:
            self.assertTrue(hasattr(m, a))

class TableDefinitionTest(unittest.TestCase):
    def testInit(self):
        with self.assertRaises(KeyError):
            TableDefinition("tests", {})

        td = TableDefinition("tests", {'id': 'INTEGER'})
        attrs = ['primary_key', 'name', 'columns', '_string']
        for a in attrs:
            self.assertTrue(hasattr(td, a))

        expected = "CREATE TABLE tests (id INTEGER PRIMARY KEY)"
        self.assertEqual(td._string, expected)

        td = TableDefinition("tests", {'id': 'integer'})
        expected = "CREATE TABLE tests (id integer PRIMARY KEY)"
        self.assertEqual(td._string, expected)

        td = TableDefinition("tests", {'id': 'integer PRIMARY KEY'})
        expected = "CREATE TABLE tests (id integer PRIMARY KEY)"
        self.assertEqual(td._string, expected)

        td = TableDefinition("tests", {'id': 'integer', 'name': 'TEXT'})
        expected = "CREATE TABLE tests (id integer PRIMARY KEY,name TEXT)"
        self.assertEqual(td._string, expected)
        self.assertEqual("%s" % td, expected)
