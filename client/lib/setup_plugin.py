import threading, Queue as queue, time
from cherrypy.process import wspbus, plugins

class SetupTask(object):
    _nameCounter = 0

    def __init__(self, name = 'DefaultTask'):
        self.name = "%s-%s" % (name, self.__class__._nameCounter)
        self.__class__._nameCounter += 1
    def run(self):
        raise RuntimeError("`run` must be defined.")

class EZJailTask(SetupTask):
    '''
    Setups ezjail in the virtual machine
    '''
    def run(self):
        pass

class SetupWorkerThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, bus=None, queue=None):
        super(self.__class__, self).__init__()
        self._stop = threading.Event()
        self._queue = queue
        self._bus = bus

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
        self._bus.log("%s started." % self.__class__)
        task = self._getTask()
        while task:
            self._bus.log("SetupWorkerThread received task: %s" % task)
            time.sleep(1) 
            task = self._getTask()

class SetupPlugin(plugins.SimplePlugin):

    def __init__(self, bus, freq=30.0):
        plugins.SimplePlugin.__init__(self, bus)
        self.freq = freq
        self._queue = queue.Queue()
        self.worker = SetupWorkerThread( bus=bus, queue = self._queue)

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

        {
         'start': self._setup_start,
         'stop': self._setup_stop,
         'status': self._setup_status
        }.get(kwargs['action'], default)()

    def _setup_stop(self, **kwargs):
        self.bus.log("Stop called. Giving back time.")
        if self.worker.isAlive():
            self.worker.stop()

    def _setup_start(self, **kwargs):
        
        if not self.worker.isAlive():
            self.bus.log("Start called. Starting worker.")
            self.worker.start()

        self.bus.log("Building task list")
        tasks = [
            EZJailTask()
        ]
        self.bus.log("Publishing tasks")
        for task in tasks:
            self.bus.log("\t Publishing: %s" % task.name)
            self._queue.put(task)

    def _setup_status(self, **kwargs):
        self.bus.log('Status called. Wants its time back.')