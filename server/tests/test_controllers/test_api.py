import unittest

from controllers.api import *
from models import Keys, Jails
from collections import OrderedDict

class ApiTest(unittest.TestCase):
    def testInit(self):
        api = Api(None)
        attrs = [
            'registration', 'keys', 'status', 'config', 'environments',
            'jails', 'yum_repo'
        ]
        for a in attrs:
            self.assertTrue(hasattr(api, a))

class ApiRegistrationTest(unittest.TestCase):
    def testPOST(self):
        ar = ApiRegistration()
        vm = ar.POST()
        expected = ['name', 'ip', 'status', 'config']
        self.assertIsInstance(vm, OrderedDict)
        for k in expected:
            self.assertTrue(vm.has_key(k))

class ApiKeysTest(unittest.TestCase):

    def testGET(self):
        ak = ApiKeys()
        keys = ak.GET()
        self.assertEqual(keys, {})

        key = Keys.new(name="test")
        Keys.add(key)
        keys = ak.GET()
        self.assertEqual(keys, {'test': key.to_dict()})

        key = Keys.new(name='hello')
        Keys.add(key)
        keys = ak.GET()
        expected = {
            'test': OrderedDict([
                ('name', 'test'),
                ('key', None)
            ]),
            'hello': OrderedDict([
                ('name', 'hello'),
                ('key', None)
            ])
        }
        self.assertEqual(keys, expected)

class ApiConfigTest(unittest.TestCase):
    def testPOST(self):
        pass
    def testGET(self):
        pass

class ApiEnvironmentsTest(unittest.TestCase):
    def testGET(self):
        ae = ApiEnvironments()
        data = ae.GET()
        self.assertIsInstance(data, list)

        fields = ['id', 'name']
        [[self.assertTrue(e.has_key(f)) for f in fields] for e in data]

class ApiJailsTest(unittest.TestCase):
    def testGET(self):
        aj = ApiJails()
        data = aj.GET()
        self.assertEqual(data, {})

        data = aj.GET('production')
        self.assertEqual(data, {})

        envs = ['production', 'test', 'production', 'development']
        types = ['content', 'database']
        jails = {}
        i = 0
        for e in envs:
            if not e in jails:
                jails[e] = {}
            for t in types:
                if not t in jails[e]:
                    jails[e][t] = []

                jail = Jails.new(jail_type=t, environment=e, name="test_%s" % i)
                Jails.add(jail)
                jails[e][t].append(jail.to_dict())
                i += 1

        data = aj.GET()
        self.assertEqual(data, {})

        self.maxDiff = None
        data = aj.GET('production')
        expected = {}
        self.assertEqual(data, jails['production'])
        self.assertEqual(aj.GET('test'), jails['test'])

class ApiYumTest(unittest.TestCase):
    def testGET(self):
        ay = ApiYum()
        self.assertEqual(ay.GET(), None)
