from models import *

def seed_jail_types():
    jail_type_seeds = [
        dict(id='content', ip='10.0.0.10', netmask='255.255.255.0'),
        dict(id='database', ip='10.0.0.11', netmask='255.255.255.0'),
        dict(id='support', ip='10.0.0.12', netmask='255.255.255.0'),
    ]
    for seed in jail_type_seeds:
        JailTypes.add(JailTypes.new(**seed))

def seed_environments():
        items = [
            Environments.new(code='dev',name='Development'),
            Environments.new(code='testing', name='Testing'),
            Environments.new(code='qa', name='Quality Assurance'),
            Environments.new(code='staging', name='Staging'),
            Environments.new(code='prod', name='Production')
        ]
        for item in items:
            Environments.add(item)

def seed_database():
    seed_jail_types()
    seed_environments()
