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
import threading, Queue as queue, time, subprocess, shlex, datetime, urllib, tarfile, os, shutil
import cherrypy
from cherrypy.process import wspbus, plugins
from jails import EzJail
from lib.interfaces import NetInterfaces

class SetupTask(object):

    def __init__(self, puck, queue):
        self.queue = queue
        self._puck = puck
        self.vm = puck.getVM()

    def run(self):
        raise NotImplementedError("`run` must be defined.")

    def log(self, msg):
        now = datetime.datetime.now()
        self.queue.put("%s\t%s\t%s" % (now.strftime("%Y-%m-%d %H:%M:%S"), self.__class__.__name__, msg))

class RcReader(object):
    def _get_rc_content(self):
        rc = None
        with open('/etc/rc.conf', 'r') as f:
            rc = f.read().split()
        if not rc:
            raise RuntimeError("File `/etc/rc.conf` is empty!")
        return rc

class EZJailTask(SetupTask, RcReader):
    '''
    Setups ezjail in the virtual machine.
    TODO: As installing ezjail builds world each time, it would probably be better to store
    the resulting basejail.
    '''
    def run(self):
        self.log('Started')

        try:
            self._enable_ezjail()
            EzJail().install(cherrypy.config.get('setup_plugin.ftp_mirror'))
        except (IOError, OSError) as e:
            self.log("Error while installing ezjail: %s" % e)
            return False
        self.log('Completed')
        return True

    def _enable_ezjail(self):
        rc = self._get_rc_content()
        for line in rc:
            if line.startswith('ezjail_enable'):
                return

        '''if we get here, it means ezjail_enable is not in rc.conf'''
        with open('/etc/rc.conf', 'a') as f:
            f.write("ezjail_enable=\"YES\"\n")

class InterfacesSetupTask(SetupTask, RcReader):
    '''Configures network interfaces for the jails.'''

    def run(self):
        self.log('Started')

        # @TODO: Move netmask to jail config.
        netmask = '255.255.0.0'
        (jails_ip, missing) = self._get_missing_ip()
        self._add_missing_ips(missing, netmask)
        self._add_missing_rc(jails_ip, netmask)
        return True

    def _add_missing_rc(self, jails_ip, netmask):
        rc_addresses = []
        rc = self._get_rc_content()
        alias_count = self._calculate_alias_count(rc_addresses, rc)

        with open('/etc/rc.conf', 'a') as f:
            for ip in jails_ip:
                if self._add_rc_ip(rc_addresses, f, alias_count, ip, netmask):
                    alias_count += 1

    def _add_missing_ips(self, missing, netmask):
        for ip in missing:
            self.log("Registering new ip address `%s`" % ip)
            self._add_ip(ip, netmask)

    def _get_missing_ip(self):
        interfaces = NetInterfaces.getInterfaces()
        missing = []
        jails_ip = []

        for jail in self.vm.jails:
            jails_ip.append(jail.ip)
            if not jail.ip in interfaces:
                missing.append(jail.ip)
        return (jails_ip, sorted(set(missing)) )

    def _calculate_alias_count(self, addresses, rc):
        alias_count = 0

        for line in rc:
            if line.startswith('ifconfig_%s_alias' % self.vm.interface):
                alias_count += 1
                addresses.append(line)

        return alias_count

    def _add_ip(self, ip, netmask):
        command = "ifconfig %s alias %s netmask %s" % (self.vm.interface, ip, netmask)
        self.log('executing: `%s`' % command)
        subprocess.Popen(shlex.split(str(command))).wait()

    def _add_rc_ip(self, rc_addresses, file, alias_count, ip, netmask):

        for item in rc_addresses:
            if item.find(ip) > 0:
                self.log("rc already knows about ip `%s`" % ip)
                return False
        self.log("Registering new rc value for ip `%s`" % ip)
        template = 'ifconfig_%s_alias%s="inet %s netmask %s"'
        line = "%s\n" % template
        file.write(line % (self.vm.interface, alias_count, ip, netmask))
        file.flush()
        return True

class EZJailSetupTask(SetupTask):
    '''
    Setups ezjail in the virtual machine
    '''
    def run(self):
        self.log('Started')

        base_dir = cherrypy.config.get('setup_plugin.jail_dir')
        dst_dir = '%s/flavours' % base_dir

        if not os.path.isdir(dst_dir):
            try:
                os.makedirs(dst_dir)
            except OSError as e:
                self.log('Critical error! Could not create folder `%s`' % dst_dir)
                return False

        # Holds the temporary file list
        tmpfiles = self._retrieveFlavours()
        if not tmpfiles:
            self.log('No flavours downloaded.')
            return False


        # Verify and extract the flavour tarball
        for file in tmpfiles:
            # Verify
            if not tarfile.is_tarfile(file['tmp_file']):
                self.log("Critical error! File `%s` is not a tarfile." % file['tmp_file'])
                return False

            # Extraction
            try:
                with tarfile.open(file['tmp_file'], mode='r:*') as t:
                    '''Will raise KeyError if file does not exists.'''
                    if not t.getmember(file['type']).isdir():
                        raise tarfile.ExtractError("Tar member `%s` is not a folder." % file['type'])
                    t.extractall("%s/" % dst_dir)
            except (IOError, KeyError, tarfile.ExtractError) as e:
                self.log("Critical error! File `%s` could not be extracted. Reason: %s" % (file['tmp_file'], e))

            # Remove the temporary tarball
            try:
                os.unlink(file['tmp_file'])
            except OSerror as e:
                self.log("error while removing file `%s`: %s" %(file['tmp_file'], e))

        self.log('Completed')
        return True

    def _retrieveFlavours(self):
        '''Retrieve the tarball for each flavours'''

        tmpfiles = []

        for jail in self.vm.jails:

            try:
                (filename, headers) = urllib.urlretrieve(jail.url)
            except (urllib.ContentTooShortError, IOError) as e:
                self.log("Error while retrieving jail `%s`: %s" % (jail.name, e))
                return False

            tmpfiles.append({'type': jail.jail_type, 'tmp_file': filename})
            self.log("Jail `%s` downloaded at `%s`" % (jail.name, filename))
        return tmpfiles

class JailConfigTask(SetupTask):
    '''
    Handles jails configuration
    '''

    def run(self):
        self.log('Started')

        jail_dir = cherrypy.config.get('setup_plugin.jail_dir')
        flavour_dir = "%s/flavours" % jail_dir

        for jail in self.vm.jails:
            self.log("Configuring jail `%s`." % jail.jail_type)

            path = "%s/%s" % (flavour_dir, jail.jail_type)
            authorized_key_file = "%s/installdata/authorized_keys" % path
            resolv_file = "%s/etc/resolv.conf" % path
            yum_file = "%s/installdata/yum_repo" % path

            # Verify the flavours exists.
            exists = os.path.exists(path)
            is_dir = os.path.isdir(path)
            if not exists or not is_dir:
                self.log("Flavour `%s` directory is missing in `%s." % (jail.jail_type, flavour_dir))
                return False

            self.log("Retrieving yum repository for environment `%s`." % self.vm.environment)
            yum_repo = self._puck.getYumRepo(self.vm.environment)

            self.log("Writing ssh keys.")
            if not self._writeKeys(jail, authorized_key_file):
                return False

            self.log("Copying resolv.conf.")
            if not self._writeResolvConf(jail, resolv_file):
                return False

            self.log("Writing yum repository.")
            if not self._writeYumRepoConf(yum_repo, yum_file):
                return False

            self.log("Creating jail.")
            if not self._createJail(jail):
                return False
        self.log('Completed')
        return True

    def _writeKeys(self, jail, authorized_key_file):
        '''Write authorized keys'''

        try:
            with open(authorized_key_file, 'w') as f:
                for key in self.vm.keys.values():
                    f.write("%s\n" % key['key'])
        except IOError as e:
            self.log("Error while writing authorized keys to jail `%s`: %s" % (jail.jail_type, e))
            return False
        return True

    def _writeResolvConf(self, jail, resolv_file):
        '''Copy resolv.conf'''

        try:
            shutil.copyfile('/etc/resolv.conf', resolv_file)
        except IOError as e:
            self.log("Error while copying host resolv file: %s" % e)
            return False
        return True

    def _writeYumRepoConf(self, yum_repo, yum_file):
        '''Setup yum repo.d file ezjail will use.'''

        try:
            with open(yum_file, 'w') as f:
                f.write(yum_repo['data'])
        except (KeyError, IOError) as e:
            self.log("Error while writing YUM repo data: %s" % e)
            return False
        return True

    def _createJail(self, jail):
        '''Create the jail'''
        try:
            jail.create()
        except OSError as e:
            self.log("Error while installing jail `%s`: %s" % (jail.jail_type, e))
            return False
        return True

class JailStartupTask(SetupTask):
    '''
    Handles starting each jail.
    '''

    def run(self):
        self.log('Started')

        # Start each jail
        for jail in self.vm.jails:
            self.log("Starting jail `%s`" % jail.jail_type)
            try:
                jail.start()
            except OSError as e:
                self.log("Could not start jail `%s`: %s" % (jail.jail_type, e))
                return False
            self.log("Jail `%s` started" % (jail.jail_type))
            if not jail.status():
                self.log("Jail `%s` is not running!" % jail.jail_type)
                return False

        self.log('Completed')

class SetupWorkerThread(threading.Thread):
    """
    Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition.
    """

    def __init__(self, bus, queue, outqueue, puck):
        super(self.__class__, self).__init__()
        self._stop = threading.Event()
        self._queue = queue
        self._bus = bus
        self._outqueue = outqueue
        self._puck = puck
        self.successful = False

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def _step(self):
        '''
        Run a task
        @raise RuntimeError when the task failed to complete
        '''

        # This will probably need to be wrapped in a try/catch.
        task = self._queue.get(True, 10)(self._puck, self._outqueue)

        loginfo = (self.__class__.__name__, task.__class__.__name__)

        if not task.run():
            raise RuntimeError("%s error while running task `%s`" % loginfo)
        self._queue.task_done()

    def run(self):
        self._bus.log("%s started." % self.__class__.__name__)
        try:
            while not self.stopped():
                self._step()
        except RuntimeError as err:
            self._bus.log(str(err))
            self._empty_queue()
            self.successful = False
            self._puck.getVM().status = 'setup_failed'
            return False
        except queue.Empty:
            pass

        self.successful = True
        self._puck.getVM().status = 'setup_complete'
        self._outqueue.put("%s finished." % self.__class__.__name__)

    def _empty_queue(self):
        while not self._queue.empty():
            try:
                self._queue.get(False)
            except queue.Empty:
                return

class SetupPlugin(plugins.SimplePlugin):
    '''
    Handles tasks related to virtual machine setup.

    The plugin launches a separate thread to asynchronously execute the tasks.
    '''

    def __init__(self, puck, bus, freq=30.0):
        plugins.SimplePlugin.__init__(self, bus)
        self.freq = freq
        self._puck = puck
        self._queue = queue.Queue()
        self._workerQueue = queue.Queue()
        self.worker = None
        self.statuses = []

    def start(self):
        self.bus.log('Starting up setup tasks')
        self.bus.subscribe('setup', self.switch)

    start.priority = 70

    def stop(self):
        self.bus.log('Stopping down setup task.')
        self._setup_stop();

    def switch(self, *args, **kwargs):
        '''
        This is the task switchboard. Depending on the parameters received,
        it will execute the appropriate action.
        '''

        if not 'action' in kwargs:
            self.log("Parameter `action` is missing.")
            return

        # Default task
        def default(**kwargs):
            return

        return {
         'start': self._setup_start,
         'stop': self._setup_stop,
         'status': self._setup_status,
         'clear': self._clear_status
        }.get(kwargs['action'], default)()

    def _clear_status(self, **kwargs):
        '''Clear the status list'''
        del(self.statuses[:])

    def _setup_stop(self, **kwargs):
        self.bus.log("Received stop request.")
        if self.worker and self.worker.isAlive():
            self.worker.stop()

    def _start_worker(self):
        self.worker = SetupWorkerThread( bus=self.bus, queue = self._queue, outqueue = self._workerQueue, puck = self._puck)
        self.worker.start()

    def _setup_start(self, **kwargs):
        self.bus.log("Received start request.")

        # Start the worker if it is not running.
        if not self.worker:
            self._start_worker()
        if not self.worker.is_alive() and not self.worker.successful:
            self._start_worker()

        tasks = [
            EZJailTask,
            EZJailSetupTask,
            InterfacesSetupTask,
            JailConfigTask,
            JailStartupTask
        ]

        # @TODO: Persistence of the list when failure occurs.
        for task in tasks:
            self._queue.put(task)

    def _setup_status(self, **kwargs):
        '''
        Returns the current log queue and if the setup is running or not.
        '''
        if self.worker and self.worker.successful:
            return (self.statuses, False)

        status = self._readQueue(self._workerQueue)
        while status:
            self.statuses.append(status)
            self.bus.log("\t%s" % status)
            status = self._readQueue(self._workerQueue)

        if not self.worker or not self.worker.isAlive():
            return (self.statuses, False)

        return (self.statuses, True)

    def _readQueue(self, q, blocking = True, timeout = 0.2):
        '''
        Wraps code to read from a queue, including exception handling.
        '''

        try:
            item = q.get(blocking, timeout)
        except queue.Empty:
            return None
        return item
