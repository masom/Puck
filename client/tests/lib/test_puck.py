import unittest, cherrypy, os
from lib.puck import Puck
from lib.vm import VM

def getConf():
    return {
        'puck.registration_file': '/tmp/puck_registration',
        'vm.persistence': '/tmp/puck_vm'
    }

jailCount = 0
def getJail():
    '''
    Returns a base jail.
    '''
    global jailCount
    jailCount += 1
    return {
        'id': 'test_%s' % jailCount,
        'type': 'default',
        'name': 'test_%s' % jailCount,
        'ip': '10.0.0.%s' % jailCount,
        'url': 'http://localhost'
    }

def getKey():
    '''
    Return a valid key entry
    '''
    return {
        'id': 'derp',
        'name': 'Martin Samson',
        'key': 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEArsIuqG9Wictam3s6cwQdW0eedJYuoMbvF7kJ9oFprfo1UEsep30G67SPSUNwuIOIqvUwErFkiNAGjTqdnL8g7PHUInLojM3KQSGSvPgYYAZz9u9wYTy5vv2f/EphBx+FytISjoW1gL8CoiP/kX0vDLpDJnFeRQ/RbvRbiws49r/yqqf/KqXM/fwl1nhQeqwNS6K8kv3H8aaaq7cHqky0xbiDf7astFQq++jRjLIx6xX0NdU8P36IwdMFoQXdnh1B8OvMuyCxHj9y5B2wN2H/1kA0tk0dEQa1BtKNqpJF8HD2AbcTGzYczcvaCMbMV1qJe5/YTQMxjullp2cz/83Hjw=='
    }

def getEnvironments():
    '''
    Return a valid list of environments.
    '''
    return {
        'dev': 'Development',
        'testing': 'Testing',
        'qa': 'Quality Assurance',
        'staging': 'Staging',
        'prod': 'Production'
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
            for i in jails[k]:
                self.assertEqual(jails[k][i].keys().sort(), getJail().keys().sort(), "getJails dict keys are not the same as expected.")

    def test_GetKeys(self):
        p = Puck()
        keys = p.getKeys()
        self.assertTrue(isinstance(keys, dict))
        self.assertGreater(len(keys.keys()), 0)

        for k in keys:
            self.assertEqual(keys[k].keys().sort(), getKey().keys().sort(), "getKeys dict keys are not the same as expected.")

    def test_GetEnvironments(self):
        p = Puck()
        env = p.getEnvironments()
        self.assertTrue(isinstance(env, dict))
        self.assertGreater(len(env.keys()), 0)

        for k in env:
            self.assertTrue(isinstance(env[k], str))
