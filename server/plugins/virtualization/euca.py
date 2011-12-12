from launcher import Launcher
from euca2ools.commands.euca import RunInstances, RebootInstances, DescribeInstances, TerminateInstances
class Euca(Launcher):
    models = [models.VM]
    supported_api = ['create', 'delete', 'status', 'restart']

    def __init__(self, models):                
        for cls in models:
            setattr(self, cls.__name__, models[cls])

    def _eucatool_init(self, cmd):
        '''Initialize the euca command.'''

        '''TODO: Get this from db.'''
        settings = {
            'ec2_user_access_key': 'derp',
            'ec2_user_secret_key': 'derp',
            'url': 'http://cloud.hcn',
            'region': 'freebsd'
        }

        cmd.handle_defaults()

        cmd.ec2_user_access_key = settings['ec2_user_access_key']
        cmd.ec2_user_secret_key = settings['ec2_user_secret_key']
        cmd.url = settings['url']
        cmd.region = settings['region']
        cmd.is_euca = False

        '''
        "id", "image_id", "public_dns_name", "private_dns_name",
        "state", "key_name", "ami_launch_index", "product_codes",
        "instance_type", "launch_time", "placement", "kernel",
        "ramdisk"
        '''
    def _euca_connect(self,cmd, type = 'ec2'):
        '''Raise euca2ools.exceptions.EucaError'''
        return cmd.make_connection('ec2')

    def _euca_make_request(self, cmd, connection, request_name, **params):
        '''
        Raise AttributeError
        Raise Exception
        '''

        try:
            if cmd.filters:
                params['filters'] = cmd.filters
            method = getattr(connection, request_name)
        except AttributeError:
            return False

        return method(**params)

    def create(self, image_id, instance_type):
        cmd = euca2ools.commands.euca.runinstances.RunInstances()
        self._eucatool_init(cmd)
        cmd.instance_type = instance_type
        cmd.image_id = image_id

        conn = self._euca_connect(cmd)

        options = dict(
            image_id=cmd.image_id,
            min_count=min_count,
            max_count=max_count,
            key_name=cmd.keyname,
            security_groups=cmd.group_name,
            user_data=cmd.user_data,
            addressing_type=cmd.addressing,
            instance_type=cmd.instance_type,
            placement=cmd.zone,
            kernel_id=cmd.kernel,
            ramdisk_id=cmd.ramdisk,
            block_device_map=cmd.block_device_mapping,
            monitoring_enabled=cmd.monitor,
            subnet_id=cmd.subnet
        )

        reservation = self._euca_make_request(cmd, conn, 'run_instances', **options)
        return reservation.id

    def status(self, id):
        cmd = euca2ools.commands.euca.describeinstances.DescribeInstances()
        self._eucatool_init(cmd)

        conn = self._euca_connect(cmd)

        options = dict(instance_ids=[id])
        reservations = self._euca_make_request(cmd, conn, 'get_all_instances', **options)

        instances = [] 
        for reservation in reservations:
            if len(reservation.instances) == 0:
                continue
            instances.extend(reservation.instances)
        return instances

    def delete(self, id):
        cmd = euca2ools.commands.euca.rebootinstances.TerminateInstances()
        self._eucatool_init(cmd)
        cmd.instance_id = id

        conn = self._euca_connect(cmd)

        options = dict(instance_ids=[id])
        instances = self._euca_make_request(cmd, conn, 'terminate_instances', **options)
        return instances

    def restart(self, id):
        cmd = euca2ools.commands.euca.rebootinstances.RebootInstances()
        self._eucatool_init(cmd)
        cmd.instance_id = id

        conn = self._euca_connect(cmd)

        options = dict(instance_ids=[id])
        status = self._euca_make_request(cmd, conn, 'reboot_instances', **options)

        if status:
            return self.instance_id
        else:
            return False
        