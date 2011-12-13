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

from plugins.virtualization.launcher import Launcher

import euca2ools

class Euca1(Launcher):
    class Euca(euca2ools.Euca2ool):
        '''Overload euca2ools.Euca2ool setup_environ'''
        def setup_environ(self):
            pass
        
    supported_api = ['create', 'delete', 'status', 'restart']

    '''Supported versions'''
    EUCA_VERSION = '2007-10-10'
    EUCA_BUNDLER_VERSION = '1.3'
    def __init__(self):
        if not hasattr(euca2ools, "VERSION"):
            msg = "euca2ools does not have a version number."
            raise RuntimeError(msg)

        if not euca2ools.VERSION == self.EUCA_VERSION:
            msg = "Wrong version of euca2ools. Expected: `%s`. Found: `%s`"
            raise RuntimeError(msg % (self.EUCA_VERSION, euca2ools.VERSION))

    def _euca_init(self):
        '''Initialize a euca connection object and returns it.'''

        '''TODO: Read database about current user.'''

        settings = {
            'ec2_user_access_key': None,
            'ec2_user_secret_key': None,
            'ec2_url': None,
            's3_url': None,
            'config_file_path': None,
            'is_s3': False
        }
        #if is_s3 is set to True, then it will connect using S3Connection.
        #must be set to False for EC2Connection

        euca = self.Euca()

        for key in settings:
            setattr(euca, key, settings[key])

        return euca
        
    def create(self, **kwargs):
        pass

    def delete(self, **kwargs):
        euca = self._euca_init()

        ids = []

        if 'id' in kwargs:
            if not euca.validate_instance_id(kwargs['id']):
                raise ValueError("Received id is not valid.")
            ids.append(kwargs['id'])

        connection = euca.make_connection()
        connection.terminate_instances(instance_ids)

    def status(self, **kwargs):
        #use euca.validate_instance_id on kwargs['id']

        euca = self._euca_init()

        ids = []

        if 'id' in kwargs:
            if not euca.validate_instance_id(kwargs['id']):
                raise ValueError("Received id is not valid.")
            ids.append(kwargs['id'])

        connection = euca.make_connection()
        reservations = connection.get_all_instances(ids)

        instances = []
        for reservation in reservations:
            if len(ids) > 0:
                for instance in reservation.instances:
                    if instance.id in ids:
                        instances.append(instance)
            else:
                instances.extend(reservation.instances)

        return self._generate_instances(instances)

    def restart(self, **kwargs):
        euca = self._euca_init()

        ids = []

        if 'id' in kwargs:
            if not euca.validate_instance_id(kwargs['id']):
                raise ValueError("Received id is not valid.")
            ids.append(kwargs['id'])

        connection = euca.make_connection()
        connection.reboot_instances(ids)
