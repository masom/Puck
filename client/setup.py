#!/usr/bin/python

from distutils.core import setup

setup (
    name = 'pixie',
    description = "Virtualization configuration client",
    author = "Martin Samson",
    author_email = "msamson@hcn-inc.com",
    version = '0.3',
    package_dir = {'pixie': 'pixie'},
    packages = [
        'pixie', 'pixie.controllers', 'pixie.lib'
    ],
    package_data={
        'pixie': [
            'static/css/*', 'static/img/*', 'html/*.html', 'html/*/*.html'
        ]
    },
    data_files = [
        ('etc', ['pixie.conf'])
    ],
    scripts = ['pixie-client.py']
)
