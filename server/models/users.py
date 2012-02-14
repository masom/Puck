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
import models
import json, hashlib
class User(Model):
    def __init__(self, id=None,user_group="user",name=None,username=None,email=None,password=None, virt_auth_data=None):
        self.id = id
        self.user_group = user_group
        self.name = name
        self.email = email
        self.username= username
        self.password = password
        self.virt_auth_data = virt_auth_data
        self.auth = None

    def validates(self):
        for a in ['name', 'email', 'username']:
            if len(getattr(self, a)) > 0:
                continue
            self._errors.append('`%s` cannot be empty' % a)

        if self._errors:
            return False
        return True

    def validate_password(self):
        if self.password != self.password_repeat:
            self._errors.append('Passwords do not match.')
            return False
        del self.password_repeat
        self.password = self._collection.hash_password(self.password)

        return True

    def generate_auth(self):
        if not self.id:
            return False

        if self.auth:
            return self.auth

        self.auth = models.Credential(id=self.id, name=self.name, email=self.email,
            data=self.virt_auth_data
        )
        return self.auth

    def set_meta_data(self, data):
        try:
            self.virt_auth_data = json.dumps(data)
        except ValueError as e:
            return False
        return True

    def get_meta_data(self):
        try:
            data = json.loads(self.virt_auth_data)
        except (ValueError, KeyError) as e:
            return {}
        return data

class Users(ModelCollection):
    _model = User


    def _generate_table_definition(self):
        columns = OrderedDict([
            ('id', 'TEXT'),
            ('user_group', 'TEXT'),
            ('username', 'TEXT'),
            ('name', 'TEXT'),
            ('email', 'TEXT'),
            ('password', 'TEXT'),
            ('virt_auth_data', 'TEXT')
        ])
        return TableDefinition('users', columns=columns)

    def hash_password(self, password):
        return hashlib.sha1(password).hexdigest()
