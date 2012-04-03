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
    attributes = ['nova_url', 'nova_username', 'nova_api_key', 'nova_project_id']

    def _post_init(self):
        for k in self.attributes:
            if k in self._data:
                setattr(self, k, self._data[k])
            else:
                setattr(self, k, None)

class Nova(Launcher):
    supported_api = ['create','delete','status','restart', 'instance_types',
        'images', 'exists', 'add_public_ip', 'public_ips', 'remove_public_ip'
    ]

    def _client(self, credentials):
        if credentials is None:
            raise RuntimeError("Invalid credential object.")
        return NovaClient(credentials.nova_username, credentials.nova_api_key, credentials.nova_project_id, credentials.nova_url)

    def create(self, **kwargs):
        image_id = kwargs['image_id']
        vm_id = kwargs['vm_id']
        vm_name = kwargs['vm_name']
        instance_type = kwargs['instance_type']
        credentials = kwargs['credentials']

        nova = self._client(credentials)
        meta = {'puck_vm_id': vm_id, 'puck_user': credentials.name}
        name = vm_name
        try:
            fl = nova.flavors.get(instance_type)
            instance = nova.servers.create(name=name, image=image_id,
                    flavor=fl, userdata=vm_id, meta=meta)
        except exceptions.NotFound as e:
            cherrypy.log(str(e))
            return False
        except exceptions.BadRequest as e:
            cherrypy.log(str(e))
            return False
        return Instance(instance)

    def delete(self, **kwargs):
        credentials = kwargs['credentials']
        nova = self._client(credentials)

        instance_id = kwargs['id']
        try:
            server = nova.servers.get(instance_id)
            server.delete()
        except exceptions.NotFound:
            return False
        return True

    def exists(self, **kwargs):
        credentials = kwargs['credentials']
        instance_id = kwargs['id']
        nova = self._client(credentials)
        try:
            instance = nova.servers.get(instance_id)
        except exceptions.NotFound:
            return False
        return True

    def status(self, **kwargs):
        credentials = kwargs['credentials']
        nova = self._client(credentials)
        servers = nova.servers.list(detailed=True)
        return self._generate_instances(servers)

    def restart(self, **kwargs):
        credentials = kwargs['credentials']
        nova = self._client(credentials)
        instance_id = kwargs['id']

        try:
            server = nova.servers.get(instance_id)
            server.reboot()
        except exceptions.NotFound:
            return False
        return True

    def instance_types(self, **kwargs):
        credentials = kwargs['credentials']
        nova = self._client(credentials)
        try:
            instance_types = nova.flavors.list()
        except exceptions.BadRequest as e:
            cherrypy.log(str(e))
            return False

        return self._generate_instance_types(instance_types)

    def images(self, **kwargs):
        credentials = kwargs['credentials']
        nova = self._client(credentials)
        images = nova.images.list()
        return self._generate_images(images)

    def public_ips(self, **kwargs):
        credentials = kwargs['credentials']
        nova = self._client(credentials)
        try:
            ips = nova.floating_ips.list()
        except exceptions.BadRequest as e:
            cherrypy.log(e)
            return []
        return ips

    def add_public_ip(self, **kwargs):
        credentials = kwargs['credentials']
        instance_id = kwargs['id']
        nova = self._client(credentials)
        ip = False
        try:
            iplist = nova.floating_ips.list()
            new_ip = None

            for ip in iplist:
                if ip.instance_id is None:
                    new_ip = ip
                    break

            if new_ip is None:
                new_ip = nova.floating_ips.create()

            server = nova.servers.get(instance_id)
            server.add_floating_ip(new_ip.ip)
        except (exceptions.BadRequest, exceptions.ClientException) as e:
            cherrypy.log(str(e))
            return False
        return ip.ip

    def remove_public_ip(self, **kwargs):
        credentials = kwargs['credentials']
        instance_id = kwargs['id']
        ip = kwargs['ip']

        nova = self._client(credentials)
        try:
            server = nova.servers.get(instance_id)
            server.remove_floating_ip(ip)
        except (exceptions.BadRequest, exceptions.ClientException) as e:
            cherrypy.log(str(e))
            return False
        return True
