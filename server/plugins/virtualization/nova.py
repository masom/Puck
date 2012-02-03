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
from libs.credentials import Credentials
import novaclient
import cherrypy

class NovaCredentials(Credentials):
    def _post_init(self):
        params = ['nova_url', 'nova_user', 'nova_password']

class Nova(Launcher):
    supported_api = ['create','delete','status','restart']

    def _client(self, credentials):
        return novaclient.OpenStack(credentials.nova_user, credentials.nova_password, credentials.nova_project, credentials.nova_url)

    def create(self, **kwargs):
        image_id = kwargs['image_id']
        instance_type = kwargs['instance_type']
        credentials = kwargs['credentials']

        nova = self._client(credentials)
        name = "%s-%s" % (credentials.username, len(nova.servers.list()))
        fl = nova.flavors.find(name=instance_type)
        instance = nova.servers.create(name=name, image=image_id, flavor=fl)
        print instance
        print dir(instance)

    def delete(self, **kwargs):
        credentials = kwargs['credentials']
        nova = self._client(credentials)

        instance_id = kwargs['id']
        server = nova.servers.get(instance_id)
        print server
        print dir(server)
        print server.delete()

    def status(self, **kwargs):
        credentials = kwargs['credentials']
        nova = self._client(credentials)
        servers = nova.servers.list(detailed=True)
        print servers

    def restart(self, **kwargs):
        credentials = kwargs['credentials']
        nova = self._client(credentials)
        instance_id = kwargs['id']

        server = nova.servers.get(id)
        print server
        print server.reboot()


