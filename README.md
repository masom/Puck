# Puck & Pixie
Puck is a virtualization configuration server used by Pixie to configure FreeBSD hypervisors and their jails.

The system expects the use of YUM+RPM as the package manager for end-user packages while the OS and jails packages are to be provided by FreeBSD ports.

We have pushed patches to freebsd ports for RPM and have upcoming ones for YUM.

It is not yet ready for use (still integration work to be done between puck and pixie).

# Virtualization Support
Current plans are to support VirtualBox, QEMU and OpenStack (euca2-tools).

By supporting OpenStack, we can probably easily add Eucalyptus and EC2.

# Why RPM and YUM
While the port system is great at creating the perfect server setup, handling package updates for the user software stack is a little bit more complex.
Yum and RPM allows updating the stack more easily and most of all, it has great support for multiple channels (repos).

Port is great, YUM is great. We merged both tools on the same platform to provide a kick-ass user experience.

We plan to open source our base flavour and the tool to sync the installed ports packages with RPM.

# Running Pixie Tests

    cd pixie
    python -m unittest discover

# Requirements
- Python 2.7
- py27-curl
- py27-iniparse
- py27-pyme
- py27-urlgrabber
- py27-yum-metadata-parser
- CherryPy 3.2
- Mako 0.5

# License
LGPL v3

# See
http://www.freshports.org/archivers/rpm4/Makefile
http://en.wikipedia.org/wiki/Puck_(mythology)

