#!/usr/bin/python
# -*- coding: utf-8 -*-
# RAED & mfaraj57 (c) 2015 - 2025

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

	def __init__(self, session, image_name = None, device_path = None, image_compression_value = 0):
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
			os.system('umount /tmp/root >> %s 2>&1')
		if not fileExists("/tmp/root/usr"):
			os.system("rm -r /tmp/root >> %s 2>&1")
		if fileExists("/tmp/.cancelBackup"):
			os.system("rm -f /tmp/.cancelBackup")
		self.timer.stop()
		cmdlist = []
		logdata("Backup log","start")
		NOW = datetime.datetime.now()
		logdata("Start Time", NOW.strftime('%H:%M')) ## Print Start time to log file
		if os.path.exists("/etc/init.d/openvpn"):
			os.system('/etc/init.d/openvpn stop >> >> %s' % LOG)
		if config.backupflashe.image_format.value == 'xz':
			IMAGENAME = '%s.tar.xz' % self.image_name
			compression_value = self.image_compression_value
			IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
			if fileExists(BRANDOS):
			   COMMANDTAR = 'tar --exclude=smg.sock --exclude msg.sock -cf - -C /tmp/root . | xz -%s -T 0 -c - > %s' % (compression_value, IMAGENAMEPATH)
			else:
			   COMMANDTAR = 'tar -cf - -C /tmp/root . | xz -%s -T 0 -c - > %s' % (compression_value, IMAGENAMEPATH)
		else:
			IMAGENAME = 'rootfs.tar'
			IMAGENAMEBZ2 = 'rootfs.tar.bz2'
			IMAGENAME2 = '%s.tar.bz2' % self.image_name
			IMAGENAMEZIP = '%s_usb.zip' % self.image_name
			BUILDFOLDER = 'build_folder/%s' % boxtype
			KERNELFILE = '/tmp/root/kernel.bin'
			IMAGEVERSION = '/tmp/imageversion'
			IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
			BUILDFOLDER_TMP = os.path.join(self.device_path, "build_folder")
			DEVICENAMEPATH = os.path.join(self.device_path, BUILDFOLDER)
			IMAGENAMEPATHBZ2 = os.path.join(self.device_path, IMAGENAMEBZ2)
			IMAGENAMEPATH2 = os.path.join(self.device_path, IMAGENAME2)
			IMAGENAMEPATHZIP = os.path.join(self.device_path, IMAGENAMEZIP)
			try:
				if fileExists(IMAGENAMEPATH):
					os.remove(IMAGENAMEPATH)
				if fileExists(IMAGENAMEPATHBZ2):
					os.remove(IMAGENAMEPATHBZ2)
				if fileExists(BUILDFOLDER_TMP):
					os.remove(BUILDFOLDER_TMP)
			except:
				pass
			compression_value = self.image_compression_value
			if fileExists(BRANDOS):
				COMMANDTAR = 'tar -cf - --exclude=smg.sock --exclude msg.sock --exclude ./boot/kernel.img --exclude ./.resizerootfs --exclude ./.resize-rootfs --exclude ./.resize-linuxrootfs --exclude ./.resize-userdata -C /tmp/root . > %s && bzip2 %s' % (IMAGENAMEPATH, IMAGENAMEPATH)
			else:
				COMMANDTAR = 'tar -cf - --exclude ./boot/kernel.img --exclude ./.resizerootfs --exclude ./.resize-rootfs --exclude ./.resize-linuxrootfs --exclude ./.resize-userdata -C /tmp/root . > %s && bzip2 %s' % (IMAGENAMEPATH, IMAGENAMEPATH)
		script_path = resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe/tools/imagebackup.sh')
		os.system('chmod 755 "%s"' % script_path)
		os.system('"%s"' % script_path)

		if self.device_path:
			mytitle = _('Backup image')
			self.IMAGENAMEPATH = IMAGENAMEPATH
			cmdlist.append('exec > /tmp/backupflash.scr')
			cmdlist.append('Backup (%s) on [%s]\n\n\n ' % (IMAGENAME, self.device_path))
			cmdlist.append('umount /tmp/root >> %s 2>&1' % LOG)
			cmdlist.append('rmdir /tmp/root >> %s 2>&1' % LOG)
			cmdlist.append('mkdir /tmp/root >> %s 2>&1' % LOG)
			cmdlist.append('mount -o bind / /tmp/root >> %s 2>&1' % LOG)
			if config.backupflashe.cleanba.value:
				cmdlist.append("rm -f /tmp/root/home/root/ba.sh; rm -f /tmp/root/sbin/bainit; rm -f /tmp/root/sbin/ba.sh; rm -f /tmp/root/sbin/init; ln -s /etc/alternatives/init /tmp/root/sbin/init; rm -f /tmp/root/etc/alternatives/init; ln -s /lib/systemd/systemd /tmp/root/etc/alternatives/init")
			cmdlist.append(COMMANDTAR)
			cmdlist.append('chmod 777 %s >> %s' % (IMAGENAMEPATH, LOG))
			if config.backupflashe.image_format.value == 'bz2' and config.backupflashe.Zipcompression.value == False:
				cmdlist.append('mv %s.bz2 %s >> %s' % (IMAGENAMEPATH, IMAGENAMEPATH2, LOG))
			if config.backupflashe.image_format.value == 'bz2' and config.backupflashe.Zipcompression.value == True:
				print(" Start Zip *************************************")
				cmdlist.append('mkdir -p %s >> %s' % (DEVICENAMEPATH, LOG))
				cmdlist.append('dd if=/dev/mmcblk0p1 of=%s >> %s' % (KERNELFILE, LOG))
				cmdlist.append('mv %s %s >> %s' % (KERNELFILE, DEVICENAMEPATH, LOG))
				cmdlist.append('mv %s %s >> %s' % (IMAGENAMEPATHBZ2, DEVICENAMEPATH, LOG))
				cmdlist.append('mv %s %s >> %s' % (IMAGEVERSION, DEVICENAMEPATH, LOG))
				cmdlist.append('echo "Rename this file to \'force\' to force an update without confirmation." > %s/noforce' % DEVICENAMEPATH)
				if fileExists("/tmp/root/usr/lib/enigma.info"):
					cmdlist.append('cp /tmp/root/usr/lib/enigma.info %s >> %s 2>&1' % (DEVICENAMEPATH, LOG))
				if fileExists("/tmp/root/usr/lib/enigma.conf"):
					cmdlist.append('cp /tmp/root/usr/lib/enigma.conf %s >> %s 2>&1' % (DEVICENAMEPATH, LOG))
				if fileExists("/tmp/root/etc/image-version"):
					cmdlist.append('cp /tmp/root/etc/image-version %s >> %s 2>&1' % (DEVICENAMEPATH, LOG))
				cmdlist.append('chmod 777 -R %s/build_folder* >> %s' % (self.device_path, LOG))
				if fileExists(BRANDOS):
					cmdlist.append('7za a -r %s %s* >> %s' % (IMAGENAMEPATHZIP, DEVICENAMEPATH, LOG))
				else:
					cmdlist.append('7za a -r -bt -bd -bso0 %s %s* >> %s' % (IMAGENAMEPATHZIP, DEVICENAMEPATH, LOG))
					print(f" Start Zip2 ************************************* {cmdlist.append('7za a -r -bt -bd -bso0 %s %s* >> %s' % (IMAGENAMEPATHZIP, DEVICENAMEPATH, LOG))}")
				cmdlist.append('rm -r %s/build_folder >> %s' % (self.device_path, LOG))
			if os.path.exists("/etc/init.d/openvpn"):
				cmdlist.append('/etc/init.d/openvpn start >> %s' % LOG)
			for item in cmdlist:
				logdata("command",str(item))
			self.session.openWithCallback(self.dofinish, ProgressScreen, title = mytitle, cmdlist = cmdlist, imagePath = self.IMAGENAMEPATH)
		else:
			self.session.open(MessageBox, _('Sorry no device found to store backup.\nPlease check your media in devices manager.'), MessageBox.TYPE_INFO)

	def dofinish(self):
		os.system('umount /tmp/root >> %s 2>&1' % LOG)
		os.system("rm -r /tmp/root >> %s 2>&1" % LOG)
		NOW = datetime.datetime.now()
		logdata("Finished Time", NOW.strftime('%H:%M')) ## Print Finished time to log file
		rootfsNAME = 'rootfs.tar'
		rootfsNAMEbz2 = 'rootfs.tar.bz2'
		IMAGENAME = None
		IMAGENAMEPATH = None
		IMAGENAMEPATH2 = os.path.join(self.device_path, rootfsNAME)
		IMAGENAMEPATH3 = os.path.join(self.device_path, rootfsNAMEbz2)		
		if config.backupflashe.image_format.value == 'xz':
			IMAGENAME = '%s.tar.xz' % self.image_name
			IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
		elif config.backupflashe.image_format.value == 'bz2' and config.backupflashe.Zipcompression.value == False:
			IMAGENAME = '%s.tar.bz2' % self.image_name
			IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
		elif config.backupflashe.image_format.value == 'bz2' and config.backupflashe.Zipcompression.value == True:
			IMAGENAME = '%s_usb.zip' % self.image_name
			BUILDFOLDER = 'build_folder/%s' % boxtype
			IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
			DEVICENAMEPATH = os.path.join(self.device_path, BUILDFOLDER)
		if fileExists(cancelBackup):
			try:
				os.system("kill -9 $(ps aux | grep imagebackup.sh | awk '{print $2}')")
				os.remove(cancelBackup)
				if IMAGENAMEPATH and fileExists(IMAGENAMEPATH):
			 		os.remove(IMAGENAMEPATH)
				if fileExists(IMAGENAMEPATH2):
			 		os.remove(IMAGENAMEPATH2)
				if fileExists(IMAGENAMEPATH3):
			 		os.remove(IMAGENAMEPATH3)
				if os.path.exists(DEVICENAMEPATH):
			 		os.remove(DEVICENAMEPATH)
			except:
				pass
			os.system('umount /tmp/root >> %s 2>&1' % LOG)
			os.system("rm -r /tmp/root >> %s 2>&1" % LOG)
			logdata(".\n.\nCancelled Backup !!!!!!")
			self.close()
		else:
			self.session.open(MessageBox, _('(%s)\non\n[%s]\n\nfinished. Press (Exit) or (Ok) Button.' % (IMAGENAME, self.device_path)), MessageBox.TYPE_INFO)
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
			os.system('umount /tmp/root >> %s 2>&1')
		if not fileExists("/tmp/root/usr"):
			os.system("rm -r /tmp/root >> %s 2>&1")
		if fileExists("/tmp/.cancelBackup"):
			os.system("rm -f /tmp/.cancelBackup")
		self.timer.stop()
		cmdlist = []
		logdata("Backup log","start")
		NOW = datetime.datetime.now()
		logdata("Start Time", NOW.strftime('%H:%M')) ## Print Start time to log file
		if config.backupflashe.image_format.value == 'xz':
			IMAGENAME = '%s.tar.xz' % self.image_name
			IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
			compression_value=self.image_compression_value
			if fileExists(BRANDOS):
			   COMMANDTAR = 'tar --exclude=smg.sock --exclude msg.sock -cf - -C /tmp/root . | xz -%s -T 0 -c - > %s' % (compression_value, IMAGENAMEPATH)
			else:
			   COMMANDTAR = 'tar -cf - -C /tmp/root . | xz -%s -T 0 -c - > %s' % (compression_value, IMAGENAMEPATH)
		else:
			IMAGENAME = 'rootfs.tar'
			IMAGENAMEBZ2 = 'rootfs.tar.bz2'
			IMAGENAME2 = '%s.tar.bz2' % self.image_name
			IMAGENAMEZIP = '%s_usb.zip' % self.image_name
			BUILDFOLDER = 'build_folder/%s' % boxtype
			KERNELFILE = '/tmp/root/kernel.bin'
			IMAGEVERSION = '/tmp/imageversion'
			BUILDFOLDER_TMP = os.path.join(self.device_path, "build_folder")
			DEVICENAMEPATH = os.path.join(self.device_path, BUILDFOLDER)
			IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
			IMAGENAMEPATHBZ2 = os.path.join(self.device_path, IMAGENAMEBZ2)
			IMAGENAMEPATH2 = os.path.join(self.device_path, IMAGENAME2)
			IMAGENAMEPATHZIP = os.path.join(self.device_path, IMAGENAMEZIP)
			try:
				if fileExists(IMAGENAMEPATH):
					os.remove(IMAGENAMEPATH)
				if fileExists(IMAGENAMEPATHBZ2):
					os.remove(IMAGENAMEPATHBZ2)
				if fileExists(BUILDFOLDER_TMP):
					os.remove(BUILDFOLDER_TMP)
			except:
				pass
			compression_value = self.image_compression_value
			if fileExists(BRANDOS):
				COMMANDTAR = 'tar -cf - --exclude=smg.sock --exclude msg.sock --exclude ./boot/kernel.img --exclude ./.resizerootfs --exclude ./.resize-rootfs --exclude ./.resize-linuxrootfs --exclude ./.resize-userdata -C /tmp/root . > %s && bzip2 %s' % (IMAGENAMEPATH, IMAGENAMEPATH)
			else:
				COMMANDTAR = 'tar -cf - --exclude ./boot/kernel.img --exclude ./.resizerootfs --exclude ./.resize-rootfs --exclude ./.resize-linuxrootfs --exclude ./.resize-userdata -C /tmp/root . > %s && bzip2 %s' % (IMAGENAMEPATH, IMAGENAMEPATH)
		script_path = resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe/tools/imagebackup.sh')
		os.system('chmod 755 "%s"' % script_path)
		os.system('"%s"' % script_path)

		if self.device_path:
			mytitle = _('Backup image')
			self.IMAGENAMEPATH = IMAGENAMEPATH
			cmdlist.append('exec > /tmp/backupflash.scr')
			cmdlist.append('Backup (%s) on [%s]\n\n\n ' % (IMAGENAME, self.device_path))
			cmdlist.append('umount /tmp/root >> %s 2>&1' % LOG)
			cmdlist.append('rmdir /tmp/root >> %s 2>&1' % LOG)
			cmdlist.append('mkdir /tmp/root >> %s 2>&1' % LOG)
			cmdlist.append('mount -o bind %s/ /tmp/root >> %s 2>&1' % (self.image_path, LOG))
			if config.backupflashe.cleanba.value:
				cmdlist.append("rm -f /tmp/root/home/root/ba.sh; rm -f /tmp/root/sbin/bainit; rm -f /tmp/root/sbin/ba.sh; rm -f /tmp/root/sbin/init; ln -s /etc/alternatives/init /tmp/root/sbin/init; rm -f /tmp/root/etc/alternatives/init; ln -s /lib/systemd/systemd /tmp/root/etc/alternatives/init")
			cmdlist.append(COMMANDTAR)
			cmdlist.append('chmod 777 %s >> %s' % (IMAGENAMEPATH, LOG))
			if config.backupflashe.image_format.value == 'bz2' and config.backupflashe.Zipcompression.value == False:
				cmdlist.append('mv %s.bz2 %s >> %s' % (IMAGENAMEPATH, IMAGENAMEPATH2, LOG))
			if config.backupflashe.image_format.value == 'bz2' and config.backupflashe.Zipcompression.value == True:
				cmdlist.append('mkdir -p %s >> %s' % (DEVICENAMEPATH, LOG))
				cmdlist.append('dd if=/dev/mmcblk0p1 of=%s >> %s' % (KERNELFILE, LOG))
				cmdlist.append('mv %s %s >> %s' % (KERNELFILE, DEVICENAMEPATH, LOG))
				cmdlist.append('mv %s %s >> %s' % (IMAGENAMEPATHBZ2, DEVICENAMEPATH, LOG))
				cmdlist.append('mv %s %s >> %s' % (IMAGEVERSION, DEVICENAMEPATH, LOG))
				cmdlist.append('echo "Rename this file to \'force\' to force an update without confirmation." > %s/noforce' % DEVICENAMEPATH)
				if fileExists("/tmp/root/usr/lib/enigma.info"):
					cmdlist.append('cp /tmp/root/usr/lib/enigma.info %s >> %s 2>&1' % (DEVICENAMEPATH, LOG))
				if fileExists("/tmp/root/usr/lib/enigma.conf"):
					cmdlist.append('cp /tmp/root/usr/lib/enigma.conf %s >> %s 2>&1' % (DEVICENAMEPATH, LOG))
				if fileExists("/tmp/root/etc/image-version"):
					cmdlist.append('cp /tmp/root/etc/image-version %s >> %s 2>&1' % (DEVICENAMEPATH, LOG))
				cmdlist.append('chmod 777 -R %s/build_folder* >> %s' % (self.device_path, LOG))
				if fileExists(BRANDOS):
					cmdlist.append('7za a -r %s %s* >> %s' % (IMAGENAMEPATHZIP, DEVICENAMEPATH, LOG))
				else:
					cmdlist.append('7za a -r -bt -bd -bso0 %s %s* >> %s' % (IMAGENAMEPATHZIP, DEVICENAMEPATH, LOG))
				cmdlist.append('rm -r %s/build_folder >> %s' % (self.device_path, LOG))
			if os.path.exists("/etc/init.d/openvpn"):
				cmdlist.append('/etc/init.d/openvpn start >> %s' % LOG)
			for item in cmdlist:
				logdata("command",str(item))
			self.session.openWithCallback(self.dofinish, ProgressScreen, title = mytitle, cmdlist = cmdlist, imagePath = self.IMAGENAMEPATH)
		else:
			self.session.open(MessageBox, _('Sorry no device found to store backup.\nPlease check your media in devices manager.'), MessageBox.TYPE_INFO)

	def dofinish(self):
		os.system('umount /tmp/root >> %s 2>&1' % LOG)
		os.system("rm -r /tmp/root >> %s 2>&1" % LOG)
		NOW = datetime.datetime.now()
		logdata("Finished Time", NOW.strftime('%H:%M')) ## Print Finished time to log file
		IMAGENAME = ""
		rootfsNAME = 'rootfs.tar'
		rootfsNAMEbz2 = 'rootfs.tar.bz2'
		IMAGENAME = None
		IMAGENAMEPATH = None
		IMAGENAMEPATH2 = os.path.join(self.device_path, rootfsNAME)
		IMAGENAMEPATH3 = os.path.join(self.device_path, rootfsNAMEbz2)
		if config.backupflashe.image_format.value == 'xz':
			IMAGENAME = '%s.tar.xz' % self.image_name
			IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
		elif config.backupflashe.image_format.value == 'bz2' and config.backupflashe.Zipcompression.value == False:
			IMAGENAME = '%s.tar.bz2' % self.image_name
			IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
		elif config.backupflashe.image_format.value == 'bz2' and config.backupflashe.Zipcompression.value == True:
			IMAGENAME = '%s_usb.zip' % self.image_name
			BUILDFOLDER = 'build_folder/%s' % boxtype
			IMAGENAMEPATH = os.path.join(self.device_path, IMAGENAME)
			DEVICENAMEPATH = os.path.join(self.device_path, BUILDFOLDER)
		if fileExists(cancelBackup):
			try:
				os.system("kill -9 $(ps aux | grep imagebackup.sh | awk '{print $2}')")
				os.remove(cancelBackup)
				if IMAGENAMEPATH and fileExists(IMAGENAMEPATH):
			 		os.remove(IMAGENAMEPATH)
				if fileExists(IMAGENAMEPATH2):
			 		os.remove(IMAGENAMEPATH2)
				if fileExists(IMAGENAMEPATH3):
			 		os.remove(IMAGENAMEPATH3)
				if os.path.exists(DEVICENAMEPATH):
			 		os.remove(DEVICENAMEPATH)
			except:
				pass
			os.system('umount /tmp/root >> %s 2>&1' % LOG)
			os.system("rm -r /tmp/root >> %s 2>&1" % LOG)
			logdata(".\n.\nCancelled Backup !!!!!!")
			self.close()
		else:
			self.session.open(MessageBox, _('(%s)\non\n[%s]\n\nfinished. Press (Exit) or (Ok) Button.' % (IMAGENAME, self.device_path)), MessageBox.TYPE_INFO)
			if config.backupflashe.shutdown.value:
					sleep(2)
					logdata("Shutdown Device") ## Print Shutdown to log file
					os.system('shutdown -P -h now')
			self.close()
