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

class Firewall(Model):
    def __init__(self, id=None, name ="", data = ""):
        self.data = data
        self.name = name
        self.id = id

class Firewalls(ModelCollection):

    _model = Firewall


    def _generate_table_definition(self):
        columns = OrderedDict([
            ('id', "TEXT"),
            ('name', "TEXT"),
            ('data', "TEXT")
        ])

        return TableDefinition('firewalls', columns=columns)

