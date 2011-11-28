import shutil
import os.path
from subprocess import call, check_output

import models

ISO = "server.iso"

class Launcher(object):
    models = [models.VM]

    def __init__(self, models):
        for cls in models:
            setattr(self, cls.__name__, models[cls])

    def launch(self):
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


        retcode = call([vm, "createvm", 
                            "--name", name, 
                            "--ostype", "FreeBSD",
                            "--register"])
        retcode = call([vm, "modifyvm", name, 
                            "--memory", "1024"])
        retcode = call([vm, "modifyvm", name, 
                            "--nic1", "nat"])
        retcode = call([vm, "createhd", 
                            "--filename",  "%s.vdi" % name, 
                            "--size", "8096", 
                            "--variant", "FIXED"])
        retcode = call([vm, "storagectl", name, 
                            "--name", "IDE Controller",
                            "--add", "ide"])
        retcode = call([vm, "modifyvm", name, 
                            "--hda", "%s.vdi" % name])
        retcode = call([vm, "storageattach", name, 
                            "--storagectl", "IDE Controller",
                            "--port", "1",
                            "--device", "0", 
                            "--type", "dvddrive", 
                            "--medium", ISO])
