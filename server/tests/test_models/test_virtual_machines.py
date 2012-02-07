import unittest
from collections import OrderedDict
from models.virtual_machines import VirtualMachine, VirtualMachines
from libs.model import ModelCollection, Model
class VirtualMachineTest(unittest.TestCase):

    def testInit(self):
        e = VirtualMachine(name="test", ip="asdf", status='derp', config='lol')
        for a in ['name', 'ip','status','config']:
            self.assertTrue(hasattr(e, a))
        self.assertEqual('test', e.name)
        self.assertEqual('asdf', e.ip)
        self.assertEqual('derp', e.status)
        self.assertEqual('lol', e.config)
        self.assertFalse(hasattr(e, 'derp'))
        self.assertIsInstance(e, Model)

class VirtualMachinesTest(unittest.TestCase):
    def testInit(self):
        vms = VirtualMachines()
        self.assertIsInstance(vms, ModelCollection)
        self.assertGreater(vms._items, 0)
        self.assertIsInstance(vms.all(), list)

        for i in vms.all():
            self.assertIsInstance(i, VirtualMachine)

    def testFirst(self):
        vms = VirtualMachines()
        self.assertEqual(vms.first(), None)
        entity = vms.new()
        vms.add(entity, persist=False)
        self.assertEqual(vms.first(), entity)

    def testNew(self):
        vms = VirtualMachines()
        self.assertIsInstance(vms.new(), VirtualMachine)

        e = vms.new(name="lol")
        self.assertEqual(e.name, 'lol')
        self.assertEqual(e.ip, None)

        e = vms.new()
        self.assertIsNotNone(e.name)
        self.assertNotEqual(vms.new().name, e.name)

    def testAdd(self):
        vms = VirtualMachines()
        before_count = len(vms.all())
        self.assertTrue(vms.add(vms.new(), persist=False))
        after_count = len(vms.all())
        self.assertGreater(after_count, before_count)
        self.assertEqual(before_count + 1, after_count)

    def testDelete(self):
        pass

    def test_GenerateSelectQuery(self):
        vms = VirtualMachines()
        expected = 'SELECT * FROM virtual_machines'
        self.assertEqual(vms._generate_select_query(), expected)

    def test_InsertQuery(self):
        vms = VirtualMachines()
        entity = vms.new(name=None)
        expected = OrderedDict([
            ('id', None), ('name', None), ('ip', None), ('status', None),
            ('image_id', None), ('image_id', None), ('instance_type_id', None),
            ('instance_id', None),('user', None), ('config', None)
        ])
        data = vms._generate_query_data(entity)
        self.assertEqual(expected, data)

        expected = 'INSERT INTO virtual_machines(id,name,ip,status,image_id,instance_type_id,instance_id,user,config) VALUES (?,?,?,?,?,?,?,?,?)'
        self.assertEqual(vms._generate_insert_query(data), expected)

    def testTableDefinition(self):
        vms = VirtualMachines()
        expected = 'CREATE TABLE virtual_machines (id TEXT PRIMARY KEY,name TEXT,ip TEXT,status TEXT,image_id TEXT,instance_type_id TEXT,instance_id TEXT,user TEXT,config TEXT)'
        self.assertEqual(str(vms.table_definition()), expected)

    def testDelete(self):
        vms = VirtualMachines()
        entity = vms.new()

        expected = 'DELETE FROM virtual_machines WHERE id = ?'
        self.assertEqual(vms._generate_delete_query(entity.name), expected)

