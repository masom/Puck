#!/usr/bin/python

from distutils.core import setup

setup (
    name = 'pixie',
    description = "Virtualization configuration client",
    author = "Martin Samson",
    author_email = "msamson@hcn-inc.com",
    version = '1.0',
    packages = ['pixie'],
    data_files = [
        ('/etc', ['pixie.conf'])
    ],
    scripts = ['pixie.py']
)
