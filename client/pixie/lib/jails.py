'''
Pixie: FreeBSD virtualization guest configuration client
Copyright (C) 2011  The Hotel Communication Network inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.f

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import sys, os, shlex, subprocess
import cherrypy
'''For the EzjailCreator workaround'''
import socket, json

class Jails(object):
    '''
    List of jails in the system
    '''
    def __init__(self):
        self._jails = {}
        self._manager = EzJail()
        self._jail = Jail

    def __iter__(self):
        for i in self._jails:
            yield self._jails[i]

    def count(self):
        '''Returns the number of jails'''
        return len(self._jails)

    def setSocket(self, ezjl_socket):
        '''Sets the create socket to the jail manager. Ugly hack.'''
        self._manager.setSocket(ezjl_socket)

    def load(self, jails):
        '''
        Load jails from a saved vm.
        '''
        for j in jails:
            self.add(self.create(j))

    def create(self, config):
        '''Creates a new jail, returning it'''
        return self._jail(self._manager, config)

    def add(self, jail):
        '''Add a jail
        raises KeyError if the jail already exists.'''
        if jail.id in self._jails:
            raise KeyError()
        self._jails[jail.id] = jail

    def remove(self, jail):
        '''Remove a jail.
        raises KeyError if the jail does not exists.'''
        if not jail.id in self._jails:
            raise KeyError()

        try:
            self._jails[jail.id].stop()
            self._jails[jail.id].delete()
        except KeyError as e:
            pass
        del(self._jails[jail.id])

    def contain(self, id):
        return id in self._jails

    def clear(self):
        '''Clear the jail registry'''
        self._jails.clear()

    def export(self):
        '''Exports the jail as a list'''
        jails = []
        for j in self._jails:
            jails.append(self._jails[j].export())
        return jails

    def get(self, id=None):
        '''Gets a jail
        raises KeyError if the jail was not found.'''
        if not id:
            return self._jails.values()

        if not id in self._jails:
            raise KeyError()

        return self._jails[id]

    def status(self):
        '''Returns the status of the jails.'''
        return self._manager.status()

class Jail(object):
    def __init__(self, manager, config):
        self._data = {}

        keys = ['id', 'url', 'jail_type', 'name', 'ip', 'netmask']
        for k in keys:
            if not k in config:
                raise KeyError("Configuration value `%s` is not set." % k)
            self._data[k] = config[k]

        self._manager = manager

    def export(self):
        '''Export the jail data.'''
        return self._data

    def __getattr__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return object.__getattribute__(self, "_data")[name]

    def __setattr__(self, name, value):
        if hasattr(self, name) or name in ['_data','_manager']:
            return object.__setattr__(self, name, value)
        object.__getattribute__(self, "_data")[name] = value
        return

    def start(self):
        '''Starts the jail'''
        return self._manager.start(self._data['jail_type'])

    def stop(self):
        '''Stops the jail'''
        return self._manager.stop(self._data['jail_type'])

    def status(self):
        '''Get the jail status'''
        return self._manager.status(self._data['jail_type'])

    def create(self):
        '''Create a jail
        Here we make the assumption the type is the same as the flavour...
        Will need to refactor for more global use than HCN's
        '''
        return self._manager.create(self._data['jail_type'], self._data['jail_type'], self._data['ip'])

    def delete(self):
        return self._manager.delete(self._data['jail_type'])

class EzJail(object):

    def __init__(self):
        self._prog = '/usr/local/bin/ezjail-admin'

    def setSocket(self, ezjl_socket):
        '''Set the socket used to communicate with the fork handling jail start.'''
        self._socket = ezjl_socket

    def install(self, mirror='ftp.freebsd.org'):
        '''
        Installs ezjail
        @raise OSError when command not found.
        '''
        options = " ".join(cherrypy.config.get('setup_plugin.ezjail_options'))
        command = '%s install %s -h %s' % (self._prog, options, mirror)
        cherrypy.log(command)

        subprocess.Popen(shlex.split(command)).wait()

    def start(self, jail = None):
        '''
        Starts the jails or a specific jail
        @raise OSError when command not found.
        '''
        cherrypy.log("Sending start request to ezjail starter.")
        if not self._send_socket({'id': 'start', 'name': jail}):
            return False

        status = self._read_socket()
        if not status:
            return False
        cherrypy.log("Status from ezjail starter: %s" % status)

        if status['status'] == 'starting':
            cherrypy.log("Jail %s is starting. This may take a while." % jail)
        else:
            cherrypy.log("Jail `%s` status: `%s`" % (jail, status['status']))
            return False

        # This will probably block for a little while...
        status = self._read_socket()
        if status['status'] == 'started':
            cherrypy.log("Jail %s is started." % jail)
            return True
        msg = "An error occured while starting jail %s: %s"
        cherrypy.log(msg % (jail, status['status']))
        return False

    def _send_socket(self, data):
        try:
            self._socket.send(json.dumps(data))
        except IOError as e:
            msg = "I/O Error: %s"
            cherrypy.log(msg % e)
            return False
        return True

    def _read_socket(self):
        try:
            data = self._socket.recv(512)
            status = json.loads(data)
        except ValueError as e:
            cherrypy.log("Received garbage from ezjail starter.")
            return False
        except IOError as e:
            cherrypy.log("I/O Error while communicating with ezjail starter.")
            return False
        return status

    def stop(self, jail = None):
        '''
        Stops the jails or a specific jail
        @raise OSError when command not found.
        '''

        command = "%s stop" % self._prog
        if jail:
            command += " %s" % str(jail)
        cherrypy.log(command)
        subprocess.Popen(shlex.split(command)).wait()

    def status(self, jail = None):
        '''
        Gives the status the installed jails.
        @raise OSError when command not found.
        @raise KeyError when jail not found.
        @return list
        '''

        command = "%s list" % self._prog
        output = subprocess.check_output(shlex.split(command))

        if len(output) == 0:
            raise RuntimeError("No data returned by ezjail.")

        data = output.splitlines(False)
        if not jail:
            return data

        for line in data[2:]:
            found = line.find(jail)
            if found < 0:
                continue
            return data[:2] + [line]
        raise KeyError("Jail not found.")

    def create(self, flavour, name, ip):
        '''
        Creates a new jail based off a flavour, name and ip
        @raise OSError when command not found.
        '''

        # ezjail-admin create -f [flavour] [name] [ip]

        # shlex does not support unicode with python < 2.7.3
        cmd = str("%s create -f %s %s %s" % (self._prog, flavour, name, ip))
        cherrypy.log(cmd)

        subprocess.Popen(shlex.split(cmd)).wait()

    def delete(self, jail):
        '''
        Deletes a jail from the system
        '''

        commands = [
            "%s stop %s" % (self._prog, jail),
            "%s delete -w %s" % (self._prog, jail)
        ]
        for command in commands:
            cherrypy.log(command)
            subprocess.Popen(shlex.split(str(command))).wait()

class StopLoopException(Exception): pass
class EzJailStarter(object):
    '''Workaround for python thread breaking jail start.'''

    def getSocketFile(self):
        '''Generate a file to be used as UNIX socket'''

        self._socket_file = "/tmp/pixie_ezc_%s" % os.getpid()
        return self._socket_file

    def teardown(self):
        self._socket.close()

    def run(self):
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._socket.bind(self._socket_file)
        self._socket.listen(1)

        (conn, addr) = self._socket.accept()
        self._conn = conn
        while True:
            try:
                data = conn.recv(4096)
            except:
                break

            cherrypy.log("EzJailStarter\tReceived data: `%s`" % data)

            (execute, command) = self._handle(data)
            if execute:
                try:
                    if execute(command):
                        conn.send(json.dumps({"status": "started"}))
                    else:
                        conn.send(json.dumps({"status": "failed"}))
                except StopLoopException:
                    break
        conn.close()

    def _handle(self, data):
        '''
        Handles incoming requests
        '''
        try:
            command  = json.loads(data)
        except ValueError as e:
            cherrypy.log("EzJailStarter\tError: %s" % e)
            return (False, False)

        if not 'id' in command:
            cherrypy.log("EzJAilStarter\tError: Command id missing.")
            return (False, False)

        execute = {
            'shutdown': self._stop,
            'start': self._startJail
        }.get(command['id'], False)

        return (execute, command)

    def _startJail(self, data):
        '''
        Starts a jail
        '''
        cmd = "/usr/local/bin/ezjail-admin start %s" % str(data['name'])
        self._conn.send(json.dumps({"status": "starting", "command": cmd}))
        cherrypy.log("EzJailStarter\tExecuting: %s" % cmd)
        try:
            subprocess.Popen(shlex.split(cmd)).wait()
        except Exception as e:
            cherrypy.log("EZJailStarter\tError: %s" % e)
            return False
        cherrypy.log("EZJailStarter\tJail `%s` Started." % data['name'])
        return True

    def _stop(self, data):
        '''
        Request the jailstarter to be stopped.
        '''
        raise StopLoopException()
