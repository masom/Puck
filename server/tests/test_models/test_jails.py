import unittest
from collections import OrderedDict
from models.jails import Jail, Jails

from libs.model import ModelCollection, Model

class JailTest(unittest.TestCase):

    def testInit(self):
        e = Jail(id="test",jail_type='omg', name='jail', ip="127.0.0.1", netmask='255.255.255.0', environment='lol')
        for a in ['id', 'jail_type', 'name', 'ip', 'netmask', 'environment', 'url']:
            self.assertTrue(hasattr(e, a))
        self.assertEqual('test', e.id)
        self.assertEqual('omg', e.jail_type)
        self.assertEqual('jail', e.name)
        self.assertEqual('127.0.0.1', e.ip)
        self.assertEqual('255.255.255.0', e.netmask)
        self.assertEqual('lol', e.environment)
        self.assertFalse(hasattr(e, 'derp'))
        self.assertIsInstance(e, Model)

class JailsTest(unittest.TestCase):
    def testInit(self):
        jails = Jails()
        self.assertIsInstance(jails, ModelCollection)
        self.assertGreater(jails._items, 0)
        self.assertIsInstance(jails.all(), list)

        for i in jails.all():
            self.assertIsInstance(i, Jail)

    def testFirst(self):
        jails = Jails()
        self.assertEqual(jails.first(), None)
        entity = jails.new()
        jails.add(entity, persist=False)
        self.assertEqual(jails.first(), entity)

    def testNew(self):
        jails = Jails()
        self.assertIsInstance(jails.new(), Jail)

        e = jails.new(id="lol")
        self.assertEqual(e.id, 'lol')

    def testAdd(self):
        jails = Jails()
        before_count = len(jails.all())
        self.assertTrue(jails.add(jails.new(), persist=False))
        after_count = len(jails.all())
        self.assertGreater(after_count, before_count)
        self.assertEqual(before_count + 1, after_count)

    def testDelete(self):
        pass

    def test_GenerateSelectQuery(self):
        jails = Jails()
        expected = 'SELECT * FROM jails'
        self.assertEqual(jails._generate_select_query(), expected)

    def test_InsertQuery(self):
        jails = Jails()
        entity = jails.new()

        expected = OrderedDict([
            ('id', None), ('jail_type', None), ('name', None),
            ('ip', None), ('netmask', None), ('environment', None), ('url', None)
        ])
        data = jails._generate_query_data(entity)
        self.assertEqual(expected, data)

        expected = 'INSERT INTO jails(id,jail_type,name,ip,netmask,environment,url) VALUES (?,?,?,?,?,?,?)'
        self.assertEqual(jails._generate_insert_query(data), expected)

    def testTableDefinition(self):
        jails = Jails()
        expected = 'CREATE TABLE jails (id TEXT PRIMARY KEY,jail_type TEXT,name TEXT,ip TEXT,netmask TEXT,environment TEXT,url TEXT)'
        self.assertEqual(str(jails.table_definition()), expected)

    def testDelete(self):
        jails = Jails()
        entity = jails.new()

        expected = 'DELETE FROM jails WHERE id = ?'
        self.assertEqual(jails._generate_delete_query(entity.id), expected)

