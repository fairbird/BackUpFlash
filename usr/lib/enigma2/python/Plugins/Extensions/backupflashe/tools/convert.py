#!/usr/bin/python
# -*- coding: utf-8 -*-
# RAED (c) 2025

from Components.Label import Label
from Components.config import config
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS
from enigma import eTimer
from time import sleep
import os, datetime, re

from .Console import Console
from .progress import ProgressScreen 
from .bftools import logdata, dellog, copylog, getboxtype

boxtype = getboxtype()
		
cancelBackup = "/tmp/.cancelBackup"
LOG = '/tmp/backupflash.scr'
SCRIPT = '/tmp/backupflash_Convert.sh'


class doConvert(Screen):

	def __init__(self, session, device_path = None, getname = None):
		Screen.__init__(self, session)
		self.list = []
		self['key_red'] = Label(_('Cancel'))
		self['key_green'] = Label(_('Convert'))
		self['lab1'] = Label('')
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'],
		{
			'red': self.close,
			'green': self.doConvertjob,
			'back': self.close
		})
		self.getname = getname
		self.device_path = device_path
		self.deviceok = True
		self.timer = eTimer()
		try:
			self.timer.callback.append(self.doConvertjob)
		except:
			self.timer_conn = self.timer.timeout.connect(self.doConvertjob)
		self.timer.start(6, 1)

	def checkonetwoimage(self):
		name = self.getname.lower()  # Convert to lowercase for case-insensitive check
		return any(x in name for x in ['dreamone', 'dreamtwo', 'dreambox', 'AIO'])

	def doConvertjob(self):
		self.timer.stop()
		cmdlist = []
		logdata("Convert log","start")
		NOW = datetime.datetime.now()
		logdata("Start Time", NOW.strftime('%H:%M')) ## Print Start time to log file
		build_folder = 'build_folder'
		IMAGENAME = 'rootfs.tar'
		IMAGENAMEBZ2 = 'rootfs.tar.bz2'
		match = re.match(r"^(.*?)-\d+\.tar\.xz$", self.getname)
		if match:
			NAMEIMAGE = match.group(1)
		else:
			NAMEIMAGE = "Dreambox"
		name = self.getname.lower()
		if name.endswith('.rootfs.tar.xz'):
			REALNAME = "{}".format(self.getname.split(".rootfs.tar.xz")[0])
		elif name.endswith('.tar.xz'):
			REALNAME = "{}".format(self.getname.split(".tar.xz")[0])
		IMAGENAMEPATH = os.path.join(self.device_path, self.getname)
		BUILDFOLDER = os.path.join(self.device_path, build_folder)
		IMAGENAMEPATH_TMP = os.path.join(self.device_path, IMAGENAME)
		IMAGENAMEPATHBZ2_TMP = os.path.join(self.device_path, IMAGENAMEBZ2)
		IMAGENAME = os.path.join(self.device_path, REALNAME)
		self.IMAGENAMEPATH = IMAGENAMEPATH
		if fileExists(BUILDFOLDER):
			os.remove(BUILDFOLDER)
		if fileExists(IMAGENAMEPATH_TMP):
			os.remove(IMAGENAMEPATH_TMP)
		if fileExists(IMAGENAMEPATHBZ2_TMP):
			os.remove(IMAGENAMEPATHBZ2_TMP)
		if self.device_path:
			if os.path.exists(SCRIPT):
				os.remove(SCRIPT)
			if os.path.exists(BUILDFOLDER):
				os.system("rm -f %s" % BUILDFOLDER)
			mytitle = _('Convert image')
			cmdlist.append('exec > /tmp/backupflash.scr')
			cmdlist.append('Convert (%s) on [%s]\n\n\n' % (self.getname, self.device_path))
			if self.checkonetwoimage():
				os.system('echo "#!/bin/bash\n" > %s' % SCRIPT)
				os.system('echo "mkdir -p %s" >> %s' % (BUILDFOLDER, SCRIPT))
				os.system('echo "mkdir -p %s/%s" >> %s' % (BUILDFOLDER, boxtype, SCRIPT))
				os.system('echo "mkdir -p %s/tmp_image" >> %s' % (BUILDFOLDER, SCRIPT))
				os.system('echo "tar -xf %s -C %s/tmp_image" >> %s' % (IMAGENAMEPATH, BUILDFOLDER, SCRIPT))
				os.system('echo "chmod 777 -R %s/tmp_image" >> %s' % (BUILDFOLDER, SCRIPT))
				os.system('echo "echo \\"%s \\n \\l\\" > %s/tmp_image/etc/issue" >> %s' % (NAMEIMAGE, BUILDFOLDER, SCRIPT))
				os.system('echo "echo \\"\\n \\l\\" >> %s/tmp_image/etc/issue" >> %s' % (BUILDFOLDER, SCRIPT))
				os.system('echo "cp -f %s/tmp_image/boot/Image.gz-4.9" "%s/%s/kernel.bin" >> %s' % (BUILDFOLDER, BUILDFOLDER, boxtype, SCRIPT))
				os.system('echo "echo %s > %s/%s/imageversion" >> %s' % (REALNAME, BUILDFOLDER, boxtype, SCRIPT))
				os.system('echo "tar -cjf "%s/rootfs.tar.bz2" -C "%s/*"" >> %s' % (BUILDFOLDER, BUILDFOLDER, SCRIPT))
			else:
				os.system('echo "#!/bin/bash\n" > %s' % SCRIPT)
				os.system('echo "mkdir -p %s" >> %s' % (BUILDFOLDER, SCRIPT))
				os.system('echo "mkdir -p %s/%s" >> %s' % (BUILDFOLDER, boxtype, SCRIPT))
				os.system('echo "xz -dc %s > %s/rootfs.tar" >> %s' % (IMAGENAMEPATH, BUILDFOLDER, SCRIPT))
				os.system('echo "bzip2 %s/rootfs.tar" >> %s' % (BUILDFOLDER, SCRIPT))
				os.system('echo "touch %s/%s/kernel.bin" >> %s' % (BUILDFOLDER, boxtype, SCRIPT))
				os.system('echo "echo %s > %s/%s/eimageversion.txt" >> %s' % (REALNAME, BUILDFOLDER, boxtype, SCRIPT))
			os.system('echo "mv %s/rootfs.tar.bz2 %s/%s" >> %s' % (BUILDFOLDER, BUILDFOLDER, boxtype, SCRIPT))
			os.system('echo "chmod 777 -R %s/%s/*" >> %s' % (BUILDFOLDER, boxtype, SCRIPT))
			os.system('echo "7za a -r %s.zip %s/%s" >> %s' % (IMAGENAME, BUILDFOLDER, boxtype, SCRIPT))
			os.system('echo "rm -r %s" >> %s' % (BUILDFOLDER, SCRIPT))
			#os.system('echo "rm -f %s" >> %s' % (SCRIPT, SCRIPT))
			os.system('echo "\n" >> %s' % SCRIPT)
			os.system('echo "exit 0" >> %s' % SCRIPT)
			cmdlist.append('sleep 2')
			cmdlist.append('chmod 755 %s && %s &' % (SCRIPT, SCRIPT))
			cmdlist.append('sleep 2')
			for item in cmdlist:
				logdata("command",str(item))
			self.session.openWithCallback(self.dofinish, ProgressScreen, endstr=mytitle, cmdlist=cmdlist, imagePath=self.IMAGENAMEPATH)
		else:
			self.session.open(MessageBox, _('Sorry no device found to convert image.\nPlease check your media in devices manager.'), MessageBox.TYPE_INFO)

	def dofinish(self):
		NOW = datetime.datetime.now()
		name = self.getname.lower()
		if name.endswith('.rootfs.tar.xz'):
			ZIPNAME = "{}.zip".format(self.getname.split(".rootfs.tar.xz")[0])
		elif name.endswith('.tar.xz'):
			ZIPNAME = "{}.zip".format(self.getname.split(".tar.xz")[0])
		IMAGEZIPNAME = os.path.join(self.device_path, ZIPNAME)
		build_folder = 'build_folder'
		BUILDFOLDER = os.path.join(self.device_path, build_folder)
		logdata("Finished Time", NOW.strftime('%H:%M')) ## Print Finished time to log file
		if fileExists(cancelBackup):
			try:
				os.remove(cancelBackup)
				if os.path.exists(BUILDFOLDER):
					os.system("rm -r %s" % BUILDFOLDER)
				if os.path.exists(IMAGEZIPNAME):
					os.remove(IMAGEZIPNAME)
				if os.path.exists(SCRIPT):
					os.remove(SCRIPT)
			except:
				pass
			logdata(".\n.\nCancelled Converting !!!!!!")
			self.close()
		else:
			self.session.open(MessageBox, _('(%s)\non\n[%s]\n\nfinished. Press (Exit) or (Ok) Button.' % (ZIPNAME, self.device_path)), MessageBox.TYPE_INFO)
			if config.backupflashe.shutdown.value:
					sleep(2)
					logdata("Shutdown Device") ## Print Shutdown to log file
					os.system('shutdown -P -h now')
			self.close()
