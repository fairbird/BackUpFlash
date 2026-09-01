#!/bin/bash
##setup command=wget https://raw.githubusercontent.com/fairbird/BackUpFlash/main/installer.sh -O - | /bin/sh

version=12.8
description=What is NEW :\n- Do not delete the mounted folder if the mount is not removed.
- Secure file deletion process.
- Do not back up or convert images if the stored space is less than 400 MB.
echo ""
if [ ! -d "/usr/lib64" ]; then
	LIBPATH="/usr/lib"
else
	LIBPATH="/usr/lib64"
fi
#########################
if [ `uname -r | grep dm7080 | wc -l` -gt 0 ]; then
	DEVICE="MIPS"
        echo "[Your device is MIPS - DM7080]"
        echo ""
elif [ `uname -r | grep dm820 | wc -l` -gt 0 ]; then
	DEVICE="MIPS"
        echo "[Your device is MIPS - DM820]"
        echo ""
elif [ `uname -r | grep dm520 | wc -l` -gt 0 ]; then
	DEVICE="MIPS"
        echo "[Your device is MIPS - DM520/525]"
        echo ""
elif [ `uname -r | grep dm525 | wc -l` -gt 0 ]; then
	DEVICE="MIPS"
        echo "[Your device is MIPS - DM525]"
        echo ""
elif [ `uname -r | grep dm900 | wc -l` -gt 0 ]; then
	DEVICE="armv7l"
        echo "[Your device is armv7l - DM900]"
        echo ""
elif [ `uname -r | grep dm920 | wc -l` -gt 0 ]; then
	DEVICE="armv7l"
        echo "[Your device is armv7l - DM920]"
        echo ""
elif [ `uname -r | grep 4.9 | wc -l` -gt 0 ]; then
	DEVICE="armv64"
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

# check depends packges
if [ -f /var/lib/dpkg/status ]; then
   STATUS=/var/lib/dpkg/status
   OSTYPE=DreamOs
else
   STATUS=/var/lib/opkg/status
   OSTYPE=Opensource
fi

if [ -f /usr/bin/python3 ] ; then
	echo "You have Python3 image"
	PYTHON=PY3
	CRYPT="python3-crypt"
	REQUESTS="python3-requests"
else
	echo "You have Python2 image"
	PYTHON=PY2
	CRYPT="python-crypt"
	REQUESTS="python-requests"
fi

wget="wget"
pigz="pigz"
xz="xz"
zip="7zip"
p7zip="p7zip"
flashscripts="flash-scripts"

# install depend packges if need it
if grep -qs "Package: $CRYPT" "$STATUS" && \
	grep -qs "Package: $REQUESTS" "$STATUS" && \
	grep -qs "Package: $wget" "$STATUS" && \
	grep -qs "Package: $xz" "$STATUS" && \
	grep -qs "Package: $pigz" "$STATUS" && \
	grep -qs "Package: $flashscripts" "$STATUS" && \
	( grep -qs "Package: $zip" "$STATUS" || grep -qs "Package: $p7zip" "$STATUS" ); then
	echo ""
	echo "All depend packages Installed"
else
	opkg update >/dev/null 2>&1
	if grep -qs "Package: $CRYPT" cat "$STATUS" ; then
		echo ""
	else
		echo "Need to install $CRYPT"
		opkg install $CRYPT >/dev/null 2>&1
	fi
	if grep -qs "Package: $REQUESTS" cat "$STATUS" ; then
		echo ""
	else
		echo "Need to install $REQUESTS"
		opkg install $REQUESTS >/dev/null 2>&1
	fi
	if grep -qs "Package: $wget" cat "$STATUS" ; then
		echo ""
	else
		echo "Need to install $wget"
		opkg install $wget >/dev/null 2>&1
	fi
	if grep -qs "Package: $pigz" cat "$STATUS" ; then
		echo ""
	else
		echo "Need to install $pigz"
		opkg install $pigz >/dev/null 2>&1
	fi
	if grep -qs "Package: $p7zip" cat "$STATUS" ; then
		echo ""
	else
		echo "Need to install $p7zip"
		opkg install $p7zip >/dev/null 2>&1
	fi
 	if grep -qs "Package: $zip" cat "$STATUS" ; then
		echo ""
	else
		echo "Need to install $zip"
		opkg install $zip >/dev/null 2>&1
	fi
	if grep -qs "Package: $xz" ""$STATUS"" ; then
		echo ""
	else
		echo "Need to install $xz"
		opkg install $xz >/dev/null 2>&1
	fi
	if grep -qs "Package: $flashscripts" cat "$STATUS" ; then
		echo ""
	else
		echo "Need to install $flashscripts"
		opkg install $flashscripts >/dev/null 2>&1
	fi
fi
# Try to download locale packages and install those missing on feed of DreamOS images
if [ "$OSTYPE" == "DreamOs" ]; then
	cd /tmp
	if [ "$DEVICE" == "MIPS" ]; then
		if ! grep -q "pigz" "$STATUS" ; then
			wget https://github.com/fairbird/BackUpFlash/raw/refs/heads/main/Packages/MIPS/pigz_2.3.3-r0.4_mipsel.deb
			dpkg -i --force-overwrite /tmp/pigz_2.3.3-r0.4_mipsel.deb
		fi
		if ! grep -q "xz" "$STATUS" ; then
			wget https://github.com/fairbird/BackUpFlash/raw/refs/heads/main/Packages/MIPS/xz_5.2.2-r0.4_mipsel.deb
			dpkg -i --force-overwrite /tmp/xz_5.2.2-r0.4_mipsel.deb
		fi
		if ! grep -q "p7zip" "$STATUS" ; then
			wget https://github.com/fairbird/BackUpFlash/raw/refs/heads/main/Packages/MIPS/p7zip_9.20.1-r0.1_mipsel.deb
			dpkg -i --force-overwrite /tmp/p7zip_9.20.1-r0.1_mipsel.deb
		fi
		if ! grep -q "flash-scripts" "$STATUS" ; then
			wget https://github.com/fairbird/BackUpFlash/raw/refs/heads/main/Packages/MIPS/flash-scripts_1.1+git12+530b1eb807-r0.0_mipsel.deb
			dpkg -i --force-overwrite /tmp/flash-scripts_1.1+git12+530b1eb807-r0.0_mipsel.deb
		fi
	elif [ "$DEVICE" == "armv7l" ]; then
		if ! grep -q "pigz" "$STATUS" ; then
			cd /tmp
			wget https://github.com/fairbird/BackUpFlash/raw/refs/heads/main/Packages/ARM/pigz_2.3.3-r0.4_armhf.deb
			dpkg -i --force-overwrite /tmp/pigz_2.3.3-r0.4_armhf.deb
		fi
		if ! grep -q "xz" "$STATUS" ; then
			cd /tmp
			wget https://github.com/fairbird/BackUpFlash/raw/refs/heads/main/Packages/ARM/xz_5.2.2-r0.4_armhf.deb
			dpkg -i --force-overwrite /tmp/xz_5.2.2-r0.4_armhf.deb
		fi
		if ! grep -q "p7zip" "$STATUS" ; then
			cd /tmp
			wget https://github.com/fairbird/BackUpFlash/raw/refs/heads/main/Packages/ARM/p7zip_9.20.1-r0.1_armhf.deb
			dpkg -i --force-overwrite /tmp/p7zip_9.20.1-r0.1_armhf.deb
		fi
		if ! grep -q "flash-scripts" "$STATUS" ; then
			cd /tmp
			wget https://github.com/fairbird/BackUpFlash/raw/refs/heads/main/Packages/ARM/flash-scripts_1.1+git9+530b1eb807-r0.0_armhf.deb
			dpkg -i --force-overwrite /tmp/flash-scripts_1.1+git9+530b1eb807-r0.0_armhf.deb
		fi
	elif [ "$DEVICE" == "armv64" ]; then
		if ! grep -q "pigz" "$STATUS" ; then
			wget https://github.com/fairbird/BackUpFlash/raw/refs/heads/main/Packages/AARCH64/pigz_2.3.4-r0.3_arm64.deb
			dpkg -i --force-overwrite /tmp/pigz_2.3.4-r0.3_arm64.deb
		fi
		if ! grep -q "xz" "$STATUS" ; then
			wget https://github.com/fairbird/BackUpFlash/raw/refs/heads/main/Packages/AARCH64/xz_5.2.3-r0.3_arm64.deb
			dpkg -i --force-overwrite /tmp/xz_5.2.3-r0.3_arm64.deb
		fi
		if ! grep -q "p7zip" "$STATUS" ; then
			wget https://github.com/fairbird/BackUpFlash/raw/refs/heads/main/Packages/AARCH64/p7zip_16.02-r0.1_arm64.deb
			dpkg -i --force-overwrite /tmp/p7zip_16.02-r0.1_arm64.deb
		fi
		if ! grep -q "flash-scripts" "$STATUS" ; then
			wget https://github.com/fairbird/BackUpFlash/raw/refs/heads/main/Packages/AARCH64/flash-scripts_1.1+git4+81ff8d40bb-r0.0_arm64.deb
			dpkg -i --force-overwrite /tmp/flash-scripts_1.1+git4+81ff8d40bb-r0.0_arm64.deb
		fi
	fi
	apt-get install -f -y
	cd ..
fi
# Make more check depend packges
if grep -q "wget" "$STATUS" ; then
     echo ""
else
     echo "Missing (wget) package"
exit 1
fi
if grep -q "pigz" "$STATUS" ; then
     echo ""
else
     echo "Missing (pigz) package"
exit 1
fi
if grep -q "7zip" "$STATUS" || grep -q "p7zip" "$STATUS" ; then
     echo ""
else
     echo "Missing (7zip) or (p7zip) package"
exit 1
fi
if grep -q "flash-scripts" "$STATUS" ; then
     echo ""
else
     echo "Missing (flash-scripts) package"
exit 1
fi
if grep -q $CRYPT "$STATUS" ; then
     echo ""
else
     echo "Missing ($CRYPT) package"
exit 1
fi
if grep -q "xz" "$STATUS" ; then
     echo ""
else
     echo "Missing (xz) package"
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
#
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
