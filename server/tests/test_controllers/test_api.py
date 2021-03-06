import unittest
import cherrypy

def fake_auth(groups=[]):
    pass

cherrypy.tools.myauth = cherrypy.Tool("before_handler", fake_auth)

from controllers.api import *
from models import Keys, Jails, YumRepositories
from collections import OrderedDict
from tests.base import PuckTestCase

class ApiTest(PuckTestCase):
    def testInit(self):
        api = Api(None)
        attrs = [
            'registration', 'keys', 'status', 'config', 'environments',
            'jails', 'yum_repo'
        ]
        for a in attrs:
            self.assertTrue(hasattr(api, a))

class ApiRegistrationTest(PuckTestCase):
    def testPOST(self):
        ar = ApiRegistration()
        vm = ar.POST()
        expected = ['name', 'ip', 'status', 'config']
        self.assertIsInstance(vm, OrderedDict)
        for k in expected:
            self.assertTrue(vm.has_key(k))

class ApiKeysTest(PuckTestCase):

    def testGET(self):
        ak = ApiKeys()
        keys = ak.GET()
        self.assertEqual(keys, {})

        key = Keys.new(name="test")
        Keys.add(key, persist=False)
        keys = ak.GET()
        self.assertEqual(keys, {'test': key.to_dict()})

        key = Keys.new(name='hello')
        Keys.add(key, persist=False)
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

class ApiConfigTest(PuckTestCase):
    def testPOST(self):
        pass
    def testGET(self):
        pass

class ApiEnvironmentsTest(PuckTestCase):
    def testGET(self):
        ae = ApiEnvironments()
        data = ae.GET()
        self.assertIsInstance(data, list)

        fields = ['id', 'name']
        [[self.assertTrue(e.has_key(f)) for f in fields] for e in data]

class ApiJailsTest(PuckTestCase):
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
                Jails.add(jail, persist=False)
                jails[e][t].append(jail.to_dict())
                i += 1

        data = aj.GET()
        self.assertEqual(data, {})

        self.maxDiff = None
        data = aj.GET('production')
        expected = {}
        self.assertEqual(data, jails['production'])
        self.assertEqual(aj.GET('test'), jails['test'])

class ApiYumTest(PuckTestCase):
    def testGET(self):
        ay = ApiYum()
        self.assertEqual(ay.GET(), None)
        self.assertEqual(ay.GET('nope'), None)

        YumRepositories.add(YumRepositories.new(environment='test'), persist=False)
        expected = OrderedDict([('environment', 'test'), ('data', None)])
        self.assertEqual(ay.GET('test'), expected)

class ApiTest(PuckTestCase):
    def testInit(self):
        api = Api(None)
        attrs = [
            'registration', 'keys', 'status', 'config',
            'environments', 'jails', 'yum_repos'
        ]
        for a in attrs:
            self.assertTrue(hasattr(api, a))
            self.assertIsInstance(getattr(api, a), ApiCall)
