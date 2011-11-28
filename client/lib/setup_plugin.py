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

class SetupTask(object):
    _nameCounter = 0

    def __init__(self, vm, id = 'SetupTask'):
        self.id = "%s-%s" % (id, self.__class__._nameCounter)
        self.__class__._nameCounter += 1
        self.vm = vm
        self.name = self.__class__.__name__

    def setOutQueue(self, queue):
        self.queue = queue

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
        commands = ['ezjail-admin install -m -p']
        for command in commands:
            try:
                (stdoutdata, stderrdata) = subprocess.Popen(shlex.split(command)).communicate()
            except OSError as e:
                self.log("Error while installing ezjail: %s" % e)
                return False

            print
            print
            print stdoutdata
            print "---------"
            print stderrdata
            print
            print
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

        tmpfiles = []
        for jail in self.vm.jails:
            try:
                (filename, headers) = urllib.urlretrieve(jail['url'])
            except urllib.ContentTooShortError as e:
                self.log("Error while retrieving jail `%s`: %s" % (jail['name'], e))
                return False

            tmpfiles.append({'type': jail['type'], 'tmp_file': filename})

            self.log("Jail `%s` downloaded at `%s`" % (jail['name'], filename))

        for file in tmpfiles:
            if not tarfile.is_tarfile(file['tmp_file']):
                self.log("Critical error! File `%s` is not a tarfile." % file)
                return False

            with tarfile.open(file['tmp_file'], mode='r:*') as t:
                t.extractall("%s/%s" % (dst_dir, file['type']))

        for file in tmpfiles:
            try:
                os.unlink(file['tmp_file'])
            except OSerror as e:
                self.log("error while removing file `%s`: %s" %(file['tmp_file'], e))
        self.log('Completed')
        return True

class JailConfigTask(SetupTask):
    def run(self):
        self.log('Started')
        '''
        TODO:
            for each jail:
                - Add public key to hcn user. the EZJAIL first boot script should read them to include in user created.
                - Get JAIL ip. Make sure the VM network interface is configured with them
                - Make sure resolv.conf is copied from HOST
                - Configure the YUM repositories in the jails flavours
                - The EZJAIL firs boot script should have YUM install the files.
                - Install the jail
        '''
        jail_dir = '/usr/local/jails'
        flavour_dir = "%s/flavours" % jail_dir
        create_command = ["ezjail-admin create -f %s %s %s"]

        '''Check if all flavours dir exists.'''
        for jail in self.vm.jails:
            path = "%s/%s" % (flavour_dir, jail['type'])
            authorized_key_file = "%s/data/authorized_keys" % path
            resolv_file = "%s/etc/resolv.conf" % path
            yum_file = "%s/data/yum_repo" % path

            exists = os.path.exists(path)
            is_dir = os.path.isdir(path)

            if not exists or not is_dir:
                self.log("Flavour `%s` directory is missing in `%s" % (jail['type'], flavour_dir))
                return False

            '''Write authorized keys'''
            try:
                with open(authorized_key_file, 'w') as f:
                    for key in self.vm.keys.values():
                        f.write("%s\n" % key['key'])
            except IOError as e:
                self.log("Error while writing authorized keys to jail `%s`: %s" % (jail['type'], e))
                return False

            '''Copy resolv.conf'''
            try:
                shutil.copyfile('/etc/resolv.conf', resolv_file)
            except IOError as e:
                self.log("Error while copying host resolv file: %s" % e)
                return False

            '''Setup yum repo.d file ezjail will use.'''
            try:
                with open(yum_file, 'w') as f:
                    f.write(self.vm.yumRepoData)
            except IOError as e:
                self.log("Error while writing YUM repo data: %s" % e)
                return False

            try:
                (stdoutdata, stderrdata) = subprocess.Popen(shlex.split(create_command)).communicate()
            except OSError as e:
                self.log("Error while installing ezjail: %s" % e)
                return False

        self.log('Completed')
        return True

class JailStartupTask(SetupTask):
    def run(self):
        self.log('Started')
        '''
        TODO:
            for each jail:
                - Start
                - Verify it is running
        '''
        self.log('Completed')

class SetupWorkerThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, bus, queue, outqueue):
        super(self.__class__, self).__init__()
        self._stop = threading.Event()
        self._queue = queue
        self._bus = bus
        self._outqueue = outqueue

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def _step(self):
        task = self._queue.get(True, 10)
        task.setOutQueue(self._outqueue)

        loginfo = (self.__class__.__name__, task.__class__.__name__)
        self._bus.log("%s received task: %s" % loginfo)
        self._outqueue.put("%s starting task: %s" % loginfo)

        if not task.run():
            raise RuntimeError("%s error while running task `%s`" % loginfo)

    def run(self):
        self._bus.log("%s started." % self.__class__.__name__)
        try:
            while True:
                self._step()
                time.sleep(1) 
        except RuntimeError as err:
            self._bus.log(str(err))
        except queue.Empty:
            self._bus.log("Shutting down.  no task.")

class SetupPlugin(plugins.SimplePlugin):

    def __init__(self, vm, bus, freq=30.0):
        plugins.SimplePlugin.__init__(self, bus)
        self.freq = freq
        self.vm = vm
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
        self.bus.log("Switch called. Linking call.")
        if not 'action' in kwargs:
            return

        def default(**kwargs):
            return

        return {
         'start': self._setup_start,
         'stop': self._setup_stop,
         'status': self._setup_status
        }.get(kwargs['action'], default)()

    def _setup_stop(self, **kwargs):
        self.bus.log("Stop called. Giving back time.")
        if self.worker and self.worker.isAlive():
            self.worker.stop()

    def _setup_start(self, **kwargs):
        
        if not self.worker or not self.worker.isAlive():
            self.bus.log("Start called. Starting worker.")
            self.worker = SetupWorkerThread( bus=self.bus, queue = self._queue, outqueue = self._workerQueue)
            self.worker.start()

        self.bus.log("Building task list")
        tasks = [
            #EZJailTask(self.vm),
            EZJailSetupTask(self.vm),
            JailConfigTask(self.vm),
            JailStartupTask(self.vm)
        ]
        self.bus.log("Publishing tasks")
        for task in tasks:
            self.bus.log("\t Publishing: %s" % task.name)
            self._queue.put(task)

    def _setup_status(self, **kwargs):
        self.bus.log("_setup_status called.")

        status = self._readQueue(self._workerQueue)
        while status:
            self.statuses.append(status)
            self.bus.log("\t%s" % status)
            status = self._readQueue(self._workerQueue)
        return self.statuses

    def _readQueue(self, q, blocking = True, timeout = 1):
        try:
            item = q.get(blocking, timeout)
        except queue.Empty:
            return None
        return item
