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

    def test_Find(self):
        mc = ModelCollection()
    def testFind(self):
        mc = ModelCollection()
        self.assertEqual(mc.find(name="derp"), [])

        expected = [MockModel(name="test")]
        mc._items = expected
        self.assertEqual(mc.find(name="test"), expected)
