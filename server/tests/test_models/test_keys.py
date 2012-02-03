import unittest
from collections import OrderedDict
from models.keys import Key, Keys
from libs.model import ModelCollection, Model
class KeyTest(unittest.TestCase):

    def testInit(self):
        e = Key(name="test", key="asdf")
        for a in ['name', 'key']:
            self.assertTrue(hasattr(e, a))
        self.assertEqual('test', e.name)
        self.assertEqual('asdf', e.key)
        self.assertFalse(hasattr(e, 'derp'))
        self.assertIsInstance(e, Model)

    def testValidates(self):
        valid_key = [
            "ssh-rsa",
            "AAAAB3NzaC1yc2EAAAADAQABAAABAQC3lQT5LQIkdnraV/OKLzpx85PkbPLei1zK6OWX3eSkKX4g8QOZuV+91DBN8TjaBpAbZMav2wbARDFOmeisyvHnLpQLRlV9EXLXu8gLZ73nD8Q6k4VstV16HNfFA7PJhFisHVKbF6v5aq92eHuNdJS/s6msihf3S+gN9vQVS1eQqIELOvzlcuGDBUIs1dBsG2DcHbKBiyAeSj5j+ULBfZxKkxLpEeNnSAhpAxngik7MbRJITyzMg9sEukCjRhVL59GLkqxI96zuTxmlX7z1h+O9G6InyhcqeRUnrxEQ3mFLQMRXKFqSwOKEQk9SH4R3aWZ0VklfIrVEaqMNeIp9b+ap",
            "masom@workstation"
        ]

        k = Key()
        self.assertFalse(k.validates())

        k = Key(name="hehe")
        self.assertFalse(k.validates())

        k = Key(name="nope", key="haha")
        self.assertFalse(k.validates())

        k = Key(name="yup", key=" ".join(valid_key))
        self.assertTrue(k.validates())

        k = Key(name="yup", key=" ".join(valid_key[:2]))
        self.assertTrue(k.validates())

        k = Key(name="nope", key=" ".join(valid_key[1:3]))
        self.assertFalse(k.validates())

class KeysTest(unittest.TestCase):
    def testInit(self):
        keys = Keys()
        self.assertIsInstance(keys, ModelCollection)
        self.assertGreater(keys._items, 0)
        self.assertIsInstance(keys.all(), list)

        for i in keys.all():
            self.assertIsInstance(i, Key)

    def testFirst(self):
        keys = Keys()
        self.assertEqual(keys.first(), None)
        entity = keys.new()
        keys.add(entity, persist=False)
        self.assertEqual(keys.first(), entity)

    def testNew(self):
        keys = Keys()
        self.assertIsInstance(keys.new(), Key)

        e = keys.new(name="lol")
        self.assertEqual(e.name, 'lol')

    def testAdd(self):
        keys = Keys()
        before_count = len(keys.all())
        self.assertTrue(keys.add(keys.new(), persist=False))
        after_count = len(keys.all())
        self.assertGreater(after_count, before_count)
        self.assertEqual(before_count + 1, after_count)

    def testDelete(self):
        pass

    def test_GenerateSelectQuery(self):
        keys = Keys()
        expected = 'SELECT * FROM keys'
        self.assertEqual(keys._generate_select_query(), expected)

    def test_InsertQuery(self):
        keys = Keys()
        entity = keys.new()

        expected = OrderedDict([('name', None), ('key', None)])
        data = keys._generate_query_data(entity)
        self.assertEqual(expected, data)

        expected = 'INSERT INTO keys(name,key) VALUES (?,?)'
        self.assertEqual(keys._generate_insert_query(data), expected)

    def testTableDefinition(self):
        keys = Keys()
        expected = 'CREATE TABLE keys (name TEXT PRIMARY KEY,key TEXT)'
        self.assertEqual(str(keys.table_definition()), expected)

    def testDelete(self):
        keys = Keys()
        entity = keys.new()

        expected = 'DELETE FROM keys WHERE name = ?'
        self.assertEqual(keys._generate_delete_query(entity.name), expected)


