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
print "$PKGCOUNT packages to be installed."
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
rpm -i *.rpm

cd $START
rm -rf $DEST

#verify sshd is enabled
grep -q sshd_enable /etc/rc.conf
RETCODE=$?
if [ $RETCODE != "0" ]; then
    echo "sshd_enable=\"YES\"" >> /etc/rc.conf
fi

#Start sshd
/etc/rc.d/sshd start

#Overwrite rc.local to launch pixie
#TODO: Proper launch options.
( cat <<'EOF'
#!/usr/local/bin/bash
/usr/local/bin/pixie.py -d -c /usr/local/etc/pixie.conf
EOF
) > /etc/rc.local

/usr/local/bin/pixie.py -d -c /usr/local/etc/pixie.conf