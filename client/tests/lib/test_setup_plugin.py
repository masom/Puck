import unittest, StringIO, Queue as queue

from lib.setup_plugin import *

class MockVM(object):
    def __init__(self):
        self.interface = 'em0'

class MockPuck(object):
    def getVM(self):
        return MockVM()

class InterfacesSetupTaskTest(unittest.TestCase):
    
    def test_add_rc_ip(self):      
        task = InterfacesSetupTask(MockPuck(), None)

        rc_addresses = []
        file = StringIO.StringIO()
        alias_count = 0
        ip = '127.0.0.1'
        netmask = '123.456.789.0'

        retval = task._add_rc_ip(rc_addresses, file, alias_count, ip, netmask)

        file.seek(0)

        expected = "ifconfig_em0_alias0=\"inet %s netmask %s\"\n" % (ip, netmask)
        data = file.readline()
        self.assertTrue(retval)
        self.assertEqual(data, expected)

        '''Prevent adding 2  times the template.'''
        rc_addresses.append(expected)
        retval = task._add_rc_ip(rc_addresses, file, alias_count, ip, netmask)
        self.assertFalse(retval)

        ip = '127.0.0.2'
        alias_count += 1
        retval = task._add_rc_ip(rc_addresses, file, alias_count, ip, netmask)
        expected = "ifconfig_em0_alias1=\"inet %s netmask %s\"\n" % (ip, netmask)
        file.seek(0)
        file.readline() #Discard first line
        data = file.readline()
        self.assertTrue(retval)
        self.assertEqual(data, expected)
        
        