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

class YumRepository(Model):
    def __init__(self, environment=None, data=None):
        self.environment = environment
        self.data = data

    def validates(self):
        for f in ['environment', 'data']:
            if len(getattr(self, f)) > 0:
                continue
            self._errors.append('`%s` cannot be empty.' % f)
        if self._errors:
            return False
        return True

class YumRepositories(ModelCollection):
    _model = YumRepository
    override_pk = False
    def _generate_table_definition(self):
        columns = OrderedDict([
            ("environment", "TEXT"),
            ("data", "TEXT")
        ])
        return TableDefinition('yum_repositories', columns=columns, primary_key='environment')
