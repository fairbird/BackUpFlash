#!/usr/bin/python
# -*- coding: utf-8 -*-
# RAED & mfaraj57 &  (c) 2018
# Code RAED & mfaraj57
# Thank you (gutemine) for swaproot tools
# Update 15-11-2018 Add xz option compress
# Update 16-11-2018 Add Value of option compress
# Update 16-11-2018 Update swaproot to 2.1 Thank you (gutemine)
# Update 17-11-2018 Add download images option
# Update 28-11-2018 Update swaproot to 2.2-r8 Thank you (gutemine)
# Update 07-10-2019 Update swaproot to 2.4-r19 Thank you (gutemine)
# Update 07-10-2019 Add support DreamOne
# Update 30-10-2020 Add support Python3
# Update 29-03-2021 Add support DreamTwo 
# Update 29-03-2021 Update swaproot to 2.8-r1 Thank you (gutemine)
# Update 29-03-2021 Add New options
# Update 29-03-2021 Go back to swaproot 2.8-r1 It more better to flash image from External flash
# Update 08-09-2021 Add Openvision images url download

# python3
from __future__ import print_function
from Plugins.Extensions.backupflashe.tools.compat import PY3

from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Components.MenuList import MenuList
from Components.Sources.StaticText import StaticText
from Tools.Directories import fileExists
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, ConfigSubsection, config, ConfigYesNo, ConfigSelection, NoSave, configfile
from enigma import eTimer, quitMainloop
import datetime
import os

from Plugins.Extensions.backupflashe.tools.skin import *
from Plugins.Extensions.backupflashe.tools.Console import Console
from Plugins.Extensions.backupflashe.tools.bftools import logdata, dellog, copylog, getboxtype, getmDevices, trace_error, getversioninfo

BRANDOS = '/var/lib/dpkg/status' ## DreamOS
BAINIT = '/sbin/bainit'
BAINFO = '/.bainfo'

Ver,lastbuild,enigmaos = getversioninfo()

config.backupflashe = ConfigSubsection()
config.backupflashe.update = ConfigYesNo(default=True)

config.backupflashe.cleanba = ConfigYesNo(default=False)
config.backupflashe.flashAllow = ConfigYesNo(default=False)

image_formats = [('xz','xz'), ('gz','gz')]
config.backupflashe.image_format = ConfigSelection(default = "xz", choices = image_formats)
xz_options = []
xz_options.append(( "1","1" ))
xz_options.append(( "2","2" ))
xz_options.append(( "3","3" ))       
xz_options.append(( "4","4" ))
xz_options.append(( "5","5" ))                                              
xz_options.append(( "6","6" ))
config.backupflashe.xzcompression = ConfigSelection(default = "1", choices = xz_options)
config.backupflashe.gzcompression = ConfigSelection(default = "3", choices = xz_options)

k=open("/proc/cmdline","r")
cmd=k.read()
k.close()
boxtype =getboxtype()
if boxtype == "dm520":
        if cmd.find("root=/dev/sda1") is not -1:
                rootfs="root=/dev/sda1"
        else:
                rootfs="root=ubi0:dreambox-rootfs"
else:
        rootfs="root=/dev/mmcblk0"

class full_main(Screen, ConfigListScreen):
    def __init__(self, session):
        global rootfs
        Screen.__init__(self, session)
        self.list = []
        ConfigListScreen.__init__(self, self.list,on_change = self.changedEntry)
        self.onChangedEntry = []
        self.skin = SKIN_full_main
        self['key_green'] = Label(_('Flash Image'))
        self['key_yellow'] = Label(_('Flash online'))
        self['key_blue'] = Label(_('Backup Image'))
        self['key_red'] = Label(_('Recovery Mode'))
        self['lab1'] = Label('Detecting mounted devices')
        self['key_green'].hide()
        self['key_blue'].hide()
        self['key_yellow'].hide()
        self["help"] = StaticText()
        self['actions'] = ActionMap(['WizardActions', 'ColorActions','MenuActions'], {'green': self.doFlash,
         'blue': self.doBackUp,
         'yellow': self.flashOnline,
         'menu' :self.showMenuoptions,                                                              
         'red': self.red,
         'back': self.close})
        self.deviceok = True
        self.new_version=Ver
        self.timer = eTimer()
        try:
            self.timer.callback.append(self.updateList)
        except:
            self.timer_conn = self.timer.timeout.connect(self.updateList)
        #if config.backupflashe.cleanba.value:
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
        self.setTitle("Backup And Flash by RAED & mfaraj57 - V" + Ver)
        self["config"].onSelectionChanged.append(self.updateHelp)

    def updateList(self):
        dellog()
        self.checkupdates()
        mounted_devices = getmDevices()
        #logdata("mounted devices",mounted_devices)
        if len(mounted_devices) > 0:
            self.deviceok = True
            self['lab1'].setText(_('Do Flash New Image or Full Backup Image.'))
            self['key_green'].show()
            self['key_blue'].show()
            self['key_yellow'].show()
            config.backupflashe.device_path = ConfigSelection(choices = mounted_devices)
            self.createSetup()
        else:
            self['lab1'].setText(_('Sorry no device mounted found.\nPlease check your media in devices manager.'))
            self['key_green'].hide()
            self['key_blue'].hide()
            self['key_yellow'].hide()
            self.deviceok = False

    def createSetup(self):
            self.list = []
            self.list.append(getConfigListEntry(('Path to store Full Backup'), config.backupflashe.device_path, _("This option to set the path of Backup/Flash directory")))
            self.list.append(getConfigListEntry(('Select Format to Compress BackUp'), config.backupflashe.image_format, _("This option to select the type of compress option")))
            if config.backupflashe.image_format.value=="xz":
                    self.list.append(getConfigListEntry(("xz")+" "+_("Compression")+" "+_("(1-6)"), config.backupflashe.xzcompression, _("This option to set stringe value of Compress image")))
            elif config.backupflashe.image_format.value=="gz":
                    self.list.append(getConfigListEntry(("gz")+" "+_("Compression")+" "+_("(1-6)"), config.backupflashe.gzcompression, _("This option to set stringe value of Compress image")))
            else:
                    pass
            if (os.path.exists("/.bainfo") or os.path.exists("/.lfinfo") or cmd.find(rootfs) is -1):
                self.list.append(getConfigListEntry(('Allow To Flash image from External image'), config.backupflashe.flashAllow, _("Warning: the process will delete the image if you are on an external flash\n(it is not recommended to Enable it)\nSafy way to Flash new image Please go to internal flash")))
            self.list.append(getConfigListEntry(('Clean image from BA symlink Before Backup'), config.backupflashe.cleanba, _("This option for remove BarryAllen symlink from image Before Start Backup")))
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
        if not config.backupflashe.flashAllow.value and (os.path.exists("/.bainfo") or os.path.exists("/.lfinfo") or cmd.find(rootfs) is -1):
                self.session.open(MessageBox, "You Disable To flash new image from External image.\nSo Flashing works only in Flash image", MessageBox.TYPE_ERROR)
        #if os.path.exists("/.bainfo"):
                #self.session.open(MessageBox, "Sorry, Flashing works only in Flash image", MessageBox.TYPE_ERROR)
        #elif os.path.exists("/.lfinfo"):
        #        self.session.open(MessageBox, "Sorry, Flashing works only in Flash image", MessageBox.TYPE_ERROR)
        #elif cmd.find(rootfs) is -1:
        #        self.session.open(MessageBox, "Sorry, Flashing works only in Flash image", MessageBox.TYPE_ERROR)
        else:
                self.configsSave()
                if self.deviceok:
                        device_path = self['config'].list[0][1].getText()
                        #logdata('selected device path', device_path)
                        from Plugins.Extensions.backupflashe.tools.flash import doFlash
                        self.session.open(doFlash, device_path)

    def doBackUp(self):
        self.configsSave()
        if self.deviceok:
            try:
                device_path = self['config'].list[0][1].getText()
                image_formats = self['config'].list[1][1].getText()
                image_compression_value = self['config'].list[2][1].getText()
                #logdata('backup started', "started")
                from Plugins.Extensions.backupflashe.tools.backup import doBackUp
                self.session.open(doBackUp, device_path, image_formats, image_compression_value)
            except:
                trace_error()
                pass

    def red(self,):
        self.session.openWithCallback(self.GoRecovery, MessageBox, _('Really shutdown now (To Go to Recovery Mode) ?!!'), MessageBox.TYPE_YESNO)

    def GoRecovery(self, answer=False):
        if answer:
            	b=open("/proc/stb/fp/boot_mode","w")
            	b.write("rescue")
            	b.close()
            	quitMainloop(2)
        else:
            	self.close()

    def flashOnline(self,):
        configfile.save()
        from Plugins.Extensions.backupflashe.tools.flashonline import teamsScreen
        device_path = self['config'].list[0][1].getText()
        #logdata('selected device path', device_path)
        self.session.open(teamsScreen,device_path)

    def configsSave(self):
        for x in self['config'].list:
            x[1].save()
        configfile.save()

    def showMenuoptions(self):
        choices=[]
        self.list = []
        EnablecheckUpdate = config.backupflashe.update.value
        choices.append(("Install backupflash version %s" %self.new_version,"Install"))
        if EnablecheckUpdate == False:
                choices.append(("Press Ok to [Enable checking for Online Update]","enablecheckUpdate"))
        else:
                choices.append(("Press Ok to [Disable checking for Online Update]","disablecheckUpdate")) 
        self.session.openWithCallback(self.choicesback, ChoiceBox, _('select task'),choices)

    def choicesback(self, select):
        if select:
                if select[1] == "Install":
                         self.install(True)
                elif select[1] == "enablecheckUpdate":
                         config.backupflashe.update.value = True
                         config.backupflashe.update.save()
                         configfile.save()
                elif select[1] == "disablecheckUpdate":
                         config.backupflashe.update.value = False
                         config.backupflashe.update.save()
                         configfile.save()
 
    def checkupdates(self):
        try:
                from twisted.web.client import getPage, error
                url = b'https://raw.githubusercontent.com/fairbird/BackUpFlash/main/installer.sh'
                getPage(url,timeout=10).addCallback(self.parseData).addErrback(self.errBack)
        except Exception as error:
                trace_error()

    def errBack(self,error=None):
        logdata("errBack-error",error)

    def parseData(self, data):
        if PY3:
                data = data.decode("utf-8")
        else:
                data = data.encode("utf-8")
        if data:
                lines = data.split("\n")
                for line in lines:
                       #line=str(line)
                       if line.startswith("version"):
                          self.new_version = line.split("=")[1]
                          #break #if enabled the for loop will exit before reading description line
                       if line.startswith("description"):
                          self.new_description = line.split("=")[1]
                          break
        if float(Ver) == float(self.new_version) or float(Ver)>float(self.new_version):
                logdata("Updates","No new version available")
        else :
                new_version = self.new_version
                new_description = self.new_description
                self.session.openWithCallback(self.install, MessageBox, _('New version %s is available.\n\n%s.\n\nDo want ot install now.' % (new_version, new_description)), MessageBox.TYPE_YESNO)

    def install(self, answer=False):
        try:
                if answer:
                           cmdlist = []
                           cmd='wget https://raw.githubusercontent.com/fairbird/BackUpFlash/main/installer.sh -O - | /bin/sh'
                           cmdlist.append(cmd)
                           self.session.open(Console, title='Installing last update, enigma will be started after install', cmdlist=cmdlist, finishedCallback=self.myCallback, closeOnSuccess=False)
        except:
                trace_error()
        
    def myCallback(self,result):
         return

def main(session, **kwargs):
        #mounted_devices = getmDevices()
        #if len(mounted_devices) > 0:
                session.open(full_main)
        #else:
        #        session.open(MessageBox, "Sorry no device mounted found.\nPlease check your media in devices manager.", MessageBox.TYPE_ERROR,timeout=8)

def Plugins(**kwargs):
        result = [
                PluginDescriptor(
                        name=_("BackupFlash"),
                        description = _("Backup And Flash Images"),
                        where = PluginDescriptor.WHERE_PLUGINMENU,
                        icon = 'plugin.png',
                        fnc = main
                ),
        ]
        return result
