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
import shutil
import os.path
from subprocess import call, check_output

import models

ISO = "FreeBSD.iso"

class Launcher(object):
    models = [models.VM]

    def __init__(self, models):
        for cls in models:
            setattr(self, cls.__name__, models[cls])

    def launch(self, with_base=True):
        name = self.VM._newId()
        while os.path.exists("%s.vdi" % name):
            name = self.VM._newId()

        vm = "VBoxManage"

        out = check_output([vm, "list", "vms"])
        if any(line.startswith('"%s"' % name)
                    for line in out.splitlines()):
            retcode = call([vm, "unregistervm", name])
            retcode = call([vm, "closemedium", "disk",
                                "%s.vdi" % name, "--delete"])

        path = os.path.join("~", "VirtualBox VMs", name)
        tree = os.path.expanduser(path)
        if os.path.exists(tree):
            shutil.rmtree(tree)

        hda = "%s.vdi" % name

        retcode = call([vm, "createvm",
                            "--name", name,
                            "--ostype", "FreeBSD",
                            "--register"])
        retcode = call([vm, "modifyvm", name,
                            "--memory", "1024"])
        retcode = call([vm, "modifyvm", name,
                            "--nic1", "bridged",
                            "--bridgeadapter1", "eth0"])
        if with_base:
            retcode = call([vm, "clonehd",
                                '/usr/local/share/puck/base.vdi',
                                hda])
        else:
            retcode = call([vm, "createhd", 
                                "--filename",  hda,
                                "--size", "8096", 
                                "--variant", "FIXED"])
        retcode = call([vm, "storagectl", name, 
                            "--name", "IDE Controller",
                            "--add", "ide"])
        retcode = call([vm, "modifyvm", name, 
                            "--hda", hda])
        if not with_base:
            retcode = call([vm, "storageattach", name,
                                "--storagectl", "IDE Controller",
                                "--port", "1",
                                "--device", "0",
                                "--type", "dvddrive",
                            "--medium", ISO])
