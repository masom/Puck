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

/usr/local/bin/rpm --initdb
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

mkdir -p /usr/local/etc/rpm
cp macros.fbsd /usr/local/etc/rpm/

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
/usr/local/bin/rpm -ivh *.rpm

cd $START
rm -rf $DEST

#Overwrites rc.local to launch pixie
echo "#!/usr/local/bin/bash" > /etc/rc.local
echo "fetch -o /usr/local/etc/puck_registration http://169.254.169.254/latest/user-data" >> /etc/rc.local
echo "fetch -o /tmp/pixie.rpm $PACKAGESITE/init/pixie.rpm" >> /etc/rc.local
echo "/usr/local/bin/rpm -ivh /tmp/pixie.rpm" >> /etc/rc.local
echo "rm /tmp/pixie.rpm" >> /etc/rc.local
echo "fetch -o /usr/local/etc/pixie.conf $PACKAGESITE/init/pixie.conf" >> /etc/rc.local
echo "/usr/local/bin/pixie-client.py -d -c /usr/local/etc/pixie.conf" >> /etc/rc.local
/etc/rc.local &
