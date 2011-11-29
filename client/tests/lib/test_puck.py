import unittest, cherrypy, os
from lib.puck import Puck
from lib.vm import VM

def getConf():
    return {
        'puck.registration_file': '/tmp/puck_registration',
        'vm.persistence': '/tmp/puck_vm'
    }

cherrypy.config.update(getConf())

class PuckTest(unittest.TestCase):

    def testInit(self):
        p = Puck()
        self.assertTrue(isinstance(p, Puck))

    def testGetVM(self):
        p = Puck()
        self.assertTrue(isinstance(p.getVM(), VM))

    def test_GetRegistration(self):
        p = Puck()
        self.assertNotEqual(p._getRegistration(), "", "Registration is empty!")

    def test_loadRegistration(self):
        p = Puck()
        p._registration_file = '/tmp/non-existent-reg'
        self.assertRaises(IOError, p._loadRegistration)

        with open("/tmp/reg-test", 'w') as f:
            f.write('test')

        p._registration_file = '/tmp/reg-test'
        self.assertEqual(4, p._loadRegistration(), "Registration data length does not match expected.")

    def test_GetJails(self):
        p = Puck()
        jails = p.getJails()
        self.assertTrue(isinstance(jails, dict), "getJails() did not return a dictionary.")
        self.assertGreater(len(jails.keys()), 0)

        for k in jails:
            self.assertGreater(len(jails[k]), 0, "No jails under `%s`" % k)

       
    