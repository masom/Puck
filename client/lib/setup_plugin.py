import threading, Queue as queue, time, subprocess, shlex, datetime
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
        raise RuntimeError("`run` must be defined.")
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

class JailSetupTask(SetupTask):
    '''
    Setups ezjail in the virtual machine
    '''
    def run(self):
        self.log('Started')
        print
        print self.vm.jails
        print
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

    def _getTask(self, blocking = True, timeout = 10):
        try:
            task = self._queue.get(blocking, timeout)
        except queue.Empty as e:
            return None
        return task

    def run(self):
        self._bus.log("%s started." % self.__class__.__name__)
        task = self._getTask()
        while task:
            task.setOutQueue(self._outqueue)
            self._bus.log("%s received task: %s" % (self.__class__.__name__, task.__class__.__name__))
            self._outqueue.put("%s starting task: %s" % (self.__class__.__name__, task.__class__.__name__))

            if not task.run():
                self._bus.log("%s error while running task `%s`" % (self.__class__.__name__, task.__class__.__name__))
                break

            time.sleep(1) 
            task = self._getTask()

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
            JailSetupTask(self.vm)
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