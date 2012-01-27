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
import deque

class VirtualMachine(Model):
    def __init__(self, name, ip, status, config):
        self.name = name
        self.ip = ip
        self.status = status
        self.config = config

class VirtualMachines(ModelCollection):
    _model = VirtualMachine

    def _after_init():
        # TODO: Move this to the config file.
        self._wordlist = deque([
            "apple", "banana", "carrot", "pepper", "salt", "orange",
            "eggplant", "squash", "melon", "peach", "kale", "swiss chard",
            "tomato", "potato", "onion", "grapefruit", "radish", "broccoli",
            "cilantro", "parsley", "plum", "scallion", "haberno", "strawberry",
            "grape", "cranberry", "lemongrass", "sugarcane"
        ])

    def _generate_table_definition(self):
        columns = {
            'name': 'TEXT PRIMARY KEY',
            'ip': 'TEXT',
            'status': 'TEXT',
            'config': 'TEXT'
        }
        return TableDefinition('virtual_machines', columns=columns, primary_key='name')

    def new(self, **kwargs):
        kwargs['name'] = self._wordlist.pop()
        ModelCollection.new(self, **kwargs)
