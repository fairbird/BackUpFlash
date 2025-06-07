#!/usr/bin/python
# -*- coding: utf-8 -*-
# RAED & mfaraj57 (c) 2018 - 2025

from enigma import eTimer, quitMainloop, getDesktop
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Plugins.Plugin import PluginDescriptor
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, fileExists, pathExists, SCOPE_MEDIA, SCOPE_PLUGINS
from Components.FileList import FileList
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.MenuList import MenuList
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, ConfigSubsection, config, ConfigYesNo, ConfigSelection, NoSave, configfile, ConfigText
from os import listdir as os_listdir
import datetime
import os

from Plugins.Extensions.backupflashe.tools.skin import *
from Plugins.Extensions.backupflashe.tools.backup import *
from Plugins.Extensions.backupflashe.tools.bftools import *
from Plugins.Extensions.backupflashe.tools.convert import *
from Plugins.Extensions.backupflashe.tools.compat import PY3
from Plugins.Extensions.backupflashe.tools.Console import Console


BRANDOS = '/var/lib/dpkg/status'  # DreamOS
BAINIT = '/sbin/bainit'
BAINFO = '/.bainfo'

boxtype = getboxtype()

Ver = getversioninfo()

XZ_, PIGZ_, ZIP_, WGET_ = get_package()

config.backupflashe = ConfigSubsection()

config.backupflashe.update = ConfigYesNo(default=True)
config.backupflashe.shutdown = ConfigYesNo(default=False)
config.backupflashe.cleanba = ConfigYesNo(default=False)
config.backupflashe.flashAllow = ConfigYesNo(default=False)
config.backupflashe.Zipcompression = ConfigYesNo(default=False)
config.backupflashe.path_left = ConfigText(default=resolveFilename(SCOPE_MEDIA))
config.backupflashe.showplugin = ConfigText(default="")

image_formats = [('xz', 'xz'), ('bz2', 'bz2')]
config.backupflashe.image_format = ConfigSelection(default="xz", choices=image_formats)
xz_options = []
if boxtype == "dm520":
	xz_options.append(("1", "1"))
	xz_options.append(("2", "2"))
	xz_options.append(("3", "3"))
	xz_options.append(("4", "4"))
else:
	xz_options.append(("1", "1"))
	xz_options.append(("2", "2"))
	xz_options.append(("3", "3"))
	xz_options.append(("4", "4"))
	xz_options.append(("5", "5"))
	xz_options.append(("6", "6"))

config.backupflashe.xzcompression = ConfigSelection(default="1", choices=xz_options)
config.backupflashe.bz2compression = ConfigSelection(default="3", choices=xz_options)

if config.backupflashe.image_format.value == "xz":
	imagecompressionvalue = config.backupflashe.xzcompression.value
else:
	imagecompressionvalue = config.backupflashe.bz2compression.value

k = open("/proc/cmdline", "r")
cmd = k.read()
k.close()

mounted_devices = getmDevices()
getname = getimage_name()
now = datetime.datetime.now()
DATETIME = now.strftime('%Y-%m-%d-%H-%M')

if boxtype == "dm520":
	if cmd.find("root=/dev/sda1") != -1:
		rootfs = "root=/dev/sda1"
	else:
		rootfs = "root=ubi0:dreambox-rootfs"
else:
	rootfs = "root=/dev/mmcblk0"


# Path of images on External Flash checking
searchPaths = []

def initPaths():
	if fileExists("/proc/mounts"):
		for line in open("/proc/mounts"):
			if "/dev/sd" in line or "/dev/disk/by-uuid/" in line or "/dev/mmc" in line:
				Path = line.split()[1].replace("\\040", " ").split(",")
				for dirName in Path:
					if os.path.isdir(dirName + "/open-multiboot"):
						return searchPaths.append(dirName + "/open-multiboot")
					elif os.path.isdir(dirName + "/ImageBoot"):
						return searchPaths.append(dirName + "/ImageBoot")
	return


initPaths()
CHECKBOOT = ''.join(searchPaths).split("/")[-1]

if os.path.isdir("/media/ba/ba"):
	IMAGLISTEPATH = "/media/ba/ba"  # Directory of BarryAllen images
	ExternalImages = True
	TEXT_CHOOSE = _("Images from BarryAllen")
elif os.path.isdir("/media/at"):
	IMAGLISTEPATH = "/media/at"  # Directory of AlanTuring images
	ExternalImages = True
	TEXT_CHOOSE = _("Images from AlanTuring")
elif os.path.isdir("/media/egamiboot/EgamiBootI"):
	IMAGLISTEPATH = "/media/egamiboot/EgamiBootI"  # Directory of Egami images
	ExternalImages = True
	TEXT_CHOOSE = _("Images from AlanTuring")
elif os.path.isdir(''.join(searchPaths)):
	# Directory of OpenMultiboot/NeoBoot images
	IMAGLISTEPATH = ''.join(searchPaths)
	ExternalImages = True
	if CHECKBOOT == "open-multiboot":
		NAMEBOOT = "OpenMultiboot"
	elif CHECKBOOT == "ImageBoot":
		NAMEBOOT = "NeoBoot"
	else:
		NAMEBOOT = "Unknown"
	TEXT_CHOOSE = _("Images from %s" % NAMEBOOT)
else:
	IMAGLISTEPATH = ""  # No Directory of image
	ExternalImages = False
####


class SelectionScreen(Screen, ConfigListScreen):

	def __init__(self, session):
		Screen.__init__(self, session)
		self.skin = SKIN_SelectionScreen
		ConfigListScreen.__init__(self, [], session=session)
		self.session = session
		self.setup_title = _("Select your choose")
		self.setTitle(self.setup_title)

		# Load pixmaps for checkboxes
		sz_w = getDesktop(0).size().width()
		if sz_w == 1280 :
			self.empty_box = LoadPixmap(resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe/buttons/checkbox_empty.png'))
			self.checked_box = LoadPixmap(resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe/buttons/checkbox_checked.png'))
		else:
			self.empty_box = LoadPixmap(resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe/buttons/checkbox_empty2.png'))
			self.checked_box = LoadPixmap(resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe/buttons/checkbox_checked2.png'))

		# Initialize selection states
		self.selection_states = {
			"Menu": False,
			"Channellist": False,
			"Extensions": False
		}

		# Get current config value and update selection states
		self.current_value = config.backupflashe.showplugin.value
		if self.current_value:
			selected_items = self.current_value.split(',')
			for item in selected_items:
				if item in self.selection_states:
					self.selection_states[item] = True

		# Create list of options with their checkbox states
		self.list = []

		# Set up the list component
		self["list"] = List(self.list)

		# Now update the list
		self.updateList()

		# Set up labels
		self["key_green"] = Label(_("Save"))
		self["key_red"] = Label(_("Cancel"))

		# Set up actions
		self["actions"] = ActionMap(["WizardActions", "ColorActions", "MenuActions"], {
			"ok": self.select_option,
			"cancel": self.close,
			"back": self.close,
			"green": self.save
		}, -2)  # Higher priority to ensure OK is captured (DreamOS images need it)

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(self.setup_title)

	def updateList(self):
		# Store the current index before updating the list
		current_index = self["list"].getIndex() or 0
		self.list = []
		choices = [
			("Menu", _("Menu")),
			("Channellist", _("Channellist")),
			("Extensions", _("Extensions"))
		]

		for key, text in choices:
			pixmap = self.checked_box if self.selection_states[key] else self.empty_box
			self.list.append((text, pixmap, key))

		self["list"].setList(self.list)
		# Restore the previous index, ensuring it's within bounds
		if current_index < len(self.list):
			self["list"].setIndex(current_index)
		else:
			self["list"].setIndex(0)  # Fallback to first item if index is out of range

	def select_option(self):
		current = self["list"].getCurrent()
		if current:
			key = current[2]
			self.selection_states[key] = not self.selection_states[key]
			self.updateList()

	def save(self):
		# Save all selected options as comma-separated string
		selected_options = [key for key, state in self.selection_states.items() if state]
		new_value = ','.join(selected_options)
		config.backupflashe.showplugin.value = new_value
		config.backupflashe.showplugin.save()

		if self.current_value != new_value:
			self.session.openWithCallback(self.restart, MessageBox, _("You need to restart GUI\nDo you want to do it now ?!"))
		else:
			self.close(True)

	def restart(self,answer=None):
		if answer:
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close(True)


class full_main(Screen, ConfigListScreen):

	def __init__(self, session):
		global rootfs
		Screen.__init__(self, session)
		self.list = []
		ConfigListScreen.__init__(self, self.list, on_change=self.changedEntry)
		self.onChangedEntry = []
		self.skin = SKIN_full_main
		#self["key_green"] = Label(_("Flash Image"))
		self["key_green"] = Label(_("Convert Image"))
		self["key_yellow"] = Label(_("Flash online"))
		self["key_blue"] = Label(_("Backup Image"))
		self["key_red"] = Label(_("Recovery Mode"))
		self["lab1"] = Label("Detecting mounted devices")
		self["key_green"].hide()
		self["key_blue"].hide()
		self["key_yellow"].hide()
		self["help"] = StaticText()
		self["actions"] = ActionMap(["WizardActions", "ColorActions", "MenuActions"], {
			#"green": self.doFlash,
			"green": self.convertimage,
			"blue": self.BackUpListSelect,
			"yellow": self.flashOnline,
			"menu": self.showMenuoptions,
			"red": self.red,
			"back": self.close,
		})
		self.deviceok = True
		self.new_version = Ver
		self.timer = eTimer()
		try:
			self.timer.callback.append(self.updateList)
		except:
			self.timer_conn = self.timer.timeout.connect(self.updateList)
		# if config.backupflashe.cleanba.value:
		#     if fileExists(BAINIT):
		#          if fileExists(BRANDOS):
		#               os.system('rm -f /sbin/init')
		#               os.system('ln -s /etc/alternatives/init /sbin/init')
		#               os.system('rm -f /etc/alternatives/init')
		#               os.system('ln -s /lib/systemd/systemd /etc/alternatives/init')
		#          else:
		#               os.system('rm -f /sbin/init')
		#               os.system('ln -s init.sysvinit /sbin/init')
		self.timer.start(6, 1)
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		if config.backupflashe.update.value:
			self.checkupdates()
		self.setTitle("Backup And Flash by RAED - V " + Ver)
		missing = []
		if not XZ_:
			missing.append("xz")
		if not PIGZ_:
			missing.append("pigz")
		if not ZIP_:
			missing.append("p7zip or 7zip")
		if not WGET_:
			missing.append("wget")
		if missing:
			self.msg_timer = eTimer()
			try:
				self.msg_timer.callback.append(self.showMissingPackages)
			except:
				self.msg_timer_conn = self.msg_timer.timeout.connect(self.showMissingPackages)
			self.msg_timer.start(100, True)

		self["config"].onSelectionChanged.append(self.updateHelp)

	def showMissingPackages(self):
		missing = []
		if not XZ_:
			logdata("Missing packages", "xz")
			missing.append("xz")
		if not PIGZ_:
			logdata("Missing packages", "pigz")
			missing.append("pigz")
		if not ZIP_:
			logdata("Missing packages", "p7zip or 7zip")
			missing.append("p7zip or 7zip")
		if not WGET_:
			logdata("Missing packages", "wget")
			missing.append("wget")
		if missing:
			message = "These packages are not installed:\n\n" + "\n".join("- %s" % pkg for pkg in missing)
		else:
			message = "All required packages are installed."
		message += "\n\nBackup or Convert or Download images may not work.\n\nLook in '/tmp/backupflash.log' for missing packages."
		self.session.open(MessageBox, message, MessageBox.TYPE_INFO, timeout=8)

	def updateList(self):
		dellog()
		if len(mounted_devices) > 0:
			self.deviceok = True
			self["lab1"].setText(_("# Press Menu ..\nTo open option of show Plugin in any where you like"))
			#self["lab1"].setText(_("Do (Full Backup) or (Convert) or (Download) Images or (Go to Recovery Mode)"))
			self["key_green"].show()
			self["key_blue"].show()
			self["key_yellow"].show()
			config.backupflashe.device_path = ConfigSelection(
				choices=mounted_devices)
			self.createSetup()
		else:
			self["lab1"].setText(_("Sorry no device mounted found.\nPlease check your media in devices manager."))
			self["key_green"].hide()
			self["key_blue"].hide()
			self["key_yellow"].hide()
			self.deviceok = False

	def createSetup(self):
		self.list = []
		self.list.append(getConfigListEntry(('Path to store Full Backup'), config.backupflashe.device_path, _(
			"This option to set the path of Backup/Flash directory")))
		self.list.append(getConfigListEntry(('Enable/Disable online update'), config.backupflashe.update, _(
			"This option to Enable or Disable check of online update")))
		self.list.append(getConfigListEntry(('Select Format to Compress BackUp'), config.backupflashe.image_format, _(
			"This option to select the type of compress option")))
		if config.backupflashe.image_format.value == "xz":
			self.list.append(getConfigListEntry(("xz")+" "+_("Compression")+" "+_("(1-6)"), config.backupflashe.xzcompression, _(
				"This option to set stringe value of Compress image (The higher the value, the longer the operation time, but the smaller the backup size)")))
		#elif config.backupflashe.image_format.value == "bz2":
		#	self.list.append(getConfigListEntry(("bz2")+" "+_("Compression")+" "+_("(1-6)"), config.backupflashe.bz2compression, _(
		#		"This option to set stringe value of Compress image (The higher the value, the longer the operation time, but the smaller the backup size)")))
		else:
			pass
		if config.backupflashe.image_format.value == "bz2":
			self.list.append(getConfigListEntry(('Compression image as Zip'), config.backupflashe.Zipcompression, _(
				"This option to Compression image inside Zip file")))
		self.list.append(getConfigListEntry(('Enable shutdown box after backup'), config.backupflashe.shutdown, _(
			"This option to Enable or Disable Shutdown Box After Finished Backup")))
		# if (os.path.exists("/.bainfo") or os.path.exists("/.lfinfo") or cmd.find(rootfs) == -1):
		#    self.list.append(getConfigListEntry(('Allow to flash image from External image'), config.backupflashe.flashAllow, _("Warning: the process will delete the image if you are on an external flash\n(it is not recommended to Enable it)\nSafy way to Flash new image Please go to internal flash")))
		self.list.append(getConfigListEntry(('Clean image from BA symlink before backup'), config.backupflashe.cleanba, _(
			"This option for remove BarryAllen symlink from image Before Start Backup")))
		self['config'].list = self.list
		self['config'].l.setList(self.list)

	def updateHelp(self):
		cur = self["config"].getCurrent()
		if cur:
			self["help"].text = cur[2]

	def changedEntry(self):
		self.createSetup()
		self.configsSave()

	def doFlash(self):
		self.session.open(
			MessageBox, "Sorry Flash feature not working.\nPlease Flash the image from recovery mode more safe more stable.", MessageBox.TYPE_ERROR, timeout=8)

	def BackUpListSelect(self):
		list = []
		list.append(("Backup Current Image", "Do Backup From Current Flash image"))
		if ExternalImages == True:
			list.append(("Backup External Image", "Do Backup From External Flash image"))
		self.session.openWithCallback(self.BackUpSelect, ChoiceBox, _('Select Backup Option'), list)

	def BackUpSelect(self, select):
		if select:
			if select[0] == "Backup External Image":  # BackUp External Flash
				self.session.openWithCallback(self.askForTarget, ChoiceBox, _("%s") % TEXT_CHOOSE, self.imagelistbackup())
			else:  # BackUp Internal Flash
				self.nameBackUp()
		else:
			self.close()

# BackUp Internal Flash
	def nameBackUp(self):
		imagename = '%s-%s-%s' % (getname, boxtype, DATETIME)
		self.session.openWithCallback(self.doBackUpInt, VirtualKeyBoard, title=_(
			"Please Enter Name For Backup Image"), text="%s" % imagename)

	def doBackUpInt(self, target):
		if target == None:
			return
		else:
			self.configsSave()
			if self.deviceok:
				try:
					image_name = target
					device_path = self['config'].list[0][1].getText()
					image_compression_value = imagecompressionvalue
					self.session.open(doBackUpInternal, image_name, device_path, image_compression_value)
				except:
					trace_error()
					pass

# BackUp External Flash

	def imagelistbackup(self):
		imageslist = []
		for line in os_listdir(IMAGLISTEPATH):
			if line.startswith("."):
				continue
			imageslist.append((line, line))
		imageslist.sort()
		return imageslist

	def askForTarget(self, source):
		if source == None:
			return
		else:
			self.configsSave()
			self.getname = source[1].rstrip()
			self.image_path = IMAGLISTEPATH + "/" + self.getname
			self.imagename = '%s-%s-%s' % (self.getname, boxtype, DATETIME)
			self.device_path = self['config'].list[0][1].getText()
			self.image_formats = self['config'].list[1][1].getText()
			self.image_compression_value = self['config'].list[2][1].getText()
			self.session.openWithCallback(self.doBackUpExt, VirtualKeyBoard, title=_(
				"Please Enter Name For Backup Image"), text="%s" % self.imagename)

	def doBackUpExt(self, target):
		if target == None:
			return
		else:
			if self.deviceok:
				try:
					image_name = target
					image_path = self.image_path
					device_path = self.device_path
					image_compression_value = self.image_compression_value
					self.session.open(doBackUpExternal, image_name, image_path,device_path, image_compression_value)
				except:
					trace_error()
					pass
#####


	def convertimage(self,):
		self.session.openWithCallback(self.askForconvert, ChoiceBox, _("Choose an image to convert to zip compress"), self.imagelist())

	def imagelist(self):
		device_path = self['config'].list[0][1].getText()
		imageslist = []
		for line in os_listdir(device_path):
			if line.endswith(".xz"):
				imageslist.append((line, line))
				imageslist.sort()
		return imageslist

	def askForconvert(self, source):
		if source == None:
			return
		else:
			self.configsSave()
			getname = source[1].rstrip()
			device_path = self['config'].list[0][1].getText()
			self.session.open(doConvert, device_path, getname)

	def red(self,):
		self.session.openWithCallback(self.GoRecovery, MessageBox, _(
			'Really shutdown now (To Go to Recovery Mode) ?!!'), MessageBox.TYPE_YESNO)

	def GoRecovery(self, answer=False):
		if answer:
			b = open("/proc/stb/fp/boot_mode", "w")
			b.write("rescue")
			b.close()
			quitMainloop(2)
		else:
			self.close()

	def flashOnline(self,):
		configfile.save()
		from Plugins.Extensions.backupflashe.tools.flashonline import teamsScreen
		device_path = self['config'].list[0][1].getText()
		# logdata('selected device path', device_path)
		self.session.open(teamsScreen, device_path)

	def configsSave(self):
		for x in self['config'].list:
			x[1].save()
		configfile.save()

	def showMenuoptions(self):
		self.session.open(SelectionScreen)
		#choices = []
		#self.list = []
		#choices.append(("Install/Reinstgall backupflash version %s" % self.new_version, "Install"))
		#self.session.openWithCallback(self.choicesback, ChoiceBox, _('select task'), choices)

	def choicesback(self, select):
		if select:
			if select[1] == "Install":
				self.install(True)

	def checkupdates(self):
		try:
			from twisted.web.client import getPage, error
			url = b'https://raw.githubusercontent.com/fairbird/BackUpFlash/main/installer.sh'
			getPage(url, timeout=10).addCallback(
				self.parseData).addErrback(self.errBack)
		except Exception as error:
			trace_error()

	def errBack(self, error=None):
		logdata("errBack-error", error)

	def parseData(self, data):
		if PY3:
			data = data.decode("utf-8")
		else:
			data = data.encode("utf-8")
		if data:
			lines = data.split("\n")
			for line in lines:
				# line=str(line)
				if line.startswith("version"):
					self.new_version = line.split("=")[1]
					# break #if enabled the for loop will exit before reading description line
				if line.startswith("description"):
					self.new_description = line.split("=")[1]
					break
		if float(Ver) >= float(self.new_version):
			logdata("Updates", "No new version available")
		else:
			new_version = self.new_version
			new_description = self.new_description
			self.session.openWithCallback(self.install, MessageBox, _(
				'New version %s is available.\n\n%s.\n\nDo want ot install now.' % (new_version, new_description)), MessageBox.TYPE_YESNO)

	def install(self, answer=False):
		try:
			if answer:
				cmdlist = []
				cmd = 'wget https://raw.githubusercontent.com/fairbird/BackUpFlash/main/installer.sh -O - | /bin/sh'
				cmdlist.append(cmd)
				self.session.open(Console, title='Installing last update, enigma will be started after install',
								  cmdlist=cmdlist, finishedCallback=self.myCallback, closeOnSuccess=False)
		except:
			trace_error()

	def myCallback(self, result):
		return

def main_menu(menuid, **kwargs):
	if menuid == "mainmenu" and config.backupflashe.showplugin.value:
		return [(_("BackupFlash"), main, "BackupFlash", 45)]
	else:
		return []

def main(session, *args, **kwargs):
	# mounted_devices = getmDevices()
	# if len(mounted_devices) > 0:
	session.open(full_main)
	# else:
	#        session.open(MessageBox, "Sorry no device mounted found.\nPlease check your media in devices manager.", MessageBox.TYPE_ERROR,timeout=8)


description = _("Backup And Flash Images")

def Plugins(**kwargs):
	result = [
		PluginDescriptor(
			name=_("BackupFlash"),
			description=description,
			icon="plugin.png",
			where=PluginDescriptor.WHERE_PLUGINMENU,
			fnc=main
		),
	]

	show = config.backupflashe.showplugin.value
	selected_options = show.split(",") if show else []

	extDescriptor = PluginDescriptor(
		name=_("Backup And Flash Images [BackupFlash]"),
		description=description,
		where=PluginDescriptor.WHERE_EXTENSIONSMENU,
		fnc=main
	)

	menulist = PluginDescriptor(
		name=_("BackupFlash"),
		description=description,
		where=PluginDescriptor.WHERE_MENU,
		fnc=main_menu
	)

	contextlist = PluginDescriptor(
		name=_("Backup And Flash Images [BackupFlash]"),
		description=description,
		where=PluginDescriptor.WHERE_CHANNEL_CONTEXT_MENU,
		fnc=main
	)

	if "Menu" in selected_options:
		result.append(menulist)
	if "Extensions" in selected_options:
		result.append(extDescriptor)
	if "Channellist" in selected_options:
		result.append(contextlist)
		if fileExists(BRANDOS):
			result.append(
				PluginDescriptor(
					name=_("Backup And Flash Images [BackupFlash]"),
					description=description,
					where=PluginDescriptor.WHERE_CHANNEL_SELECTION_RED,
					fnc=main
				)
			)
	return result
