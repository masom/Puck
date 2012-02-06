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

class VirtualMachine(Model):
    def __init__(self, id=None,name=None, ip=None, status=None, config=None,
            instance_type_id=None, image_id=None, instance_id = None,
            user=None):
        self.id = id
        self.name = name
        self.instance_type_id = instance_type_id
        self.instance_id = instance_id
        self.image_id = image_id
        self.ip = ip
        self.status = status
        self.config = config
        self.user = user

class VirtualMachines(ModelCollection):
    _model = VirtualMachine

    def _after_init(self):
        # TODO: Move this to the config file.
        self._wordlist = deque([
            "apple", "banana", "carrot", "pepper", "salt", "orange",
            "eggplant", "squash", "melon", "peach", "kale", "swiss chard",
            "tomato", "potato", "onion", "grapefruit", "radish", "broccoli",
            "cilantro", "parsley", "plum", "scallion", "haberno", "strawberry",
            "grape", "cranberry", "lemongrass", "sugarcane"
        ])

    def _generate_table_definition(self):
        columns = OrderedDict([
            ('id', 'TEXT'),
            ('name', 'TEXT'),
            ('ip', 'TEXT'),
            ('status', 'TEXT'),
            ('image_id', 'TEXT'),
            ('instance_type_id', 'TEXT'),
            ('instance_id', 'TEXT'),
            ('user', 'TEXT'),
            ('config', 'TEXT')
        ])
        return TableDefinition('virtual_machines', columns=columns)

    def new(self, **kwargs):
        if not 'name' in kwargs:
            kwargs['name'] = self._wordlist.pop()
        return ModelCollection.new(self, **kwargs)
