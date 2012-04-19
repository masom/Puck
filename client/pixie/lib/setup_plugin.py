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
import threading, Queue as queue, time, subprocess, shlex, datetime
import urllib, tarfile, os, shutil, tempfile, pwd
import cherrypy
from cherrypy.process import wspbus, plugins
from pixie.lib.jails import EzJail
from pixie.lib.interfaces import NetInterfaces

class SetupTask(object):

    def __init__(self, puck, queue):
        self.queue = queue
        self._puck = puck
        self.vm = puck.getVM()

    def run(self):
        raise NotImplementedError("`run` must be defined.")

    def log(self, msg):
        now = datetime.datetime.now()
        cherrypy.log("%s %s" % (self.__class__.__name__, msg))
        tpl =  "%s\t%s\t%s"
        date_format = "%Y-%m-%d %H:%M:%S"
        cls = self.__class__.__name__
        self.queue.put(tpl % (now.strftime(date_format), cls, msg))

class RcReader(object):

    def _has_line(self, lines, line_start):
        for line in lines:
            if line.startswith(line_start):
                return True
        return False

    def _get_rc_content(self):
        rc = None
        try:
            with open('/etc/rc.conf', 'r') as f:
                rc = f.readlines()
        except IOError:
            pass
        if not rc:
            raise RuntimeError("File `/etc/rc.conf` is empty!")
        return rc

class EZJailTask(SetupTask, RcReader):
    '''
    Setups ezjail in the virtual machine.
    '''
    def run(self):

        try:
            self.log("Enabling EZJail.")
            self._enable_ezjail()
            EzJail().install(cherrypy.config.get('setup_plugin.ftp_mirror'))
        except (IOError, OSError) as e:
            self.log("Error while installing ezjail: %s" % e)
            return False
        return True

    def _enable_ezjail(self):
        rc = self._get_rc_content()

        if self._has_line(rc, 'ezjail_enable'):
            self.log("EZJail is already enabled.")
            return

        self.log("Adding to rc: `%s`" % 'ezjail_enable="YES"')
        '''if we get here, it means ezjail_enable is not in rc.conf'''
        with open('/etc/rc.conf', 'a') as f:
            f.write("ezjail_enable=\"YES\"\n")

class SSHTask(SetupTask):
    '''Create the base user `puck` and add the authorized ssh keys'''

    def run(self):
        self._setup_ssh()
        return True

    def _setup_ssh(self):
        if not self.vm.keys:
            self.log("No keys to install.");
            return True

        #@TODO Could be moved to config values instead of hardcoded.
        user = 'puck'
        try:
            pwd.getpwnam(user)
        except KeyError as e:
            cmd = 'pw user add %s -m -G wheel' % user
            self.log("Adding user. Executing `%s`" % cmd)
            subprocess.Popen(shlex.split(str(cmd))).wait()

        user_pwd = pwd.getpwnam(user)

        path = '/home/%s/.ssh' % user
        authorized_file = "%s/authorized_keys" % path
        if not os.path.exists(path):
            os.mkdir(path)
            os.chown(path, user_pwd.pw_uid, user_pwd.pw_gid)

        with open(authorized_file, 'a') as f:
            for key in self.vm.keys:
                self.log("Writing key `%s`" % key)
                f.write('%s\n' % self.vm.keys[key]['key'])

        os.chmod(authorized_file, 0400)
        os.chown(authorized_file, user_pwd.pw_uid, user_pwd.pw_gid)

class FirewallSetupTask(SetupTask, RcReader):
    def run(self):

        # TODO Move this to a congfiguration value from puck. Not high priority
        pf_conf = '/etc/pf.rules.conf'
        rc_conf = '/etc/rc.conf'
        self.setup_rc(rc_conf, pf_conf)
        self.setup_pf_conf(pf_conf)
        self.launch_pf()

        return True

    def launch_pf(self):
        # Stop it in case it
        commands = ['/etc/rc.d/pf stop', '/etc/rc.d/pf start']
        for command in commands:
            self.log("Executing: `%s`" % command)
            subprocess.Popen(shlex.split(str(command))).wait()

    def setup_pf_conf(self, pf_conf):
        rules = self.vm.firewall
        if not rules:
            self.log("No firewall to write.")
            return False
        self.log("Writing firewall rules at `%s`." % pf_conf)
        with open(pf_conf, 'w') as f:
            f.write(rules)
            f.flush()

    def setup_rc(self, rc_conf, pf_conf):
        #TODO Move this to a configuration value. Not high priority.
        rc_items = {
            'pf_enable'      : 'YES',
            'pf_rules'       : pf_conf,
            'pflog_enable'   : 'YES',
            'gateway_enable' : 'YES'
        }
        rc_present = []
        rc = self._get_rc_content()

        for line in rc:
            for k in rc_items:
                if line.startswith(k):
                    rc_present.append(k)
                    break

        missing = set(rc_items.keys()) - set(rc_present)

        tpl = 'Adding to rc: `%s="%s"`'
        [self.log(tpl % (k, rc_items[k])) for k in missing]

        template = '%s="%s"\n'
        with open(rc_conf, 'a') as f:
            [f.write(template % (k,rc_items[k])) for k in missing]
            f.flush()

class InterfacesSetupTask(SetupTask, RcReader):
    '''Configures network interfaces for the jails.'''

    def run(self):

        (netaddrs, missing) = self._get_missing_netaddrs()
        self._add_missing_netaddrs(missing)
        self._add_missing_rc(netaddrs)
        return True

    def _add_missing_rc(self, netaddrs):
        rc_addresses = []
        rc = self._get_rc_content()
        alias_count = self._calculate_alias_count(rc_addresses, rc)

        with open('/etc/rc.conf', 'a') as f:
            for netaddr in netaddrs:
                if self._add_rc_ip(rc_addresses, f, alias_count, netaddr):
                    alias_count += 1

    def _add_missing_netaddrs(self, netaddrs):
        for netaddr in netaddrs:
            self.log("Registering new ip address `%s`" % netaddr['ip'])
            self._add_addr(netaddr['ip'], netaddr['netmask'])

    def _get_missing_netaddrs(self):
        interfaces = NetInterfaces.getInterfaces()
        missing = []
        netaddrs = []

        for jail in self.vm.jails:
            netaddr = {'ip': jail.ip, 'netmask': jail.netmask}
            netaddrs.append(netaddr)
            if not interfaces.has_key(jail.ip):
                missing.append(netaddr)
        return (netaddrs, missing)

    def _calculate_alias_count(self, addresses, rc):
        alias_count = 0

        for line in rc:
            if line.startswith('ifconfig_%s_alias' % self.vm.interface):
                alias_count += 1
                addresses.append(line)

        return alias_count

    def _add_addr(self, ip, netmask):
        cmd = "ifconfig %s alias %s netmask %s"
        command = cmd % (self.vm.interface, ip, netmask)
        self.log('executing: `%s`' % command)
        subprocess.Popen(shlex.split(str(command))).wait()

    def _add_rc_ip(self, rc_addresses, file, alias_count, netaddr):

        for item in rc_addresses:
            if item.find(netaddr['ip']) > 0:
                self.log("rc already knows about ip `%s`" % netaddr['ip'])
                return False
        self.log("Registering new rc value for ip `%s`" % netaddr['ip'])
        template = 'ifconfig_%s_alias%s="inet %s netmask %s"'
        line = "%s\n" % template
        values = (
            self.vm.interface, alias_count, netaddr['ip'], netaddr['netmask']
        )

        file.write(line % values)
        file.flush()
        return True

class HypervisorSetupTask(SetupTask, RcReader):
    '''
    Setups a few hypervisor settings such as Shared Memory/IPC
    '''
    def run(self):
        self._add_rc_settings()
        self._add_sysctl_settings()
        self._set_hostname()
        return True

    def _set_hostname(self):

        self.log("Replacing hostname in /etc/rc.conf")
        (fh, abspath) = tempfile.mkstemp()

        tmp = open(abspath, 'w')
        with open('/etc/rc.conf', 'r') as f:
            for line in f:
                if not line.startswith('hostname'):
                    tmp.write(line)
                    continue
                tmp.write('hostname="%s"\n' % self.vm.name)
        tmp.close()
        os.close(fh)
        os.remove('/etc/rc.conf')
        shutil.move(abspath, '/etc/rc.conf')

        cmd = str('hostname %s' % self.vm.name)
        self.log('Executing: `%s`' % cmd)
        subprocess.Popen(shlex.split(cmd)).wait()


    def _add_sysctl_settings(self):
        sysvipc = cherrypy.config.get('hypervisor.jail_sysvipc_allow')
        ipc_setting = 'security.jail.sysvipc_allowed'

        self.log("Configuring sysctl")
        with open('/etc/sysctl.conf', 'r') as f:
            sysctl = f.readlines()

        if sysvipc:

            cmd = str("sysctl %s=1" % ipc_setting)
            self.log('Executing: `%s`' % cmd)
            subprocess.Popen(shlex.split(cmd)).wait()

            if self._has_line(sysctl, ipc_setting):
                self.log('SysV IPC already configured in sysctl.conf')
                return

            template = '%s=%s\n'
            data = template % (ipc_setting, 1)
            self.log('Adding to sysctl.conf: `%s`' % data)
            with open('/etc/sysctl.conf', 'a') as f:
                f.write(data)

    def _add_rc_settings(self):
        items = [
            'jail_sysvipc_allow',
            'syslogd_flags'
        ]
        rc = self._get_rc_content()

        # settings will contain items to be added to rc
        settings = {}
        for i in items:
            value = cherrypy.config.get('hypervisor.%s' % i)
            if not value:
                continue

            if self._has_line(rc, i):
                continue

            self.log('Adding to rc: `%s="%s"`' % (i, value))
            settings[i] = value

        # settings now contains items to be added
        template = '%s="%s"\n'
        with open('/etc/rc.conf', 'a') as f:
            [f.write(template % (k, settings[k])) for k in settings]
            f.flush()

class EZJailSetupTask(SetupTask):
    '''
    Setups ezjail in the virtual machine
    '''
    def run(self):

        base_dir = cherrypy.config.get('setup_plugin.jail_dir')
        dst_dir = '%s/flavours' % base_dir

        if not os.path.isdir(dst_dir):
            try:
                self.log("Creating folder `%s`." % dst_dir)
                os.makedirs(dst_dir)
            except OSError as e:
                self.log('Could not create folder `%s`' % dst_dir)
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
                msg = "File `%s` is not a tarfile."
                self.log(msg % file['tmp_file'])
                return False
            self.log('Extracting `%s`' % file['tmp_file'])
            # Extraction
            try:
                with tarfile.open(file['tmp_file'], mode='r:*') as t:
                    '''Will raise KeyError if file does not exists.'''
                    if not t.getmember(file['type']).isdir():
                        msg ="Tar member `%s` is not a folder."
                        raise tarfile.ExtractError(msg % file['type'])
                    t.extractall("%s/" % dst_dir)
            except (IOError, KeyError, tarfile.ExtractError) as e:
                msg = "File `%s` could not be extracted. Reason: %s"
                self.log(msg % (file['tmp_file'], e))

            # Remove the temporary tarball
            try:
                os.unlink(file['tmp_file'])
            except OSerror as e:
                msg = "Error while removing file `%s`: %s"
                self.log(msg % (file['tmp_file'], e))
        return True

    def _retrieveFlavours(self):
        '''Retrieve the tarball for each flavours'''

        tmpfiles = []

        jail_dir = cherrypy.config.get('setup_plugin.jail_dir')

        for jail in self.vm.jails:
            (handle, tmpname) = tempfile.mkstemp(dir=jail_dir)

            self.log("Fetching flavour `%s` at `%s`" % (jail.name, jail.url))
            try:
                (filename, headers) = urllib.urlretrieve(jail.url, tmpname)
            except (urllib.ContentTooShortError, IOError) as e:
                msg = "Error while retrieving jail `%s`: %s"
                self.log(msg % (jail.name, e))
                return False

            tmpfiles.append({'type': jail.jail_type, 'tmp_file': filename})
            self.log("Jail `%s` downloaded at `%s`" % (jail.name, filename))
        return tmpfiles

class JailConfigTask(SetupTask):
    '''
    Handles jails configuration
    '''

    def run(self):

        jail_dir = cherrypy.config.get('setup_plugin.jail_dir')
        flavour_dir = "%s/flavours" % jail_dir

        for jail in self.vm.jails:
            self.log("Configuring jail `%s`." % jail.jail_type)

            path = "%s/%s" % (flavour_dir, jail.jail_type)
            authorized_key_file = "%s/installdata/authorized_keys" % path
            resolv_file = "%s/etc/resolv.conf" % path
            yum_file = "%s/installdata/yum_repo" % path

            # Create /installdata and /etc folder.
            for p in ['%s/installdata', '%s/etc']:
                if not os.path.exists(p % path):
                    os.mkdir(p % path)

            # Verify the flavours exists.
            exists = os.path.exists(path)
            is_dir = os.path.isdir(path)
            if not exists or not is_dir:
                msg = "Flavour `%s` directory is missing in `%s."
                self.log(msg % (jail.jail_type, flavour_dir))
                return False

            msg = "Retrieving yum repository for environment `%s`."
            self.log(msg % self.vm.environment)
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
        return True

    def _writeKeys(self, jail, authorized_key_file):
        '''Write authorized keys'''

        try:
            with open(authorized_key_file, 'w') as f:
                for key in self.vm.keys.values():
                    f.write("%s\n" % key['key'])
        except IOError as e:
            msg = "Error while writing authorized keys to jail `%s`: %s"
            self.log(msg % (jail.jail_type, e))
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
            msg = "Error while installing jail `%s`: %s"
            self.log(msg % (jail.jail_type, e))
            return False
        return True

class JailStartupTask(SetupTask):
    '''
    Handles starting each jail.
    '''

    def run(self):

        # Start each jail
        for jail in self.vm.jails:
            self.log("Starting jail `%s`" % jail.jail_type)
            try:
                status = jail.start()
            except OSError as e:
                self.log("Could not start jail `%s`: %s" % (jail.jail_type, e))
                return False
            self.log("Jail status: %s" % status)
            self.log("Jail `%s` started" % jail.jail_type)
            if not jail.status():
                self.log("Jail `%s` is not running!" % jail.jail_type)
                return False

        return True

class SetupWorkerThread(threading.Thread):
    """
    Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition.
    """

    def __init__(self, bus, queue, outqueue, puck):
        super(self.__class__, self).__init__()
        self._stop = threading.Event()
        self.running = threading.Event()
        self.successful = False
        self.completed = False

        self._queue = queue
        self._bus = bus
        self._outqueue = outqueue
        self._puck = puck

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
        task.log('Starting')
        if not task.run():
            raise RuntimeError("%s error while running task `%s`" % loginfo)
        task.log('Completed')
        self._queue.task_done()

    def run(self):
        if self.completed:
            self._bus.log("%s had already been run." % self.__class__.__name__)
            return False

        if self.running.isSet():
            self._bus.log("%s is already running." % self.__class__.__name__)
            return False

        self.running.set()

        self._bus.log("%s started." % self.__class__.__name__)
        try:
            while not self.stopped():
                self._step()
        except RuntimeError as err:
            self._bus.log(str(err))
            self._empty_queue()
            self._puck.getVM().status = 'setup_failed'
            self.succesful = False
            self.completed = True
            return False
        except queue.Empty:
            pass

        self.completed = True
        self.sucessful = True
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
        self.worker = SetupWorkerThread(
                bus=self.bus, queue = self._queue,
                outqueue = self._workerQueue, puck = self._puck
        )
        self.worker.start()

    def _setup_start(self, **kwargs):
        self.bus.log("Received start request.")

        # Start the worker if it is not running.
        if not self.worker:
            self._start_worker()
        if not self.worker.is_alive() and not self.worker.successful:
            self._start_worker()

        # @TODO: Persistence of the list when failure occurs.
        # or a state machine instead of a queue.
        for task in cherrypy.config.get('setup_plugin.tasks'):
            self._queue.put(task)

    def _setup_status(self, **kwargs):
        '''
        Returns the current log queue and if the setup is running or not.
        '''
        if self.worker and self.worker.completed:
            return (self.statuses, False)

        status = self._readQueue(self._workerQueue)
        while status:
            self.statuses.append(status)
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
