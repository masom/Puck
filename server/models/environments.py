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

class Environment(Model):
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

class Environments(ModelCollection):

    _model = Environment

    def _generate_table_definition(self):
        columns = {
            'id': "TEXT PRIMARY KEY",
            'name': "TEXT"
        }

        return TableDefinition('environments', columns=columns)

    def _after_init(self):
        ''' TODO: Move this to the config file.'''
        items = [
            self.new(id='dev',name='Development'),
            self.new(id='testing', name='Testing'),
            self.new(id='qa', name='Quality Assurance'),
            self.new(id='staging', name='Staging'),
            self.new(id='prod', name='Production')
        ]

        for i in items:
            self.add(i)
