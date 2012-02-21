import unittest, StringIO, Queue as queue

from pixie.lib.setup_plugin import *

class MockJail(object):
    def __init__(self, ip, netmask):
        self.ip = ip
        self.netmask = netmask

class MockVM(object):
    def __init__(self):
        self.interface = 'em0'
        self.jails = [MockJail('127.0.0.1', '255.255.255.0'), MockJail('127.0.0.2', '255.255.255.0')]
        self.firewall = "test firewall"

class MockPuck(object):
    def getVM(self):
        return MockVM()

class InterfacesSetupTaskTest(unittest.TestCase):

    def test_add_rc_ip(self):
        task = InterfacesSetupTask(MockPuck(), queue.Queue())

        rc_addresses = []
        file = StringIO.StringIO()
        alias_count = 0
        netaddr = {'ip': '127.0.0.1', 'netmask': '123.456.789.0'}
        retval = task._add_rc_ip(rc_addresses, file, alias_count, netaddr)

        file.seek(0)

        expected = "ifconfig_em0_alias0=\"inet %s netmask %s\"\n" % (netaddr['ip'], netaddr['netmask'])
        data = file.readline()
        self.assertTrue(retval)
        self.assertEqual(data, expected)

        '''Prevent adding 2 times the template.'''
        rc_addresses.append(expected)
        retval = task._add_rc_ip(rc_addresses, file, alias_count, netaddr)
        self.assertFalse(retval)

        netaddr['ip'] = '127.0.0.2'
        alias_count += 1
        retval = task._add_rc_ip(rc_addresses, file, alias_count, netaddr)
        expected = "ifconfig_em0_alias1=\"inet %s netmask %s\"\n" % (netaddr['ip'], netaddr['netmask'])
        file.seek(0)
        file.readline() #Discard first line
        data = file.readline()
        self.assertTrue(retval)
        self.assertEqual(data, expected)

        file.close()

    def test_calculate_alias_count(self):
        task = InterfacesSetupTask(MockPuck(), None)

        rc = StringIO.StringIO()
        addresses = []
        alias_count = task._calculate_alias_count(addresses, rc)
        self.assertEqual(0, alias_count)

        rc.writelines(["ifconfig_em0_alias0\n", "ifconfig_em0_alias1\n"])
        rc.flush()
        rc.seek(0)
        alias_count = task._calculate_alias_count(addresses, rc)
        self.assertEqual(2, alias_count)

        rc.writelines(["is0\n", "ifconfig_alias1\n", "sshd_enable=YES\n"])
        rc.seek(0)
        rc.flush()

        alias_count = task._calculate_alias_count(addresses, rc)
        self.assertEqual(2, alias_count)

        rc.writelines(["ifconfig_em0_alias33\n"])
        rc.seek(0)
        rc.flush()
        alias_count = task._calculate_alias_count(addresses, rc)
        self.assertEqual(3, alias_count)

        rc.close()

    def test_get_missing_netaddrs(self):
        task = InterfacesSetupTask(MockPuck(), None)

        (jails_ip, missing) = task._get_missing_netaddrs()
        self.assertEqual([{'ip': '127.0.0.2', 'netmask': '255.255.255.0'}], missing)

class FirewallSetupTaskTest(unittest.TestCase):
    def testSetupRc(self):
        task = FirewallSetupTask(MockPuck(), None)
        rc = StringIO.StringIO()

        task.setup_rc(rc, '/etc/pf.rules.conf')
        rc.flush()
        rc.seek(0)

        expected = [
            'pf_enable="YES"', 'pf_rules="/etc/pf.rules.conf"',
            'pflog_enable="YES"', 'gateway_enable="YES"'
        ]
        lines = rc.readlines()
        self.assertEqual(lines, expected)

        data = ['pf_enabled="YES"', 'gateway_enable="YES"']
        rc = StringIO.StringIO()
        rc.writelines(data)
        rc.flush()
        task.setup_rc(rc, '/etc/pf.rules.conf')
        rc.flush()
        rc.seek(0)
        lines = rc.readlines()
        self.assertEqual(lines, expected)
