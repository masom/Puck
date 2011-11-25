import threading, Queue as queue, time, subprocess, shlex, datetime, urllib, tarfile, os
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
        self.log('Completed')

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
