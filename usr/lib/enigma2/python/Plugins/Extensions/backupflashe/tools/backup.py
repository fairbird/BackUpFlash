#!/usr/bin/python
# -*- coding: utf-8 -*-
# RAED & mfaraj57 (c) 2018
# Code RAED & mfaraj57

from Components.Label import Label
from Components.config import config
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS
from enigma import eTimer
from time import sleep
import os, datetime

from .Console import Console
from .progress import ProgressScreen 
from .bftools import logdata, dellog, copylog, getboxtype

boxtype = getboxtype()

BRANDOS = '/var/lib/dpkg/status' ## DreamOS
BAINIT = '/sbin/bainit'
cancelBackup = "/tmp/.cancelBackup"
LOG = '/tmp/backupflash.scr'


## BackUp Internal Flash
class doBackUpInternal(Screen):

	def __init__(self, session, image_name = None, device_path = None, image_formats = None, image_compression_value = 0):
		Screen.__init__(self, session)
		self.list = []
		self['key_red'] = Label(_('Cancel'))
		self['key_green'] = Label(_('Backup'))
		self['lab1'] = Label('')
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'],
			{
				'red': self.close,
				'green': self.doBackUpjob,
				'back': self.close
			})
		self.image_name = image_name
		self.device_path = device_path
		self.image_formats = image_formats
		self.image_compression_value = image_compression_value
		self.deviceok = True
		self.timer = eTimer()
		try:
			self.timer.callback.append(self.doBackUpjob)
		except:
			self.timer_conn = self.timer.timeout.connect(self.doBackUpjob)
		self.timer.start(6, 1)

	def doBackUpjob(self):
		if fileExists("/tmp/root"):
			 os.system(f'umount /tmp/root >> {LOG} 2>&1')
		if not fileExists("/tmp/root/usr"):
			 os.system(f"rm -r /tmp/root >> {LOG} 2>&1")
		if fileExists("/tmp/.cancelBackup"):
			 os.system("rm -f /tmp/.cancelBackup")
		self.timer.stop()
		cmdlist = []
		logdata("Backup log","start")
		NOW = datetime.datetime.now()
		logdata("Start Time", NOW.strftime('%H:%M')) ## Print Start time to log file
		if os.path.exists("/etc/init.d/openvpn"):
			os.system(f'/etc/init.d/openvpn stop >> >> {LOG}')
		if self.image_formats == 'xz':
			IMAGENAME = f'{self.image_name}.tar.xz'
			IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
			self.IMAGENAMEPATH = IMAGENAMEPATH
			compression_value=self.image_compression_value
			if fileExists(BRANDOS):
			   COMMANDTAR = f'tar --exclude=smg.sock --exclude msg.sock -cf - -C /tmp/root . | xz -{compression_value} -T 0 -c - > {IMAGENAMEPATH}'
			else:
			   COMMANDTAR = f'tar -cf - -C /tmp/root . | xz -{compression_value}  -T 0 -c - > {IMAGENAMEPATH}'
		else:
			IMAGENAME = 'rootfs.tar'
			IMAGENAMEBZ2 = 'rootfs.tar.bz2'
			IMAGENAME2 = f'{self.image_name}.tar.bz2'
			IMAGENAMEZIP = f'{self.image_name}_usb.zip'
			BUILDFOLDER = f'build_folder/{boxtype}'
			KERNELFILE = '/tmp/root/kernel.bin'
			IMAGEVERSION = '/tmp/imageversion'
			DEVICENAMEPATH = os.path.join(self.device_path, BUILDFOLDER)
			IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
			IMAGENAMEPATHBZ2 = os.path.join(self.device_path, IMAGENAMEBZ2)
			IMAGENAMEPATH2 = os.path.join(self.device_path, IMAGENAME2)
			IMAGENAMEPATHZIP = os.path.join(self.device_path, IMAGENAMEZIP)
			compression_value = self.image_compression_value
			if fileExists(BRANDOS):
			   COMMANDTAR = f'tar -cf - --exclude=smg.sock --exclude msg.sock --exclude ./boot/kernel.img --exclude ./.resizerootfs --exclude ./.resize-rootfs --exclude ./.resize-linuxrootfs --exclude ./.resize-userdata -C /tmp/root . > {IMAGENAMEPATH} && bzip2 {IMAGENAMEPATH}'
			else:
			   COMMANDTAR = f'tar -cf - --exclude ./boot/kernel.img --exclude ./.resizerootfs --exclude ./.resize-rootfs --exclude ./.resize-linuxrootfs --exclude ./.resize-userdata -C /tmp/root . > {IMAGENAMEPATH} && bzip2 {IMAGENAMEPATH}'
		IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
		self.IMAGENAMEPATH = IMAGENAMEPATH
		os.system(resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe/tools/imagebackup.sh'))

		if self.device_path:
			mytitle = _('Backup image')
			cmdlist.append('exec > /tmp/backupflash.scr')
			cmdlist.append(f'Backup ({IMAGENAME}) on [{self.device_path}]\n\n\n')
			cmdlist.append(f'umount /tmp/root >> {LOG} 2>&1')
			cmdlist.append(f'rmdir /tmp/root >> {LOG} 2>&1')
			cmdlist.append(f'mkdir /tmp/root >> {LOG} 2>&1')
			cmdlist.append(f'mount -o bind / /tmp/root >> {LOG} 2>&1')
			if config.backupflashe.cleanba.value:
				cmdlist.append("rm -f /tmp/root/home/root/ba.sh; rm -f /tmp/root/sbin/bainit; rm -f /tmp/root/sbin/ba.sh; rm -f /tmp/root/sbin/init; ln -s /etc/alternatives/init /tmp/root/sbin/init; rm -f /tmp/root/etc/alternatives/init; ln -s /lib/systemd/systemd /tmp/root/etc/alternatives/init")
			cmdlist.append(COMMANDTAR)
			cmdlist.append(f'chmod 777 {IMAGENAMEPATH} >> {LOG}')
			if self.image_formats == 'bz2' and config.backupflashe.Zipcompression.value == False:
				cmdlist.append(f'mv {IMAGENAMEPATH}.bz2 {IMAGENAMEPATH2} >> {LOG}')
			if self.image_formats == 'bz2' and config.backupflashe.Zipcompression.value == True:
				cmdlist.append(f'mkdir -p {DEVICENAMEPATH} >> {LOG}')
				cmdlist.append(f'dd if=/dev/mmcblk0p1 of={KERNELFILE} >> {LOG}')
				cmdlist.append(f'mv {KERNELFILE} {DEVICENAMEPATH} >> {LOG}')
				cmdlist.append(f'mv {IMAGENAMEPATHBZ2} {DEVICENAMEPATH} >> {LOG}')
				cmdlist.append(f'mv {IMAGEVERSION} {DEVICENAMEPATH} >> {LOG}')
				cmdlist.append(f'echo "Rename this file to \'force\' to force an update without confirmation." > {DEVICENAMEPATH}/noforce')
				if fileExists("/tmp/root/usr/lib/enigma.info"):
					cmdlist.append(f'cp /tmp/root/usr/lib/enigma.info {DEVICENAMEPATH} >> {LOG} 2>&1')
				if fileExists("/tmp/root/usr/lib/enigma.conf"):
					cmdlist.append(f'cp /tmp/root/usr/lib/enigma.conf {DEVICENAMEPATH} >> {LOG} 2>&1')
				if fileExists("/tmp/root/etc/image-version"):
					cmdlist.append(f'cp /tmp/root/etc/image-version {DEVICENAMEPATH} >> {LOG} 2>&1')
				cmdlist.append(f'chmod 777 -R {self.device_path}/build_folder* >> {LOG}')
				cmdlist.append(f'7za a -r -bt -bd -bso0 {IMAGENAMEPATHZIP} {DEVICENAMEPATH}* >> {LOG}')
				cmdlist.append(f'rm -r {self.device_path}/build_folder >> {LOG}')
			if os.path.exists("/etc/init.d/openvpn"):
				cmdlist.append(f'/etc/init.d/openvpn start >> {LOG}')
			for item in cmdlist:
				logdata("command",str(item))
			self.session.openWithCallback(self.dofinish, ProgressScreen, title = mytitle, cmdlist = cmdlist, imagePath = self.IMAGENAMEPATH)
		else:
			self.session.open(MessageBox, _('Sorry no device found to store backup.\nPlease check your media in devices manager.'), MessageBox.TYPE_INFO)

	def dofinish(self):
		os.system('umount /tmp/root >> {LOG} 2>&1')
		os.system("rm -r /tmp/root >> {LOG} 2>&1")
		NOW = datetime.datetime.now()
		logdata("Finished Time", NOW.strftime('%H:%M')) ## Print Finished time to log file
		rootfsNAME = 'rootfs.tar'
		IMAGENAMEPATH2 = os.path.join(self.device_path, rootfsNAME)
		if self.image_formats == 'xz':
			IMAGENAME = f'{self.image_name}.tar.xz'
			IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
		elif self.image_formats == 'bz2' and config.backupflashe.Zipcompression.value == False:
			IMAGENAME = f'{self.image_name}.tar.bz2'
			IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
		elif self.image_formats == 'bz2' and config.backupflashe.Zipcompression.value == True:
			IMAGENAME = f'{self.image_name}_usb.zip'
			BUILDFOLDER = f'build_folder/{boxtype}'
			IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
			DEVICENAMEPATH = os.path.join(self.device_path, BUILDFOLDER)

		if fileExists(cancelBackup):
			if os.path.exists(cancelBackup):
				os.remove(cancelBackup)
			if os.path.exists(rootfsNAME):
				os.remove(rootfsNAME)
			if os.path.exists(IMAGENAMEPATH):
			 	os.remove(IMAGENAMEPATH)
			if os.path.exists(DEVICENAMEPATH):
			 	os.remove(DEVICENAMEPATH)
			if os.path.exists(IMAGENAMEPATH2):
			 	os.remove(IMAGENAMEPATH2)
			os.system('umount /tmp/root >> {LOG} 2>&1')
			os.system("rm -r /tmp/root >> {LOG} 2>&1")
			logdata(".\n.\nCancelled Backup !!!!!!")
			self.close()
		else:
			self.session.open(MessageBox, _(f'({IMAGENAME})\non\n[{self.device_path}]\n\nfinished. Press (Exit) or (Ok) Button.'), MessageBox.TYPE_INFO)
			if config.backupflashe.shutdown.value:
					sleep(2)
					logdata("Shutdown Device") ## Print Shutdown to log file
					os.system('shutdown -P -h now')
			self.close()


## BackUp External Flash
class doBackUpExternal(Screen):

	def __init__(self, session, image_name = None, image_path = None, device_path = None, image_formats = None, image_compression_value = 0):
		Screen.__init__(self, session)
		self.list = []
		self['key_red'] = Label(_('Cancel'))
		self['key_green'] = Label(_('Backup'))
		self['lab1'] = Label('')
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'],
			{
				'red': self.close,
				'green': self.doBackUpjob,
				'back': self.close
			})
		self.image_name = image_name
		self.image_path = image_path
		self.device_path = device_path
		self.image_formats = image_formats
		self.image_compression_value = image_compression_value
		self.deviceok = True
		self.timer = eTimer()
		try:
			self.timer.callback.append(self.doBackUpjob)
		except:
			self.timer_conn = self.timer.timeout.connect(self.doBackUpjob)
		self.timer.start(6, 1)

	def doBackUpjob(self):
		if fileExists("/tmp/root"):
			 os.system(f'umount /tmp/root >> {LOG} 2>&1')
		if not fileExists("/tmp/root/usr"):
			 os.system(f"rm -r /tmp/root >> {LOG} 2>&1")
		if fileExists("/tmp/.cancelBackup"):
			 os.system("rm -f /tmp/.cancelBackup")
		self.timer.stop()
		cmdlist = []
		logdata("Backup log","start")
		NOW = datetime.datetime.now()
		logdata("Start Time", NOW.strftime('%H:%M')) ## Print Start time to log file
		if self.image_formats == 'xz':
			IMAGENAME = f'{self.image_name}.tar.xz'
			IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
			self.IMAGENAMEPATH = IMAGENAMEPATH
			compression_value=self.image_compression_value
			if fileExists(BRANDOS):
			   COMMANDTAR = f'tar --exclude=smg.sock --exclude msg.sock -cf - -C /tmp/root . | xz -{compression_value} -T 0 -c - > {IMAGENAMEPATH}'
			else:
			   COMMANDTAR = f'tar -cf - -C /tmp/root . | xz -{compression_value}  -T 0 -c - > {IMAGENAMEPATH}'
		else:
			IMAGENAME = 'rootfs.tar'
			IMAGENAMEBZ2 = 'rootfs.tar.bz2'
			IMAGENAME2 = f'{self.image_name}.tar.bz2'
			IMAGENAMEZIP = f'{self.image_name}_usb.zip'
			BUILDFOLDER = f'build_folder/{boxtype}'
			KERNELFILE = '/tmp/root/kernel.bin'
			IMAGEVERSION = '/tmp/imageversion'
			DEVICENAMEPATH = os.path.join(self.device_path, BUILDFOLDER)
			IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
			IMAGENAMEPATHBZ2 = os.path.join(self.device_path, IMAGENAMEBZ2)
			IMAGENAMEPATH2 = os.path.join(self.device_path, IMAGENAME2)
			IMAGENAMEPATHZIP = os.path.join(self.device_path, IMAGENAMEZIP)
			compression_value = self.image_compression_value
			if fileExists(BRANDOS):
			   COMMANDTAR = f'tar -cf - --exclude=smg.sock --exclude msg.sock --exclude ./boot/kernel.img --exclude ./.resizerootfs --exclude ./.resize-rootfs --exclude ./.resize-linuxrootfs --exclude ./.resize-userdata -C /tmp/root . > {IMAGENAMEPATH} && bzip2 {IMAGENAMEPATH}'
			else:
			   COMMANDTAR = f'tar -cf - --exclude ./boot/kernel.img --exclude ./.resizerootfs --exclude ./.resize-rootfs --exclude ./.resize-linuxrootfs --exclude ./.resize-userdata -C /tmp/root . > {IMAGENAMEPATH} && bzip2 {IMAGENAMEPATH}'
		IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
		self.IMAGENAMEPATH = IMAGENAMEPATH
		os.system(resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe/tools/imagebackup.sh'))

		if self.device_path:
			mytitle = _('Backup image')
			cmdlist.append('exec > /tmp/backupflash.scr')
			cmdlist.append(f'Backup ({IMAGENAME}) on [{self.device_path}]\n\n\n')
			cmdlist.append(f'umount /tmp/root >> {LOG} 2>&1')
			cmdlist.append(f'rmdir /tmp/root >> {LOG} 2>&1')
			cmdlist.append(f'mkdir /tmp/root >> {LOG} 2>&1')
			cmdlist.append(f'mount -o bind {self.image_path}/ /tmp/root >> {LOG} 2>&1')
			if config.backupflashe.cleanba.value:
				cmdlist.append("rm -f /tmp/root/home/root/ba.sh; rm -f /tmp/root/sbin/bainit; rm -f /tmp/root/sbin/ba.sh; rm -f /tmp/root/sbin/init; ln -s /etc/alternatives/init /tmp/root/sbin/init; rm -f /tmp/root/etc/alternatives/init; ln -s /lib/systemd/systemd /tmp/root/etc/alternatives/init")
			cmdlist.append(COMMANDTAR)
			cmdlist.append(f'chmod 777 {IMAGENAMEPATH} >> {LOG}')
			if self.image_formats == 'bz2' and config.backupflashe.Zipcompression.value == False:
				cmdlist.append(f'mv {IMAGENAMEPATH}.bz2 {IMAGENAMEPATH2} >> {LOG}')
			if self.image_formats == 'bz2' and config.backupflashe.Zipcompression.value == True:
				cmdlist.append(f'mkdir -p {DEVICENAMEPATH} >> {LOG}')
				cmdlist.append(f'dd if=/dev/mmcblk0p1 of={KERNELFILE} >> {LOG}')
				cmdlist.append(f'mv {KERNELFILE} {DEVICENAMEPATH} >> {LOG}')
				cmdlist.append(f'mv {IMAGENAMEPATHBZ2} {DEVICENAMEPATH} >> {LOG}')
				cmdlist.append(f'mv {IMAGEVERSION} {DEVICENAMEPATH} >> {LOG}')
				cmdlist.append(f'echo "Rename this file to \'force\' to force an update without confirmation." > {DEVICENAMEPATH}/noforce')
				if fileExists("/tmp/root/usr/lib/enigma.info"):
					cmdlist.append(f'cp /tmp/root/usr/lib/enigma.info {DEVICENAMEPATH} >> {LOG} 2>&1')
				if fileExists("/tmp/root/usr/lib/enigma.conf"):
					cmdlist.append(f'cp /tmp/root/usr/lib/enigma.conf {DEVICENAMEPATH} >> {LOG} 2>&1')
				if fileExists("/tmp/root/etc/image-version"):
					cmdlist.append(f'cp /tmp/root/etc/image-version {DEVICENAMEPATH} >> {LOG} 2>&1')
				cmdlist.append(f'chmod 777 -R {self.device_path}/build_folder* >> {LOG}')
				cmdlist.append(f'7za a -r -bt -bd -bso0 {IMAGENAMEPATHZIP} {DEVICENAMEPATH}* >> {LOG}')
				cmdlist.append(f'rm -r {self.device_path}/build_folder >> {LOG}')
			if os.path.exists("/etc/init.d/openvpn"):
				cmdlist.append(f'/etc/init.d/openvpn start >> {LOG}')
			for item in cmdlist:
				logdata("command",str(item))
			self.session.openWithCallback(self.dofinish, ProgressScreen, title = mytitle, cmdlist = cmdlist, imagePath = self.IMAGENAMEPATH)
		else:
			self.session.open(MessageBox, _('Sorry no device found to store backup.\nPlease check your media in devices manager.'), MessageBox.TYPE_INFO)

	def dofinish(self):
		os.system('umount /tmp/root >> {LOG} 2>&1')
		os.system("rm -r /tmp/root >> {LOG} 2>&1")
		NOW = datetime.datetime.now()
		logdata("Finished Time", NOW.strftime('%H:%M')) ## Print Finished time to log file
		rootfsNAME = 'rootfs.tar'
		if self.image_formats == 'xz':
			IMAGENAME = f'{self.image_name}.tar.xz'
			IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
		elif self.image_formats == 'bz2' and config.backupflashe.Zipcompression.value == False:
			IMAGENAME = f'{self.image_name}.tar.bz2'
			IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
		elif self.image_formats == 'bz2' and config.backupflashe.Zipcompression.value == True:
			IMAGENAME = f'{self.image_name}_usb.zip'
			BUILDFOLDER = f'build_folder/{boxtype}'
			IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
			DEVICENAMEPATH = os.path.join(self.device_path, BUILDFOLDER)

		if fileExists(cancelBackup):
			if os.path.exists(cancelBackup):
				os.remove(cancelBackup)
			if os.path.exists(rootfsNAME):
				os.remove(rootfsNAME)
			if os.path.exists(IMAGENAMEPATH):
			 	os.remove(IMAGENAMEPATH)
			if os.path.exists(DEVICENAMEPATH):
			 	os.remove(DEVICENAMEPATH)
			os.system('umount /tmp/root >> {LOG} 2>&1')
			os.system("rm -r /tmp/root >> {LOG} 2>&1")
			logdata(".\n.\nCancelled Backup !!!!!!")
			self.close()
		else:
			self.session.open(MessageBox, _(f'({IMAGENAME})\non\n[{self.device_path}]\n\nfinished. Press (Exit) or (Ok) Button.'), MessageBox.TYPE_INFO)
			if config.backupflashe.shutdown.value:
					sleep(2)
					logdata("Shutdown Device") ## Print Shutdown to log file
					os.system('shutdown -P -h now')
			self.close()
