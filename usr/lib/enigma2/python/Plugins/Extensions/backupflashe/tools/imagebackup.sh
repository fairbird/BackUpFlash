#!/bin/sh

if [ -f /tmp/root/usr/lib/enigma.info ]; then
	Distro=`/bin/grep "^distro=" /tmp/root/usr/lib/enigma.info | /bin/sed -En "s/^\w+=(['\"]?)(.*?)\1$/\2/p"`
	DisplayDistro=`/bin/grep "^displaydistro=" /tmp/root/usr/lib/enigma.info | /bin/sed -En "s/^\w+=(['\"]?)(.*?)\1$/\2/p"`
	ImageVersion=`/bin/grep "^imageversion=" /tmp/root/usr/lib/enigma.info | /bin/sed -En "s/^\w+=(['\"]?)(.*?)\1$/\2/p"`
elif [ -f /tmp/root/etc/image-version ]; then
	Distro=`/bin/grep "^distro=" /tmp/root/etc/image-version | /usr/bin/cut -d"=" -f2`
	if [ "$Distro" == "" ]; then
		DisplayDistro=`/bin/grep "^creator=" /tmp/root/etc/image-version | /usr/bin/cut -d"=" -f2`
		Distro=`/bin/echo "$DisplayDistro" | /usr/bin/cut -d" " -f1`
		Version=`/bin/grep "^version=" /tmp/root/etc/image-version | /usr/bin/cut -d"=" -f2`
		ImageVersion=`/bin/echo "${Version:0:3}" | /bin/sed -En "s/^0*(\d*)/\1/p"`.${Version:3:1}.${Version:4:2}
	else
		DisplayDistro=`/bin/grep "^creator=" /tmp/root/etc/image-version | /usr/bin/cut -d"=" -f2`
		ImageVersion=`/bin/grep "^imageversion=" /tmp/root/etc/image-version | /usr/bin/cut -d"=" -f2`
	fi
elif [ -f /tmp/root/etc/issue ]; then
	Data=`/bin/sed -n 2p /tmp/root/etc/issue`
	Distro=`/bin/echo $Data | /usr/bin/cut -d" " -f1`
	DisplayDistro=`/bin/sed -n 1p /tmp/root/etc/issue | /usr/bin/cut -d" " -f3`
	ImageVersion=`/bin/echo $Data | /usr/bin/cut -d" " -f2`
else
	Distro=Unknown
	DisplayDistro=Unknown
	ImageVersion=Unknown
fi
#/bin/echo "Image version $DisplayDistro $ImageVersion."
/bin/echo "[Image Version]" > /tmp/imageversion
/bin/echo "distro=$Distro" >> /tmp/imageversion
/bin/echo "displaydistro=$DisplayDistro" >> /tmp/imageversion
/bin/echo "imageversion=$ImageVersion." >> /tmp/imageversion
/bin/echo >> /tmp/imageversion
/bin/echo "[Enigma2 Settings]" >> /tmp/imageversion
/bin/cat /etc/enigma2/settings >> /tmp/imageversion
