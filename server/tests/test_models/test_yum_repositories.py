import unittest
from collections import OrderedDict
from models.yum_repositories import YumRepository, YumRepositories
from libs.model import ModelCollection, Model
class YumRepositoryTest(unittest.TestCase):

    def testInit(self):
        e = YumRepository(environment="test", data='lol')
        for a in ['environment', 'data']:
            self.assertTrue(hasattr(e, a))
        self.assertEqual('test', e.environment)
        self.assertEqual('lol', e.data)
        self.assertFalse(hasattr(e, 'derp'))
        self.assertIsInstance(e, Model)

class YumRepositoriesTest(unittest.TestCase):
    def testInit(self):
        yr = YumRepositories()
        self.assertIsInstance(yr, ModelCollection)
        self.assertGreater(yr._items, 0)
        self.assertIsInstance(yr.all(), list)

        for i in yr.all():
            self.assertIsInstance(i, YumRepository)

    def testFirst(self):
        yr = YumRepositories()
        self.assertEqual(yr.first(), None)
        entity = yr.new()
        yr.add(entity)
        self.assertEqual(yr.first(), entity)

    def testNew(self):
        yr = YumRepositories()
        self.assertIsInstance(yr.new(), YumRepository)

        e = yr.new(environment="lol")
        self.assertEqual(e.environment, 'lol')
        self.assertEqual(e.data, None)

    def testAdd(self):
        yr = YumRepositories()
        before_count = len(yr.all())
        self.assertTrue(yr.add(yr.new()))
        after_count = len(yr.all())
        self.assertGreater(after_count, before_count)
        self.assertEqual(before_count + 1, after_count)

    def testDelete(self):
        pass

    def test_GenerateSelectQuery(self):
        yr = YumRepositories()
        expected = 'SELECT * FROM yum_repositories'
        self.assertEqual(yr._generate_select_query(), expected)

    def test_InsertQuery(self):
        yr = YumRepositories()
        entity = yr.new()
        expected = OrderedDict([('environment', None), ('data', None)])
        data = yr._generate_query_data(entity)
        self.assertEqual(expected, data)

        expected = 'INSERT INTO yum_repositories(environment,data) VALUES (?,?)'
        self.assertEqual(yr._generate_insert_query(data), expected)

    def testTableDefinition(self):
        yr = YumRepositories()
        expected = 'CREATE TABLE yum_repositories (environment TEXT PRIMARY KEY,data TEXT)'
        self.assertEqual(str(yr.table_definition()), expected)

    def testDelete(self):
        yr = YumRepositories()
        entity = yr.new()

        expected = 'DELETE FROM yum_repositories WHERE environment = ?'
        self.assertEqual(yr._generate_delete_query(entity.environment), expected)


