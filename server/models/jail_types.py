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
from collections import OrderedDict
class JailType(Model):
    def __init__(self, id=None, ip=None, netmask=None):
        self.id = id
        self.ip = ip
        self.netmask = netmask

class JailTypes(ModelCollection):
    _model = JailType

    def _generate_table_definition(self):
        columns = OrderedDict([
            ('id', 'TEXT PRIMARY KEY'),
            ('ip', 'TEXT'),
            ('netmask', 'TEXT')
        ])
        return TableDefinition('jail_types', columns=columns)

    def _after_init(self):
        return
        # TODO Move this to database instead of hard coded
        netmask='255.255.255.0'
        self.add(self.new(id='content', ip='10.0.0.10', netmask=netmask))
        self.add(self.new(id='database', ip='10.0.0.11', netmask=netmask))
        self.add(self.new(id='support', ip='10.0.0.12', netmask=netmask))

