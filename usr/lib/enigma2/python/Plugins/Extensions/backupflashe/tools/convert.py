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
import os, datetime

from .Console import Console
from .progress import ProgressScreen 
from .bftools import logdata, dellog, copylog, getboxtype

boxtype = getboxtype()
		
cancelBackup = "/tmp/.cancelBackup"
LOG = '/tmp/backupflash.scr'
SCRIPT = '/tmp/backupflash_Convert.sh'

# Ensure compatibility with Python 2 and 3
try:
	basestring  # Python 2
except NameError:
	basestring = str  # Python 3


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

	def doConvertjob(self):
		self.timer.stop()
		cmdlist = []
		logdata("Convert log","start")
		NOW = datetime.datetime.now()
		logdata("Start Time", NOW.strftime('%H:%M')) ## Print Start time to log file
		build_folder = 'build_folder'
		ZIPNAME = "{}.zip".format(self.getname.split(".rootfs.tar.xz")[0])
		IMAGENAMEPATH = os.path.join(self.device_path, self.getname)
		BUILDFOLDER = os.path.join(self.device_path, build_folder)
		IMAGEZIPNAME = os.path.join(self.device_path, ZIPNAME)
		self.IMAGENAMEPATH = IMAGENAMEPATH
		if self.device_path:
			if os.path.exists(SCRIPT):
				os.remove(SCRIPT)
			if os.path.exists(BUILDFOLDER):
				os.system("rm -f %s" % BUILDFOLDER)
			mytitle = _('Convert image')
			cmdlist.append('exec > /tmp/backupflash.scr')
			cmdlist.append('Convert (%s) on [%s]\n\n\n' % (self.getname, self.device_path))
			os.system('echo "#!/bin/bash\n" > %s' % SCRIPT)
			os.system('echo "mkdir -p %s" >> %s' % (BUILDFOLDER, SCRIPT))
			os.system('echo "mkdir -p %s/box" >> %s' % (BUILDFOLDER, SCRIPT))
			os.system('echo "xz -dc %s > %s/rootfs.tar" >> %s' % (IMAGENAMEPATH, BUILDFOLDER, SCRIPT))
			os.system('echo "bzip2 %s/rootfs.tar" >> %s' % (BUILDFOLDER, SCRIPT))
			os.system('echo "mv %s/rootfs.tar.bz2 %s/box" >> %s' % (BUILDFOLDER, BUILDFOLDER, SCRIPT))
			os.system('echo "touch %s/box/kernel.bin" >> %s' % (BUILDFOLDER, SCRIPT))
			os.system('echo "echo %s > %s/box/eimageversion.txt" >> %s' % (self.getname, BUILDFOLDER, SCRIPT))
			os.system('echo "chmod 777 -R %s/box/*" >> %s' % (BUILDFOLDER, SCRIPT))
			os.system('echo "7za a -r %s %s/box/*" >> %s' % (IMAGEZIPNAME, BUILDFOLDER, SCRIPT))
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
		ZIPNAME = "{}.zip".format(self.getname.split(".rootfs.tar.xz")[0])
		IMAGEZIPNAME = os.path.join(self.device_path, ZIPNAME)
		build_folder = 'build_folder'
		BUILDFOLDER = os.path.join(self.device_path, build_folder)
		logdata("Finished Time", NOW.strftime('%H:%M')) ## Print Finished time to log file
		if fileExists(cancelBackup):
			if os.path.exists(BUILDFOLDER):
				os.system("rm -r %s" % BUILDFOLDER)
			if os.path.exists(IMAGEZIPNAME):
				os.remove(IMAGEZIPNAME)
			if os.path.exists(SCRIPT):
				os.remove(SCRIPT)
			logdata(".\n.\nCancelled Converting !!!!!!")
			self.close()
		else:
			self.session.open(MessageBox, _('(%s)\non\n[%s]\n\nfinished. Press (Exit) or (Ok) Button.' % (ZIPNAME, self.device_path)), MessageBox.TYPE_INFO)
			if config.backupflashe.shutdown.value:
					sleep(2)
					logdata("Shutdown Device") ## Print Shutdown to log file
					os.system('shutdown -P -h now')
			self.close()
