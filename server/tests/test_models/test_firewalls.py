import unittest
from collections import OrderedDict
from models.firewalls import Firewall, Firewalls
from libs.model import ModelCollection, Model
class FirewallTest(unittest.TestCase):

    def testInit(self):
        e = Firewall(name="test", data='derp')
        for a in ['name', 'data']:
            self.assertTrue(hasattr(e, a))
        self.assertEqual('test', e.name)
        self.assertEqual('derp', e.data)
        self.assertFalse(hasattr(e, 'derp'))
        self.assertIsInstance(e, Model)

class FirewallsTest(unittest.TestCase):
    def testInit(self):
        firewalls = Firewalls()
        self.assertIsInstance(firewalls, ModelCollection)
        self.assertGreater(firewalls._items, 0)
        self.assertIsInstance(firewalls.all(), list)

        for i in firewalls.all():
            self.assertIsInstance(i, Firewall)

    def testFirst(self):
        firewalls = Firewalls()
        self.assertEqual(firewalls.first(), None)
        entity = firewalls.new()
        firewalls.add(entity, persist=False)
        self.assertEqual(firewalls.first(), entity)

    def testNew(self):
        firewalls = Firewalls()
        self.assertIsInstance(firewalls.new(), Firewall)

        e = firewalls.new(name="lol")
        self.assertEqual(e.name, 'lol')

    def testAdd(self):
        firewalls = Firewalls()
        before_count = len(firewalls.all())
        self.assertTrue(firewalls.add(firewalls.new(), persist=False))
        after_count = len(firewalls.all())
        self.assertGreater(after_count, before_count)
        self.assertEqual(before_count + 1, after_count)

    def testDelete(self):
        pass

    def test_GenerateSelectQuery(self):
        firewalls = Firewalls()
        expected = 'SELECT * FROM firewalls'
        self.assertEqual(firewalls._generate_select_query(), expected)

    def test_InsertQuery(self):
        firewalls = Firewalls()
        entity = firewalls.new()

        expected = OrderedDict([
            ('id', None), ('name', None), ('data', None)
        ])
        data = firewalls._generate_query_data(entity)
        self.assertEqual(expected, data)

        expected = 'INSERT INTO firewalls(id,name,data) VALUES (?,?,?)'
        self.assertEqual(firewalls._generate_insert_query(data), expected)

    def testTableDefinition(self):
        firewalls = Firewalls()
        expected = 'CREATE TABLE firewalls (id TEXT PRIMARY KEY,name TEXT,data TEXT)'
        self.assertEqual(str(firewalls.table_definition()), expected)

    def testDelete(self):
        firewalls = Firewalls()
        entity = firewalls.new()

        expected = 'DELETE FROM firewalls WHERE id = ?'
        self.assertEqual(firewalls._generate_delete_query(entity.name), expected)




