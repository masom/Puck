import unittest, cherrypy, os
from lib.vm import VM

def getConf():
    return {
        'puck.registration_file': '/tmp/puck_registration',
        'vm.persistence': '/tmp/puck_vm'
    }

cherrypy.config.update(getConf())

class VMTest(unittest.TestCase):

    def testInit(self):
        vm = VM()
        self.assertEqual(None, vm.id)
        self.assertEqual({}, vm.keys)
        self.assertEqual('new', vm.status)
        self.assertEqual(None, vm.environment)
        self.assertTrue(isinstance(vm.interfaces, dict))
        self.assertGreater(len(vm.interfaces.keys()), 0)
        self.assertFalse(vm.configured)
        self.assertEqual(vm._persist_file, getConf()['vm.persistence'])

    def testUpdate(self):
        vm = VM()

        expected = {'test': {}}
        vm.update(keys = expected)
        self.assertEqual(vm.keys, expected, "VM keys do not match expected value.")