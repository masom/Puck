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
from euca2ools.commands.euca import RunInstances, RebootInstances, DescribeInstances, TerminateInstances
class Euca2(Launcher):
    supported_api = ['create', 'delete', 'status', 'restart']

    def _eucatool_init(self, credentials, cmd):
        '''Initialize the euca command.'''

        settings = {
            'ec2_user_access_key': credentials.access_key,
            'ec2_user_secret_key': credentials.secret_key,
            'url': credentials.cloud_url,
            'region': credentials.region
        }

        cmd.handle_defaults()

        cmd.ec2_user_access_key = settings['ec2_user_access_key']
        cmd.ec2_user_secret_key = settings['ec2_user_secret_key']
        cmd.url = settings['url']
        cmd.region = settings['region']
        cmd.is_euca = False

        '''
        "id", "image_id", "public_dns_name", "private_dns_name",
        "state", "key_name", "ami_launch_index", "product_codes",
        "instance_type", "launch_time", "placement", "kernel",
        "ramdisk"
        '''
    def _euca_connect(self,cmd, type = 'ec2'):
        '''Raise euca2ools.exceptions.EucaError'''
        return cmd.make_connection('ec2')

    def _euca_make_request(self, cmd, connection, request_name, **params):
        '''
        Raise AttributeError
        Raise Exception
        '''

        try:
            if cmd.filters:
                params['filters'] = cmd.filters
            method = getattr(connection, request_name)
        except AttributeError:
            return False

        return method(**params)

    def create(self, **kwargs):
        image_id = kwargs['image_id']
        instance_type = kwargs['instance_type']
        credentials = kwargs['credentials']

        cmd = euca2ools.commands.euca.runinstances.RunInstances()
        self._eucatool_init(credentials, cmd)
        cmd.instance_type = instance_type
        cmd.image_id = image_id

        conn = self._euca_connect(cmd)

        options = dict(
            image_id=cmd.image_id,
            min_count=min_count,
            max_count=max_count,
            key_name=cmd.keyname,
            security_groups=cmd.group_name,
            user_data=cmd.user_data,
            addressing_type=cmd.addressing,
            instance_type=cmd.instance_type,
            placement=cmd.zone,
            kernel_id=cmd.kernel,
            ramdisk_id=cmd.ramdisk,
            block_device_map=cmd.block_device_mapping,
            monitoring_enabled=cmd.monitor,
            subnet_id=cmd.subnet
        )

        reservation = self._euca_make_request(cmd, conn, 'run_instances', **options)
        return reservation.id

    def status(self, **kwargs):
        id = kwargs['id']
        credentials = kwargs['credentials']

        cmd = euca2ools.commands.euca.describeinstances.DescribeInstances()
        self._eucatool_init(cmd)

        conn = self._euca_connect(credentials, cmd)

        options = dict(instance_ids=[id])
        reservations = self._euca_make_request(cmd, conn, 'get_all_instances', **options)

        instances = []
        for reservation in reservations:
            if len(reservation.instances) == 0:
                continue
            instances.extend(reservation.instances)
        return instances

    def delete(self, **kwargs):
        id = kwargs['id']
        credentials = kwargs['credentials']

        cmd = euca2ools.commands.euca.rebootinstances.TerminateInstances()
        self._eucatool_init(credentials, cmd)
        cmd.instance_id = id

        conn = self._euca_connect(cmd)

        options = dict(instance_ids=[id])
        instances = self._euca_make_request(cmd, conn, 'terminate_instances', **options)
        return instances

    def restart(self, **kwargs):
        id = kwargs['id']
        credentials = kwargs['credentials']

        cmd = euca2ools.commands.euca.rebootinstances.RebootInstances()
        self._eucatool_init(credentials, cmd)
        cmd.instance_id = id

        conn = self._euca_connect(cmd)

        options = dict(instance_ids=[id])
        status = self._euca_make_request(cmd, conn, 'reboot_instances', **options)

        if status:
            return self.instance_id
        else:
            return False

