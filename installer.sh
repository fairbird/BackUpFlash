#!/bin/bash
##setup command=wget https://raw.githubusercontent.com/fairbird/BackUpFlash/main/installer.sh -O - | /bin/sh

version=10.1
description=What is NEW :\n- Add url download for OpenPLI-Japhar Team-\n\n**************************\n: ما هو الجديد\n- OpenPLI-Japhar-Team إضافة رابط تحميل لصور فريق

echo ""
if [ ! -d '/usr/lib64' ]; then
	LIBPATH='/usr/lib'
else
	LIBPATH='/usr/lib64'
fi
# Find name of device
DreamOS=/var/lib/dpkg/status

if [ `uname -r | grep dm7080 | wc -l` -gt 0 ]; then
        echo "[Your device is MIPS - DM7080]"
        echo ""
elif [ `uname -r | grep dm820 | wc -l` -gt 0 ]; then
        echo "[Your device is MIPS - DM820]"
        echo ""
elif [ `uname -r | grep dm520 | wc -l` -gt 0 ]; then
        echo "[Your device is MIPS - DM520/525]"
        echo ""
elif [ `uname -r | grep dm525 | wc -l` -gt 0 ]; then
        echo "[Your device is MIPS - DM525]"
        echo ""
elif [ `uname -r | grep dm900 | wc -l` -gt 0 ]; then
        echo "[Your device is armv7l - DM900]"
        echo ""
elif [ `uname -r | grep dm920 | wc -l` -gt 0 ]; then
        echo "[Your device is armv7l - DM920]"
        echo ""
elif [ `uname -r | grep 4.9 | wc -l` -gt 0 ]; then
        if [ -e /dev/ci0 ]; then
        	echo "[Your device is armv64 - dreamtwo]"
        else
        	echo "[Your device is armv64 - dreamone]"
        fi
        echo ""
else
echo "##############################################"
echo "#     Sorry plugin not support your STB      #"
echo "##############################################"
exit 1
echo ""
fi
if [ -f /usr/bin/python3 ] ; then
	echo "You have Python3 image"
	PYTHON=PY3
	CRYPT=python3-crypt
	REQUESTS=python3-requests
else
	echo "You have Python2 image"
	PYTHON=PY2
	CRYPT=python-crypt
	REQUESTS=python-requests
fi
if [ -f $DreamOS ]; then
   STATUS=$DreamOS
else
   STATUS=/var/lib/opkg/status
fi
# check depends packges if installed
if grep -q wget $STATUS ; then
	wget="True"
else
	wget="False"
fi
if grep -q pigz $STATUS ; then
	pigz="True"
else
	pigz="False"
fi
if which xz > /dev/null ; then
	xz="True"
else
	xz="False"
fi
if grep -q flash-scripts $STATUS ; then
	flashscripts="True"
else
	flashscripts="False"
fi
if grep -q $CRYPT $STATUS ; then
	PYCRYPT="True"
else
	PYCRYPT="False"
fi
if grep -q $REQUESTS $STATUS ; then
	PYREQUESTS="True"
else
	PYREQUESTS="False"
fi
# install depend packges if need it
if [ $wget = 'True' -a $pigz = 'True' -a $xz = 'True' -a $flashscripts = 'True' -a $PYCRYPT = 'True' ]; then
	echo "All depend packages Installed"
else
	if [ -f $DreamOS ]; then
		dpkg --configure -a;
		apt-get update;
		apt-get install wget pigz xz flash-scripts python-requests python-crypt python-requests -y;
		apt-get install -f -y;
	elif [ $PYTHON = "PY3" ]; then
		opkg update
		opkg install wget pigz xz flash-scripts python3-requests python3-crypt python3-requests;
	elif [ $PYTHON = "PY2" ]; then
		opkg update;
		opkg install wget pigz xz flash-scripts python-requests python-crypt python-requests;
	fi
fi
# Make more check depend packges
if grep -q wget $STATUS ; then
     echo ""
else
     echo "Missing (wget) package"
exit 1
fi
if grep -q pigz $STATUS ; then
     echo ""
else
     echo "Missing (pigz) package"
exit 1
fi
if grep -q xz $STATUS ; then
     echo ""
else
     echo "Missing (xz) package"
exit 1
fi
if grep -q flash-scripts $STATUS ; then
     echo ""
else
     echo "Missing (flash-scripts) package"
exit 1
fi
if grep -q $CRYPT $STATUS ; then
     echo ""
else
     echo "Missing ($CRYPT) package"
exit 1
fi

# remove old version
if [ /media/ba/backupflashe ]; then
	rm -rf /media/ba/backupflashe
fi
if [ $LIBPATH/enigma2/python/Plugins/Extensions/backupflashe ]; then
	rm -rf $LIBPATH/enigma2/python/Plugins/Extensions/backupflashe
fi
if [ $LIBPATH/enigma2/python/Plugins/Extensions/backupflashe2 ]; then
	rm -rf $LIBPATH/enigma2/python/Plugins/Extensions/backupflashe2
fi
if [ $LIBPATH/enigma2/python/Plugins/Extensions/dBackup ]; then
	rm -rf $LIBPATH/enigma2/python/Plugins/Extensions/dBackup
fi
# Download and install plugin
cd /tmp 
set -e
rm -rf *BackUpFlash* > /dev/null 2>&1
rm -rf *main* > /dev/null 2>&1
wget https://github.com/fairbird/BackUpFlash/archive/refs/heads/main.tar.gz
tar -xzf main.tar.gz
cp -r BackUpFlash-main/usr /
rm -rf *BackUpFlash* > /dev/null 2>&1
rm -rf *main* > /dev/null 2>&1
## This commands to save plugin from BA protection
if [ -f "/media/ba/ba.sh" -a "$LIBPATH/enigma2/python/Plugins/Extensions/backupflashe" ]; then
mv /usr/lib/enigma2/python/Plugins/Extensions/backupflashe /media/ba
ln -s /media/ba/backupflashe /usr/lib/enigma2/python/Plugins/Extensions
fi
##
set +e
cd ..
sync

### Check if plugin installed correctly
if [ ! -d $LIBPATH/enigma2/python/Plugins/Extensions/backupflashe ]; then
if [ ! -d /media/ba/backupflashe ]; then
	echo "Some thing wrong .. Plugin not installed"
	exit 1
fi
fi

echo "#########################################################"
echo "#          BackupFlash INSTALLED SUCCESSFULLY           #"
echo "#                 Raed  &  mfaraj57                     #"              
echo "#                     support                           #"
echo "#   https://www.tunisia-sat.com/forums/threads/3902669/ #"
echo "#########################################################"
echo "#           Your STB Will RESTARTING Now                #"
echo "#########################################################"
sleep 3
killall enigma2
exit 0
