import environments
import images
import jails
import keys
import users
import virtual_machines
import yum_repositories
import jail_types
import instance_types
import firewalls

Environments = environments.Environments()
Firewalls = firewalls.Firewalls()
Images = images.Images()
InstanceTypes = instance_types.InstanceTypes()
Jails = jails.Jails()
JailTypes = jail_types.JailTypes()
Keys = keys.Keys()
Users = users.Users()
VirtualMachines = virtual_machines.VirtualMachines()
YumRepositories = yum_repositories.YumRepositories()

Credential=None

def load():
    collections = [
        Environments, Images,Jails,JailTypes,Keys,Users,
        VirtualMachines,YumRepositories,InstanceTypes, Firewalls
    ]
    [c.load() for c in collections]

