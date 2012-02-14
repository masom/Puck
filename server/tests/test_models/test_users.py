import unittest
from collections import OrderedDict
from models.users import User, Users
from libs.model import ModelCollection, Model
class UserTest(unittest.TestCase):

    def testInit(self):
        e = User(name="test", password='derp')
        for a in ['name', 'password']:
            self.assertTrue(hasattr(e, a))
        self.assertEqual('test', e.name)
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
        users.add(entity, persist=False)
        self.assertEqual(users.first(), entity)

    def testNew(self):
        users = Users()
        self.assertIsInstance(users.new(), User)

        e = users.new(name="lol")
        self.assertEqual(e.name, 'lol')

    def testAdd(self):
        users = Users()
        before_count = len(users.all())
        self.assertTrue(users.add(users.new(), persist=False))
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

        expected = OrderedDict([
            ('id', None), ('user_group', 'user'), ('username', None),
            ('name', None), ('email', None), ('password', None),
            ('virt_auth_data', None)
        ])
        data = users._generate_query_data(entity)
        self.assertEqual(expected, data)

        expected = 'INSERT INTO users(id,user_group,username,name,email,password,virt_auth_data) VALUES (?,?,?,?,?,?,?)'
        self.assertEqual(users._generate_insert_query(data), expected)

    def testTableDefinition(self):
        users = Users()
        expected = 'CREATE TABLE users (id TEXT PRIMARY KEY,user_group TEXT,username TEXT,name TEXT,email TEXT,password TEXT,virt_auth_data TEXT)'
        self.assertEqual(str(users.table_definition()), expected)

    def testDelete(self):
        users = Users()
        entity = users.new()

        expected = 'DELETE FROM users WHERE id = ?'
        self.assertEqual(users._generate_delete_query(entity.name), expected)



