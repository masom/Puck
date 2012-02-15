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

- A machine to run puck
- A FreeBSD virtual machine image

# Notes on using FreeBSD images
## Virtio
There is a FreeBSD patch to be applied on images for VirtIO to work. Otherwise, nova-compute libvirt configuration must be updated to use normal hard drives (hd) instead of virtio.
## Uploading Images

If an image is uploaded with euca2ools, the glance entry must be updated to reflect the following:

    container_type: bare
    image_type: qcow2

# Installation
Configure `setup/setup.sh` to match your environment (mostly just change the url of the package site).

The boostrap file should be included in the virtual machine base image and be run during the first boot.

The RPM packages required for Pixie to run are CherryPy and Mako. These should be present in the second package site (named `init`).

More to come.

## How to create a package site
A package site is essentially just a repository of freebsd pkg tarballs. Here's an example one:

    autoconf-2.68.tbz			help2man-1.40.4.tbz			perl-5.12.4_3.tbz			screen-4.0.3_13.tbz
    autoconf-wrapper-20101119.tbz		index					pkg-config-0.25_1.tbz			sqlite3-3.7.9.tbz
    autossh-1.4b.tbz			libassuan-2.0.2.tbz			popt-1.16.tbz				ssmtp-2.64.tbz
    bash-4.1.11.tbz				libgcrypt-1.5.0.tbz			postgresql-client-8.4.9.tbz		sudo-1.8.3_1.tbz
    bison-2.4.3,1.tbz			libgpg-error-1.10.tbz			pth-2.0.7.tbz				swig-1.3.40.tbz
    ca_root_nss-3.12.11_1.tbz		libiconv-1.13.1_1.tbz			py27-PyGreSQL-4.0,1.tbz			tcl-8.4.19_3,1.tbz
    cowsay-3.03_1.tbz			libksba-1.2.0.tbz			py27-iniparse-0.4.tbz			tcl-8.5.11.tbz
    curl-7.21.3_2.tbz			libtool-2.4_1.tbz			py27-pyme-0.8.1_4.tbz			tcl-modules-8.5.11.tbz
    db46-4.6.21.4.tbz			libxml2-2.7.8_1.tbz			py27-sqlite3-2.7.2_1.tbz		unzip-6.0_1.tbz
    expect-5.43.0_3.tbz			lua-5.1.4_6.tbz				py27-urlgrabber-3.9.1.tbz		vim-7.3.121.tbz
    gettext-0.18.1.1.tbz			m4-1.4.16,1.tbz				py27-yaml-3.10.tbz			wget-1.13.4_1.tbz
    gmake-3.82.tbz				nano-2.2.6.tbz				py27-yum-metadata-parser-1.1.4.tbz	zip-3.0.tbz
    gnupg-2.0.18_1.tbz			nspr-4.8.9.tbz				python27-2.7.2_3.tbz
    gpgme-1.3.1.tbz				nss-3.12.11.tbz				rpm-4.9.1.2_1.tbz
    gsed-4.2.1_2.tbz			p5-Locale-gettext-1.05_3.tbz		rsync-3.0.9.tbz

The index file is used by the bootstrap script to download the appropriate packages.

## The package index

`rm index; for file in *; do echo $file >> index; done;`

## How to create a jail flavor
Copy the template located at `/flavour`. The new folder should be named exactly the same as the flavor.

Add all the required FreeBSD packages in `[flavor name]/pkg/All`.
Add your RPM packages in `[flavor name]/pkg/rpm`.

Edit `[flavor name]/ezjail.flavour` as required (Add users, custom config, etc.). Most of the changes should probably be in a RPM or FreeBSD package.

Tar up the folder: `tar -cf [flavor name].tar [flavor name]`

The tar structure should be like this:
    [flavor name]/
        ezjail.flavour
        pkg/
            All/
                ...
            rpm/
                ...
            registerports.py
            spectemplate

# License
LGPL v3

# See
- http://freebsd.org
- http://erdgeist.org/arts/software/ezjail/
- http://www.freshports.org/archivers/rpm4/Makefile
- http://openstack.org/
- http://en.wikipedia.org/wiki/Puck_(mythology)

