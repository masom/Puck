'''
Puck: FreeBSD virtualization guest configuration server
Copyright (C) 2011  The Hotel Communication Network inc.

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
from libs.instance import Instance, InstanceType
from libs.image import Image
class Launcher(object):

    def create(self, **kwargs):
        raise NotImplementedError()

    def exists(self, **kwargs):
        raise NotImplementedError()

    def status(self, **kwargs):
        raise NotImplementedError()

    def start(self, **kwargs):
        raise NotImplementedError()

    def stop(self, **kwargs):
        raise NotImplementedError()

    def delete(self, **kwargs):
        raise NotImplementedError()

    def restart(self, **kwargs):
        raise NotImplementedError()

    def instance_types(self, **kwargs):
        raise NotImplementedError()

    def images(self, **kwargs):
        raise NotImplementedError()

    def _generate_instances(self, items = []):
        '''Instance generator.'''

        return [Instance(item) for item in items]

    def _generate_instance_types(self, items = []):
        '''Instance Type generator.'''

        return [InstanceType(id=item.id, name=item.name) for item in items]

    def _generate_images(self, items=[]):
        ''' Image generator. '''

        return [Image(id=item.id, name=item.name) for item in items]
