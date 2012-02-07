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
import base64, struct

class Key(Model):
    def __init__(self, name=None, key=None):
        self.name = name
        self.key = key

    def validates(self):
        ''' Validates if the entity holds a valid SSH-RSA key
        See http://stackoverflow.com/questions/2494450/ssh-rsa-public-key-validation-using-a-regular-expression
        '''

        if not self.key:
            return False

        if len(self.key) == 0:
            return False

        if "\n" in self.key:
            return False

        raw = self.key.split()
        if len(raw) not in (2, 3):
            return False

        type = raw[0]
        key = raw[1]

        int_len = 4

        try:
            data = base64.decodestring(key)
            str_len = struct.unpack('>I', data[:int_len])[0]
        except TypeError:
            return False

        return data[int_len:int_len+str_len] == type

class Keys(ModelCollection):
    _model = Key
    override_pk = False
    def _generate_table_definition(self):
        columns = OrderedDict([
            ('name', 'TEXT'),
            ('key', 'TEXT')
        ])
        return TableDefinition('keys', columns=columns, primary_key='name')


