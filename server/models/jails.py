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
from  collections import OrderedDict
class Jail(Model):
    def __init__(self, name=None, ip=None, netmask=None, environment=None, id=None, jail_type=None, url=None):
        self.id = id
        self.jail_type = jail_type
        self.name = name
        self.ip = ip
        self.netmask = netmask
        self.environment = environment
        self.url = url

    def validates(self):
        fields = ['jail_type', 'environment', 'name', 'ip', 'netmask', 'url']
        for f in fields:
            if len(getattr(self, f)):
                continue
            self._errors.append('`%s` cannot be empty.' % f)

        if self._errors:
            return False
        return True

class Jails(ModelCollection):
    _model = Jail

    def _generate_table_definition(self):
        columns = OrderedDict([
            ('id', 'TEXT'),
            ('jail_type', 'TEXT'),
            ('name', 'TEXT'),
            ('ip', 'TEXT'),
            ('netmask', 'TEXT'),
            ('environment', 'TEXT')
        ])
        return TableDefinition('jails', columns=columns)
