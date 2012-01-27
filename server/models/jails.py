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

from libs.model import ModelCollection, Model
class Jail(Model):
    def __init__(self, name, ip, netmask, environment, id=None, jail_type=None):
        self.id = id
        self.jail_type = jail_type
        self.name = name
        self.ip = ip
        self.netmask = netmask
        self.environment = environment

class Jails(ModelCollection):
    _model = Jail

    def _generate_table_definition(self):
        columns = {
            'id': 'TEXT PRIMARY KEY',
            'jail_type': 'TEXT',
            'name': 'TEXT',
            'ip': 'TEXT',
            'netmask': 'TEXT',
            'environment': 'TEXT'
        }
        return TableDefinition('jails', columns=columns)
