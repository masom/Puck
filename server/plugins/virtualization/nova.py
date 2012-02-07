'''
Puck: FreeBSD virtualization guest configuration server
Copyright (C) 2011  The Hotel Communication Network inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from libs.launcher import Launcher
from libs.instance import Instance
from libs.credentials import Credentials
from novaclient.v1_1 import Client as NovaClient
from novaclient import exceptions
import cherrypy

class NovaCredentials(Credentials):
    def _post_init(self):
        params = ['nova_url', 'nova_username', 'nova_api_key', 'nova_project_id']
        for k in params:
            if k in self._data:
                setattr(self, k, self._data[k])
            else:
                setattr(self, k, None)

class Nova(Launcher):
    supported_api = ['create','delete','status','restart', 'instance_types', 'images']

    def _client(self, credentials):
        if credentials is None:
            raise RuntimeError("Invalid credential object.")

        return NovaClient(credentials.nova_username, credentials.nova_api_key, credentials.nova_project_id, credentials.nova_url)

    def create(self, **kwargs):
        image_id = kwargs['image_id']
        instance_type = kwargs['instance_type']
        credentials = kwargs['credentials']

        nova = self._client(credentials)
        name = "%s-%s" % (credentials.nova_username, len(nova.servers.list()))
        try:
            fl = nova.flavors.get(instance_type)
            instance = nova.servers.create(name=name, image=image_id, flavor=fl)
        except exceptions.NotFound as e:
            print e
            return False
        except exceptions.BadRequest as e:
            print e
            return False
        return Instance(instance)

    def delete(self, **kwargs):
        credentials = kwargs['credentials']
        nova = self._client(credentials)

        instance_id = kwargs['id']
        server = nova.servers.get(instance_id)
        print server.delete()

    def status(self, **kwargs):
        credentials = kwargs['credentials']
        nova = self._client(credentials)
        servers = nova.servers.list(detailed=True)
        return self._generate_instances(servers)

    def restart(self, **kwargs):
        credentials = kwargs['credentials']
        nova = self._client(credentials)
        instance_id = kwargs['id']

        server = nova.servers.get(id)
        print server.reboot()

    def instance_types(self, **kwargs):
        credentials = kwargs['credentials']
        nova = self._client(credentials)
        instance_types = nova.flavors.list()
        return self._generate_instance_types(instance_types)

    def images(self, **kwargs):
        credentials = kwargs['credentials']
        nova = self._client(credentials)
        images = nova.images.list()
        return self._generate_images(images)
