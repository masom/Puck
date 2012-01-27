import unittest
from libs.model import ModelCollection

class ModelTest(unittest.TestCase):
    pass

class MockModel(object):
    def __init__(self, **kwargs):
        for i in kwargs:
            setattr(self, i, kwargs[i])

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

    def testFind(self):
        mc = ModelCollection()
        self.assertEqual(mc.find(name="derp"), [])

        expected = [MockModel(name="test")]
        mc._items = expected
        self.assertEqual(mc.find(name="test"), expected)
