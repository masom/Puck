#!/bin/sh
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

START=$(pwd)
PACKAGESITE="http://10.0.254.23/pkgsite/current/"

DEST=$(mktemp -d pkg.XXX)

cd $DEST
fetch "$PACKAGESITE/pkg/hypervisor/index"
PKGCOUNT=$(wc -l index)
echo "$PKGCOUNT packages to be installed."
while read file; do
    fetch "$PACKAGESITE/pkg/hypervisor/$file"
done < index
rm index

pkg_add *.tbz

#Now fetch the initalization application
fetch "$PACKAGESITE/init/index"
while read file; do
    fetch "$PACKAGESITE/init/$file"
done < index
rm index

rpm --initdb
########################
#
#    RPM REGISTRATION
#
#    TODO: Find a better way to do this... this requires too much stuff.
#
########################
for d in BUILD BUILDROOT RPMS SOURCES SRPMS SPECS; do
    mkdir -p /root/rpmbuild/$d
done

mkdir /usr/local/share/hcn/
cp spectemplate /usr/local/share/hcn

HOME=/root
PATH=$PATH:/usr/local/bin
export HOME
export PATH
pkg_info | /usr/local/bin/python registerports.py

########################
#
#    RPM INSTALLATION
#
########################
rpm -ivh *.rpm

tar -xzf pixie.tar.gz -C /usr/local/
cp pixie.conf /usr/local/etc/pixie.conf

cd $START
rm -rf $DEST

# Download meta-data from openstack.
fetch http://169.254.169.254/2009-04-04/meta-data/puck_vm_id -o /usr/local/etc/puck_registration

#Overwrites rc.local to launch pixie
( cat <<'EOF'
#!/usr/local/bin/bash
/usr/local/bin/pixie.py -d -c /usr/local/etc/pixie.conf
EOF
) > /etc/rc.local

/usr/local/bin/pixie.py -d -c /usr/local/etc/pixie.conf
