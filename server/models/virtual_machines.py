'''
Puck: FreeBSD virtualization guest configuration server
Copyright (C) 2012  The Hotel Communication Network inc.

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
from libs.model import ModelCollection, Model, TableDefinition
from collections import OrderedDict, deque
import cherrypy

class VirtualMachine(Model):
    def __init__(self, id=None,name=None, ip=None, status=None, config=None,
            instance_type_id=None, image_id=None, instance_id = None,
            user_id=None):
        self.id = id
        self.name = name
        self.instance_type_id = instance_type_id

        if instance_id and instance_id.isdigit():
            self.instance_id = int(instance_id)
        else:
            self.instance_id = instance_id

        self.image_id = image_id
        self.ip = ip
        self.status = status
        self.config = config
        self.user_id = user_id

    def add_public_ip(self, creds):
        ''' Assign a public ip to the instance.'''

        args = dict(
            action="add_public_ip",
            id = self.instance_id,
            credentials=creds
        )

        ip = cherrypy.engine.publish('virtualization', **args).pop()

        if not ip:
            return False

        self.update({'ip': ip}, ['ip'])
        return ip

    def remove_public_ip(self, creds):
        ''' De-assign a public ip from the instance.'''

        args = dict(
            action = 'remove_public_ip',
            id = self.instance_id,
            ip = self.ip,
            credentials = creds
        )
        removed = cherrypy.engine.publish('virtualization', **args).pop()
        if removed:
            self.update({'ip': None}, ['ip'])
        return removed


    def release_public_ip(self):
        pass

    def start_instance(self, image, instance_type, creds):
        ''' Starts an instance and updates itself with the relational details.'''

        self.image_id = image.id
        self.instance_type_id = instance_type.id

        args = dict(
            action="create",
            vm_id = self.id,
            vm_name = self.name,
            image_id=image.backend_id,
            instance_type=instance_type.id,
            credentials=creds
        )

        instance = cherrypy.engine.publish("virtualization", **args).pop()
        if not instance:
            return False
        data = {'instance_id': instance.id, 'user_id': creds.id}
        self.update(data, ['instance_id', 'user_id'])
        return True

    def stop_instance(self, creds):
        ''' Stops the attached instance. '''
        if not self.instance_id:
            return False

        args = dict(
            action="stop",
            id=self.instance_id,
            credentials=creds
        )
        return cherrypy.engine.publish("virtualization", **args).pop()

    def restart_instance(self, creds):
        ''' Restart the attached instance. '''
        if not self.instance_id:
            return False

        args = dict(
            action="restart",
            id=self.instance_id,
            credentials=creds
        )
        return cherrypy.engine.publish("virtualization", **args).pop()

    def instance_exists(self, creds):
        ''' Determine if an instance exists. '''
        if not self.instance_id:
            return False

        self.remove_public_ip(creds)

        args = dict(
            action="exists",
            id=self.instance_id,
            credentials=creds
        )
        return cherrypy.engine.publish("virtualization", **args).pop()

    def delete_instance(self, creds):
        ''' Delete the attached instance. '''
        if not self.instance_id:
            return False

        if not self.instance_exists(creds):
            raise KeyError('Instance %s does not exists.' % self.instance_id)

        args = dict(
            action="delete",
            id=self.instance_id,
            credentials=creds
        )
        return cherrypy.engine.publish("virtualization", **args).pop()

class VirtualMachines(ModelCollection):
    _model = VirtualMachine

    def _after_init(self):
        # TODO: Move this to the config file.
        self._word_p = 0
        self._wordlist = list(set([
            "apple", "banana", "carrot", "pepper", "salt", "orange",
            "eggplant", "squash", "melon", "peach", "kale",
            "tomato", "potato", "onion", "grapefruit", "radish", "broccoli",
            "cilantro", "parsley", "plum", "scallion", "haberno", "strawberry",
            "grape", "cranberry", "lemongrass", "sugarcane", "dragonfly", "derp",
            "iseewhatyoudid", "awwwyeah", "trolololol", "mudkipz", "ped_bear",
            "cliff", "energy", "hybrid", "dell", "perl", "python", "php", "ruby",
            "reddit", "4chan", "9gag", "facebook", "onion", "swiss", "steveo",
            "bart", "homer", "lisa", "crashoverride", "acidburn", "cerealkiller",
            "knifeparty", "zedsdead", "flux", "pavilion", "filth", "dimmu",
            "borgir", "agonist", "dethklok", "disturbed", "graveworm", "korn",
            "lagwagon", "mudvayne", "murderdolls", "offspring", "rammstein",
            "spliknot", "svartsot", "tool", "twisted"
            ]))
        self._wordlist.sort()

    def _generate_table_definition(self):
        columns = OrderedDict([
            ('id', 'TEXT'),
            ('name', 'TEXT'),
            ('ip', 'TEXT'),
            ('status', 'TEXT'),
            ('image_id', 'TEXT'),
            ('instance_type_id', 'TEXT'),
            ('instance_id', 'TEXT'),
            ('user_id', 'TEXT'),
            ('config', 'TEXT')
        ])
        return TableDefinition('virtual_machines', columns=columns)


    def get_instances(self, creds):
        args = dict(
            action="status",
            credentials=creds
        )
        instances = cherrypy.engine.publish("virtualization", **args).pop()
        return instances

    def new(self, **kwargs):
        if not 'name' in kwargs:
            loops = 0
            name = None
            while name is None:
                name = self._wordlist[self._word_p]

                if ModelCollection.first(self, name=name):
                    name = None
                self._word_p += 1
                if self._word_p >= len(self._wordlist):
                    self._word_p = 0
                    loops += 1
                    if loops > 2:
                        name = 'unnamed-%s' % len(self._items)
                        break

            kwargs['name'] = name
        return ModelCollection.new(self, **kwargs)
