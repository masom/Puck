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
from cherrypy.process import wspbus, plugins
from jails import EzJail

class SetupTask(object):
    _nameCounter = 0

    def __init__(self, puck, id = 'SetupTask'):
        self.id = "%s-%s" % (id, self.__class__._nameCounter)
        self.__class__._nameCounter += 1
        self.name = self.__class__.__name__

        self.puck = puck
        self.vm = puck.getVM()

    def setOutQueue(self, queue):
        self.queue = queue

    def setEzJail(self, ezjail):
        self.ezjail = ezjail

    def run(self):
        raise NotImplementedError("`run` must be defined.")

    def log(self, msg):
        now = datetime.datetime.now()
        self.queue.put("%s\t%s\t%s" % (now.strftime("%Y-%m-%d %H:%M:%S"), self.__class__.__name__, msg))

class EZJailTask(SetupTask):
    '''
    Setups ezjail in the virtual machine
    '''
    def run(self):
        self.log('Started')
        try:
            self.ezjail.install()
        except OSError as e:
            self.log("Error while installing ezjail: %s" % e)
            return False
        self.log('Completed')
        return True

class EZJailSetupTask(SetupTask):
    '''
    Setups ezjail in the virtual machine
    '''
    def run(self):
        self.log('Started')
        #TODO: Move this to a cherrypy configuration value
        dst_dir = '/usr/local/jails/flavours'

        '''Holds the temporary file list'''
        tmpfiles = self._retrieveFlavours()
        if not tmpfiles:
            return False

        '''Verify and extract the flavour tarball'''
        for file in tmpfiles:
            '''Verify'''
            if not tarfile.is_tarfile(file['tmp_file']):
                self.log("Critical error! File `%s` is not a tarfile." % file['tmp_file'])
                return False

            '''Extraction'''
            with tarfile.open(file['tmp_file'], mode='r:*') as t:
                t.extractall("%s/%s" % (dst_dir, file['type']))

            '''Remove the temporary tarball'''
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
            except urllib.ContentTooShortError as e:
                self.log("Error while retrieving jail `%s`: %s" % (jail.name, e))
                return False

            tmpfiles.append({'type': jail.type, 'tmp_file': filename})
            self.log("Jail `%s` downloaded at `%s`" % (jail.name, filename))
        return tmpfiles

class JailConfigTask(SetupTask):
    '''
    Handles jails configuration
    '''

    def run(self):
        self.log('Started')

        #TODO: Move these to a cherrypy configuration value
        jail_dir = '/usr/local/jails'
        flavour_dir = "%s/flavours" % jail_dir

        for jail in self.vm.jails:
            path = "%s/%s" % (flavour_dir, jail.type)
            authorized_key_file = "%s/installdata/authorized_keys" % path
            resolv_file = "%s/etc/resolv.conf" % path
            yum_file = "%s/installdata/yum_repo" % path

            '''Verify the flavours exists.'''
            exists = os.path.exists(path)
            is_dir = os.path.isdir(path)
            if not exists or not is_dir:
                self.log("Flavour `%s` directory is missing in `%s" % (jail.type, flavour_dir))
                return False

            if not self._writeKeys(authorized_key_file):
                return False

            if not self._writeResolvConf(resolv_file):
                return False

            if not self._writeYumRepoConf(yum_file):
                return False

            if not self._createJail(jail):
                return False
        self.log('Completed')
        return True

    def _writeKeys(self, authorized_key_file):
        '''Write authorized keys'''

        try:
            with open(authorized_key_file, 'w') as f:
                for key in self.vm.keys.values():
                    f.write("%s\n" % key['key'])
        except IOError as e:
            self.log("Error while writing authorized keys to jail `%s`: %s" % (jail.type, e))
            return False
        return True

    def _writeResolvConf(self, resolv_file):
        '''Copy resolv.conf'''

        try:
            shutil.copyfile('/etc/resolv.conf', resolv_file)
        except IOError as e:
            self.log("Error while copying host resolv file: %s" % e)
            return False
        return True

    def _writeYumRepoConf(self, yum_file):
        '''Setup yum repo.d file ezjail will use.'''

        try:
            with open(yum_file, 'w') as f:
                f.write(self.vm.yumRepoData)
        except IOError as e:
            self.log("Error while writing YUM repo data: %s" % e)
            return False
        return True

    def _createJail(self, jail):
        '''Create the jail'''
        flavour = jail.type
        name = jail.type
        ip = jail.ip
        try:
            #TODO: Use jail.create() instead of new ezjail instance.
            self.ezjail.create(flavour, name, ip)
        except OSError as e:
            self.log("Error while installing jail `%s`: %s" % (jail.type, e))
            return False
        return True

class JailStartupTask(SetupTask):
    '''
    Handles starting each jail.
    '''

    def run(self):
        self.log('Started')

        '''Start each jail'''
        for jail in self.vm.jails:
            self.log("Starting jail `%s`" % jail.type)
            try:
                #TODO: Use jail.start() instead of new ezjail instance.
                self.ezjail.start(jail.type)
            except OSError as e:
                self.log("Could not start jail `%s`: %s" % (jail.type, e))
                return False
            self.log("Jail `%s` started" % (jail.type))
            if not self.ezjail.status(jail.type):
                self.log("Jail `%s` is not running!" % jail.type)
                return False

        self.log('Completed')

class SetupWorkerThread(threading.Thread):
    """
    Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition.
    """

    def __init__(self, bus, queue, outqueue, ezjail):
        super(self.__class__, self).__init__()
        self._stop = threading.Event()
        self._queue = queue
        self._bus = bus
        self._outqueue = outqueue
        self._ezjail = ezjail

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def _step(self):
        '''
        Run a task
        @raise RuntimeError when the task failed to complete
        '''
        task = self._queue.get(True, 10)
        task.setOutQueue(self._outqueue)
        task.setEzJail(self._ezjail)

        loginfo = (self.__class__.__name__, task.__class__.__name__)
        self._bus.log("%s received task: %s" % loginfo)
        self._outqueue.put("%s starting task: %s" % loginfo)

        if not task.run():
            raise RuntimeError("%s error while running task `%s`" % loginfo)
        self._queue.task_done()

    def run(self):
        self._bus.log("%s started." % self.__class__.__name__)
        try:
            while not self.stopped():
                self._step()
                time.sleep(1) 
        except RuntimeError as err:
            self._bus.log(str(err))
            self._queue.empty()
        except queue.Empty:
            self._bus.log("Shutting down.  no task.")

class SetupPlugin(plugins.SimplePlugin):
    '''
    Handles tasks related to virtual machine setup.

    The plugin launches a separate thread to asynchronously execute the tasks.
    '''

    def __init__(self, vm, bus, freq=30.0):
        plugins.SimplePlugin.__init__(self, bus)
        self.freq = freq
        self.vm = vm
        self._queue = queue.Queue()
        self._workerQueue = queue.Queue()
        self.worker = None
        self.statuses = []
        self._ezjail = EzJail()

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

        '''Default task'''
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

    def _setup_start(self, **kwargs):
        self.bus.log("Received start request.")

        '''Start the worker if it is not running.'''
        if not self.worker or not self.worker.isAlive():
            self.bus.log("Start called. Starting worker.")
            self.worker = SetupWorkerThread( bus=self.bus, queue = self._queue, outqueue = self._workerQueue, ezjail = self._ezjail)
            self.worker.start()

        
        tasks = [
            #EZJailTask(self.vm),
            EZJailSetupTask(self.vm),
            JailConfigTask(self.vm),
            JailStartupTask(self.vm)
        ]

        self.bus.log("Publishing tasks")
        #TODO: Persistence of the list when failure occurs.
        for task in tasks:
            self.bus.log("\t Publishing: %s" % task.name)
            self._queue.put(task)

    def _setup_status(self, **kwargs):
        '''
        Returns the current log queue
        '''

        status = self._readQueue(self._workerQueue)
        while status:
            self.statuses.append(status)
            self.bus.log("\t%s" % status)
            status = self._readQueue(self._workerQueue)

        if not self.worker or not self.worker.isAlive():
            self.statuses.append("%s worker is not running." % self.__class__.__name__)

        return self.statuses

    def _readQueue(self, q, blocking = True, timeout = 0.2):
        '''
        Wraps code to read from a queue, including exception handling.
        '''

        try:
            item = q.get(blocking, timeout)
        except queue.Empty:
            return None
        return item
