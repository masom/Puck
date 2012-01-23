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

from plugins.virtualization.launcher import Launcher

ISO = "FreeBSD.iso"

class VirtualBox(Launcher):
    supported_api = ['create', 'delete', 'status', 'stop', 'start', 'restart']

    def create(self, **kwargs):

        name = kwargs['image_id']

        vdi_template = "%s_%s.vdi"
        i = 0
        while os.path.exists(vdi_template % (name, i)):
            i += 1

        vm = "VBoxManage"

        hda = vdi_template % (name, i)

        out = check_output([vm, "list", "vms"])
        if any(line.startswith('"%s"' % name)
                    for line in out.splitlines()):
            retcode = call([vm, "unregistervm", name])
            retcode = call([vm, "closemedium", "disk",
                                hda, "--delete"])

        path = os.path.join("~", "VirtualBox VMs", name)
        tree = os.path.expanduser(path)
        if os.path.exists(tree):
            shutil.rmtree(tree)

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
