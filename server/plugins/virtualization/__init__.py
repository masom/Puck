'''
Pixie: FreeBSD virtualization guest configuration client
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
import os, imp
import cherrypy
from cherrypy.process import wspbus, plugins

'''http://stackoverflow.com/questions/301134/dynamic-module-import-in-python'''
def load_from_file(filepath, expected):
    class_inst = None

    mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])

    if file_ext.lower() == '.py':
        py_mod = imp.load_source(mod_name, filepath)

    elif file_ext.lower() == '.pyc':
        py_mod = imp.load_compiled(mod_name, filepath)

    if expected in dir(py_mod):
        class_inst = getattr(py_mod, expected)
    return class_inst

class VirtualizationPlugin(plugins.SimplePlugin):

    def __init__(self, bus):
        plugins.SimplePlugin.__init__(self, bus)

        '''Super ugly hack for now.'''
        plugin_name = cherrypy.config.get('virtualization.plugin')
        self._plugin_filename = './plugins/virtualization/%s.py' % plugin_name.lower()
        plugin = load_from_file(self._plugin_filename, plugin_name)
        self.api = plugin()
        self.switchboard = {}

        for key in self.api.supported_api:
            if not hasattr(self.api, key):
                raise NotImplementedError("API is missing definition for `%s`" % key)
            self.switchboard[key] = getattr(self.api, key)

    def start(self):
        self.bus.log('Starting up virtualization task')
        self.bus.subscribe('virtualization', self.switch)
    start.priority = 70

    def get_credential_class(self):
        name = cherrypy.config.get('virtualization.credentials')
        return load_from_file(self._plugin_filename, name)

    def switch(self, *args, **kwargs):
        '''
        This is the task switchboard. Depending on the parameters received,
        it will execute the appropriate action.
        '''

        if not 'action' in kwargs:
            self.log("Parameter `action` is missing.")
            return

        '''Default task'''
        def default(**kwargs):
            return

        return self.switchboard.get(kwargs['action'], default)(**kwargs)
