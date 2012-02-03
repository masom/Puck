import environments
import images
import jails
import keys
import users
import virtual_machines
import yum_repositories
import jail_types

Environments = environments.Environments()
Images = images.Images()
Jails = jails.Jails()
JailTypes = jail_types.JailTypes()
Keys = keys.Keys()
Users = users.Users()
VirtualMachines = virtual_machines.VirtualMachines()
YumRepositories = yum_repositories.YumRepositories()

def load():
    collections = [
        Environments, Images,Jails,JailTypes,Keys,Users,
        VirtualMachines,YumRepositories
    ]
    [c.load() for c in collections]

