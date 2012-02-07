import urllib2, urllib, json, unittest


class Requester(object):
    def __init__(self):
        self._base = 'http://localhost:8080/api'
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        self._open = opener.open

    def post(self, resource, data=''):
        return self._request('POST', resource, data=data)

    def get(self, resource, **params):
        if params:
            resource += '?' + urllib.urlencode(params)
        return self._request('GET', resource)

    def put(self, resource, id, data=''):
        resource += '/%s' % id
        return self._request('PUT', resource, data=data)

    def _resource(self, *args):
        return '/'.join((self._base,) + args)

    def _request(self, method, resource, data=None):
        if data:
            data=json.dumps(data)
        request = urllib2.Request(self._resource(resource), data=data)
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda : method

        try:
            data = json.load(self._open(request))
        except urllib2.HTTPError as e:
            # @TODO: Logging
            return None
        return data

class ApiTest(unittest.TestCase):
    def testRegistration(self):
        requester = Requester()
        registration = requester.post('registration')
        keys = ['status', 'name', 'ip', 'instance_type_id', 'instance_id',
                'image_id', 'user', 'config', 'id'
        ]
        [self.assertTrue(registration.has_key(k)) for k in keys]
        self.assertEqual(registration['ip'], '127.0.0.1')

        registrations = [
                requester.post('registration'),
                requester.post('registration')
        ]
        self.assertNotEqual(registrations[0]['id'], registrations[1]['id'])
        self.assertNotEqual(registrations[0]['name'], registrations[1]['name'])

    def testKeys(self):
        requester = Requester()
        ssh_keys = requester.get('keys')
        self.assertIsInstance(ssh_keys, dict)

        keys = ['name', 'key']
        for id in ssh_keys:
            self.assertEqual(ssh_keys[id]['name'], id)
            [self.assertTrue(ssh_keys[id].has_key(k)) for k in keys]

    def testStatus(self):
        requester = Requester()
        registration = requester.post('registration')

        data = {'id': None, 'status':'bogus'}
        status = requester.put('status', None, data)
        self.assertIsNone(status)

        data = {'id': registration['id'], 'status': 'lol'}
        status = requester.put('status', registration['id'], data)
        expected = {'status': 200, 'message': 'Status updated.'}
        self.assertEqual(status, expected)
