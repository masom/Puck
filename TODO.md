# Authentication & Security
Puck and Pixie have no authentication methods.

- A simple login window.
- Communications between pixie, puck and browser should be done using HTTPS
- Pixie should communicate with Puck to get a list of valid credentials.

# GPG Signature Support for Flavours

Either use python-gpg or do like port with md5+sha1

http://packages.python.org/python-gnupg/#verification

# QEMU Launcher for Puck.

There is a VirtualBox vm launcher, adding one for QEMU would be great.

Current plans are to support euca2-tools (OpenStack, Eucalyptus and possibly EC2).

# ORM
Puck uses a mini homegrown db adapter. Moving to a real ORM would be preferable.
