import unittest
from collections import OrderedDict
from models.images import Image, Images
from libs.model import ModelCollection, Model
class ImageTest(unittest.TestCase):

    def testInit(self):
        e = Image(id="test", name="Test")
        for a in ['id', 'name', 'backend_id']:
            self.assertTrue(hasattr(e, a))
        self.assertEqual('test', e.id)
        self.assertEqual('Test', e.name)
        self.assertEqual(None, e.backend_id)
        self.assertFalse(hasattr(e, 'derp'))
        self.assertIsInstance(e, Model)

        e = Image(id='test', name="Test", backend_id=2)
        self.assertEqual(2, e.backend_id)

class ImagesTest(unittest.TestCase):
    def testInit(self):
        envs = Images()
        self.assertIsInstance(envs, ModelCollection)
        self.assertGreater(envs._items, 0)
        self.assertIsInstance(envs.all(), list)

        for i in envs.all():
            self.assertIsInstance(i, Image)

    def testFirst(self):
        envs = Images()
        self.assertEqual(envs.first(), None)
        entity = envs.new()
        envs.add(entity, persist=False)
        self.assertEqual(envs.first(), entity)

    def testNew(self):
        envs = Images()
        self.assertIsInstance(envs.new(), Image)

        e = envs.new(id="lol")
        self.assertEqual(e.id, 'lol')

    def testAdd(self):
        envs = Images()
        before_count = len(envs.all())
        self.assertTrue(envs.add(envs.new(), persist=False))
        after_count = len(envs.all())
        self.assertGreater(after_count, before_count)
        self.assertEqual(before_count + 1, after_count)

    def testDelete(self):
        pass

    def test_GenerateSelectQuery(self):
        envs = Images()
        expected = 'SELECT * FROM images'
        self.assertEqual(envs._generate_select_query(), expected)

    def test_InsertQuery(self):
        envs = Images()
        entity = envs.new()

        expected = OrderedDict([('id', None), ('name', None), ('backend_id', None), ('description', None)])
        data = envs._generate_query_data(entity)
        self.assertEqual(expected, data)

        expected = 'INSERT INTO images(id,name,backend_id,description) VALUES (?,?,?,?)'
        self.assertEqual(envs._generate_insert_query(data), expected)

    def testTableDefinition(self):
        envs = Images()
        expected = 'CREATE TABLE images (id TEXT PRIMARY KEY,name TEXT,backend_id TEXT,description TEXT)'
        self.assertEqual(str(envs.table_definition()), expected)

    def testDelete(self):
        envs = Images()
        entity = envs.new()

        expected = 'DELETE FROM images WHERE id = ?'
        self.assertEqual(envs._generate_delete_query(entity.id), expected)
