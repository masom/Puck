import unittest
from collections import OrderedDict
from models.users import User, Users
from libs.model import ModelCollection, Model
class UserTest(unittest.TestCase):

    def testInit(self):
        e = User(name="test", key="asdf", password='derp')
        for a in ['name', 'key', 'password']:
            self.assertTrue(hasattr(e, a))
        self.assertEqual('test', e.name)
        self.assertEqual('asdf', e.key)
        self.assertEqual('derp', e.password)
        self.assertFalse(hasattr(e, 'derp'))
        self.assertIsInstance(e, Model)

class UsersTest(unittest.TestCase):
    def testInit(self):
        users = Users()
        self.assertIsInstance(users, ModelCollection)
        self.assertGreater(users._items, 0)
        self.assertIsInstance(users.all(), list)

        for i in users.all():
            self.assertIsInstance(i, User)

    def testFirst(self):
        users = Users()
        self.assertEqual(users.first(), None)
        entity = users.new()
        users.add(entity)
        self.assertEqual(users.first(), entity)

    def testNew(self):
        users = Users()
        self.assertIsInstance(users.new(), User)

        e = users.new(name="lol")
        self.assertEqual(e.name, 'lol')

    def testAdd(self):
        users = Users()
        before_count = len(users.all())
        self.assertTrue(users.add(users.new()))
        after_count = len(users.all())
        self.assertGreater(after_count, before_count)
        self.assertEqual(before_count + 1, after_count)

    def testDelete(self):
        pass

    def test_GenerateSelectQuery(self):
        users = Users()
        expected = 'SELECT * FROM users'
        self.assertEqual(users._generate_select_query(), expected)

    def test_InsertQuery(self):
        users = Users()
        entity = users.new()

        expected = OrderedDict([('name', None), ('password', None),('key', None)])
        data = users._generate_query_data(entity)
        self.assertEqual(expected, data)

        expected = 'INSERT INTO users(name,password,key) VALUES (?,?,?)'
        self.assertEqual(users._generate_insert_query(data), expected)

    def testTableDefinition(self):
        users = Users()
        expected = 'CREATE TABLE users (name TEXT PRIMARY KEY,password TEXT,key TEXT)'
        self.assertEqual(str(users.table_definition()), expected)

    def testDelete(self):
        users = Users()
        entity = users.new()

        expected = 'DELETE FROM users WHERE name = ?'
        self.assertEqual(users._generate_delete_query(entity.name), expected)



