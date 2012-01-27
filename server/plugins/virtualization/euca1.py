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

'''
This is the euca2ools version 1.3 launcher
'''

from libs.launcher import Launcher

import euca2ools

class Euca1(Launcher):
    class Euca(euca2ools.Euca2ool):
        def __init__(self, credentials=None):
            '''Overloads euca2ools.Euca2ool to prevent reading app options.'''

            self.ec2_user_access_key = credentials.ec2_user_access_key
            self.ec2_user_secret_key = credentials.ec2_user_secret_key
            self.url = credentials.ec2_url
            self.is_s3 = False
            self.img = euca2ools.LinuxImage(False)

            self.environ = {
                'EC2_ACCESS_KEY': credentials.ec2_user_access_key,
                'EC2_SECRET_KEY': credentials.ec2_user_secret_key,
                'S3_URL': credentials.s3_url,
                'EC2_URL': credentials.ec2_url,
                'EC2_CERT': credentials.ec2_cert,
                'EC2_PRIVATE_KEY': credentials.ec2_private_key,
                'EUCALYPTUS_CERT': credentials.eucalyptus_cert,
                'EC2_USER_ID': credentials.ec2_user_id
            }

        def setup_environ(self):
            '''Overload euca2ools.Euca2ool setup_environ'''
            pass

    supported_api = ['create', 'delete', 'status', 'restart']

    # Supported versions
    EUCA_VERSION = '2007-10-10'
    EUCA_BUNDLER_VERSION = '1.3'

    def __init__(self):
        if not hasattr(euca2ools, "VERSION"):
            msg = "euca2ools does not have a version number."
            raise RuntimeError(msg)

        if not euca2ools.VERSION == self.EUCA_VERSION:
            msg = "Wrong version of euca2ools. Expected: `%s`. Found: `%s`"
            raise RuntimeError(msg % (self.EUCA_VERSION, euca2ools.VERSION))

    def _euca_init(self, credentials, *args):
        '''Initialize a euca connection object and returns it.'''

        settings = {
            'ec2_user_access_key': credentials.access_key,
            'ec2_user_secret_key': credentials.secret_key,
            'ec2_url': credentials.cloud_url,
            's3_url': None,
            'config_file_path': None,
            'is_s3': False
        }
        #if is_s3 is set to True, then it will connect using S3Connection.
        #must be set to False for EC2Connection

        print args
        euca = self.Euca(*args)

        for key in settings:
            setattr(euca, key, settings[key])

        return euca

    def create(self, **kwargs):
        image_id = kwargs['image_id']
        instance_type = kwargs['instance_type']

        credentials = kwargs['credientials']

        args = [
            'key=',
            'kernel=',
            'ramdisk=',
            'instance-count=',
            'instance-type=',
            'group=',
            'user-data=',
            'user-data-file=',
            'addressing=',
            'availability-zone=',
            'block-device-mapping=',
            'monitor',
            'subnet_id=',
        ]
        euca = self._euca_init(credentials, 'k:n:t:g:d:f:z:b:', args)

        defaults = dict(
            image_id = image_id,
            key_name = None,
            kernel_id = None,
            ramdisk_id = None,
            min_count = 1,
            max_count = 1,
            instance_type = instance_type,
            security_groups = [],
            user_data = None,
            user_data_file = None,
            addressing_type = None,
            placement = None,
            block_device_map_args = [],
            block_device_map = None,
            monitoring_enabled = False,
            subnet_id = None,
        )

        try:
            euca_conn = euca.make_connection()
            reservation = euca_conn.run_instances(**defaults)
        except (ConnectionFailed,Exception) as e:
            print e.message
            raise e

        return self._generate_instances(reservation.instances)

    def delete(self, **kwargs):
        credentials = kwargs['credentials']
        euca = self._euca_init(credentials)

        if not euca.validate_instance_id(kwargs['id']):
            raise ValueError("Received id is not valid.")

        connection = euca.make_connection()
        connection.terminate_instances([kwargs['id']])
        return True

    def status(self, **kwargs):
        #use euca.validate_instance_id on kwargs['id']
        credentials = kwargs['credentials']
        euca = self._euca_init(credentials)

        if 'id' in kwargs:
            if not euca.validate_instance_id(kwargs['id']):
                raise ValueError("Received id is not valid.")

        connection = euca.make_connection()
        reservations = connection.get_all_instances([kwargs['id']])

        instances = []
        for reservation in reservations:
            instances.extend(reservation.instances)

        return self._generate_instances(instances)

    def restart(self, **kwargs):
        credentials = kwargs['credentials']
        euca = self._euca_init(credentials)

        if not euca.validate_instance_id(kwargs['id']):
            raise ValueError("Received id is not valid.")

        connection = euca.make_connection()
        connection.reboot_instances([kwargs['id']])
        return True
