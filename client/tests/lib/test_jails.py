import sys, os, unittest
from lib.jails import Jails, Jail, EzJail

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

class JailTest(unittest.TestCase):
    def testInit(self):
        pass
    def testCreate(self):
        pass

class JailsTest(unittest.TestCase):
    def testInit(self):
        jls = Jails()
        self.assertEqual({}, jls._jails, "Jails.jails hash is invalid.")
        self.assertTrue(isinstance(jls._manager, EzJail), "Jails._manager is not an EZJail instance.")
        self.assertEqual(Jail, jls._jail, "Jails._jail is not a Jail reference.")

    def testCreate(self):
        jls = Jails()
        j = jls.create(getJail())
        self.assertTrue(isinstance(j, Jail))

    def testAdd(self):
        jls = Jails()
        j = jls.create(getJail())
        jls.add(j)

        self.assertEqual(1, jls.count())
        self.assertRaises(KeyError, jls.add, j)

    def testGet(self):
        jls = Jails()
        jail = getJail()
        j = jls.create(jail)
        jls.add(j)

        self.assertEqual(j, jls.get(jail['id']))
        self.assertRaises(KeyError, jls.get, 'derp')

    def testContain(self):
        jls = Jails()
        jail = getJail()
        self.assertFalse(jls.contain(jail['id']), "Jails registry already contains the jail o_O")

        jls.add(jail)
        self.assertTrue(jls.contain(jail['id']), "Jails registry does not contain the jail!")

    def testIterate(self):
        jls = Jails()
        jails = []

        jails.append(jls.create(getJail()))
        jails.append(jls.create(getJail()))

        for j in jls:
            self.assertIn(j, jails, "Jail is not in expected list.")

    def testLoad(self):
        '''
        Jails.load() will load a json-serialized jail list and add them to it's registry
        '''
        jls = Jails()
        jails = []
        for i in range(10):
            jails.append(getJail())
        
        jls.load(jails)
        self.assertEqual(jls.count(), 10, "The number of imported jails does not match generated count")
