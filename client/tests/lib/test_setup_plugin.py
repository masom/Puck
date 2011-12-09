import unittest, StringIO, Queue as queue

from lib.setup_plug import *

class InterfacesSetupTaskTest(unittest.TestCase):
    
    def test_add_rc_ip(self):      
        task = InterfacesSetupTask(None, None)

        rc_addresses = []
        file = StringIO.StringIO()
        alias_count = 0
        ip = '127.0.0.1'
        netmask = '123.456.789.0'

        task._add_rc_ip(rc_addresses, file, alias_count, ip, netmask)

        file.seek(0)

        msg = "Generated rc config does not match provided data."
        expected = 'ifconfig_em0_alias0="inet %s netmask %s"' % (ip, netmask)
        self.assertEqual(file.readline(), expected, msg)