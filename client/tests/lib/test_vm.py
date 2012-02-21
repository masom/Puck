import unittest, cherrypy, os
from pixie.lib.vm import VM

def getConf():
    return {
        'puck.registration_file': '/tmp/puck_registration',
        'vm.persistence': '/tmp/puck_vm'
    }

cherrypy.config.update(getConf())

class VMTest(unittest.TestCase):

    def testInit(self):
        vm = VM({'id': None, 'name': None})
        self.assertEqual(None, vm.id)
        self.assertEqual({}, vm.keys)
        self.assertEqual('new', vm.status)
        self.assertEqual(None, vm.environment)
        self.assertTrue(isinstance(vm.interfaces, dict))
        self.assertGreater(len(vm.interfaces.keys()), 0)
        self.assertFalse(vm.configured)
        self.assertEqual(vm._persist_file, getConf()['vm.persistence'])

    def testUpdate(self):
        vm = VM({'id': None, 'name': None})

        expected = {'test': {}}
        vm.update(keys = expected)
        self.assertEqual(vm.keys, expected, "VM keys do not match expected value.")

        '''This test makes sure __setattr__ will not assign data to invalid attributes.'''
        vm.update(invalid = "derp")
        with self.assertRaises(AttributeError):
            vm.invalid

    def testIsConfigured(self):
        vm = VM({'id': None, 'name': None})

        self.assertFalse(vm.isConfigured())
        self.assertTrue(vm.isConfigured(True))
        self.assertEqual(vm.status, 'configured')

        self.assertFalse(vm.isConfigured(False))
        self.assertEqual(vm.status, 'new')
