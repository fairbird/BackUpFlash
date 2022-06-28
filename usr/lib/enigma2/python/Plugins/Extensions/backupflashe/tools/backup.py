#!/usr/bin/python
# -*- coding: utf-8 -*-
# RAED & mfaraj57 &  (c) 2018
# Code RAED & mfaraj57

# python3
from __future__ import print_function

from Components.ActionMap import ActionMap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Tools.Directories import fileExists
from Components.config import config
from enigma import eTimer
import datetime
import os

from .Console import Console
from .progress import ProgressScreen 
from .bftools import logdata, getboxtype, dellog, getimage_name, copylog

BRANDOS = '/var/lib/dpkg/status' ## DreamOS
BAINIT = '/sbin/bainit'

class doBackUp(Screen):
    def __init__(self, session, device_path = None, image_formats = None, image_compression_value = 0):
        Screen.__init__(self, session)
        self.list = []
        self['key_red'] = Label(_('Cancel'))
        self['key_green'] = Label(_('Backup'))
        self['lab1'] = Label('')
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'],
        	{
        		'red': self.close,
         		'green': self.doBackUp,
         		'back': self.close
         	})
        self.device_path = device_path
        self.image_formats = image_formats
        self.image_compression_value = image_compression_value
        self.deviceok = True
        self.timer = eTimer()
        try:
            self.timer.callback.append(self.doBackUp)
        except:
            self.timer_conn = self.timer.timeout.connect(self.doBackUp)
        self.timer.start(6, 1)

    def doBackUp(self):
        if fileExists("/tmp/.cancelBackup"):
             os.system("rm -f /tmp/.cancelBackup")
        self.timer.stop()
        cmdlist = []
        boxtype = getboxtype()
        getname = getimage_name()
        LOG = '/tmp/backupflash.scr'
        now = datetime.datetime.now()
        DATETIME = now.strftime('%Y-%m-%d-%H-%M')
        logdata("Backup log","start")
        logdata("Start Time",now.strftime('%H:%M')) ## Print Start time to log file
        if config.backupflashe.cleanba.value:
             if fileExists(BAINIT):
                  if fileExists(BRANDOS):
                       os.system('rm -f /sbin/init')
                       os.system('ln -s /etc/alternatives/init /sbin/init')
                       os.system('rm -f /etc/alternatives/init')
                       os.system('ln -s /lib/systemd/systemd /etc/alternatives/init')
                  else:
                       os.system('rm -f /sbin/init')
                       os.system('ln -s init.sysvinit /sbin/init')
        if os.path.exists("/etc/init.d/openvpn"):
            os.system('/etc/init.d/openvpn stop >> >> %s' % LOG)
        if self.image_formats == 'xz':
            IMAGENAME = '%s-%s-%s.tar.xz ' % (getname, boxtype, DATETIME)
            IMAGENAME1 = os.path.join(self.device_path, IMAGENAME)
            self.IMAGENAME1=IMAGENAME1
            compression_value=self.image_compression_value
            if fileExists(BRANDOS):
               COMMANDTAR = 'tar --exclude=smg.sock --exclude msg.sock -cf - -C /tmp/root . | xz -%s -T 0 -c - > %s' % (compression_value, IMAGENAME1)
            else:
               COMMANDTAR = 'tar -cf - -C /tmp/root . | xz -%s -T 0 -c - > %s' % (compression_value, IMAGENAME1)
        else:
            IMAGENAME = '%s-%s-%s.tar.gz ' % (getname, boxtype, DATETIME)
            IMAGENAME1 = os.path.join(self.device_path, IMAGENAME)
            compression_value=self.image_compression_value
            if fileExists(BRANDOS):
               COMMANDTAR = 'tar -cf - --exclude=smg.sock --exclude msg.sock -C /tmp/root . | pigz -%s  > %s' % (compression_value, IMAGENAME1)
            else:
               COMMANDTAR = 'tar -cf - -C /tmp/root . | pigz -%s  > %s' % (compression_value, IMAGENAME1)
        IMAGENAME1 = os.path.join(self.device_path, IMAGENAME)
        self.IMAGENAME1=IMAGENAME1
        if self.device_path:
            mytitle = _('Backup image')
            cmdlist.append('exec > /tmp/backupflash.scr')
            #cmdlist.append('echo "Start make Full Backup ... Wait 1 to 2 (minutes) To Finish It\n"')
            cmdlist.append('echo "Backup (%s) on [%s]\n\n\n" ' % (IMAGENAME, self.device_path))
            cmdlist.append('umount /tmp/root >> %s 2>&1' % LOG)
            cmdlist.append('rmdir /tmp/root >> %s 2>&1' % LOG)
            cmdlist.append('mkdir /tmp/root >> %s 2>&1' % LOG)
            cmdlist.append('mount -o bind / /tmp/root >> %s 2>&1' % LOG)
            cmdlist.append(COMMANDTAR)
            cmdlist.append('umount /tmp/root >> %s' % LOG)
            cmdlist.append('rmdir /tmp/root >> %s' % LOG)
            cmdlist.append('chmod 777 %s >> %s' % (IMAGENAME1, LOG))
            if os.path.exists("/etc/init.d/openvpn"):
               cmdlist.append('/etc/init.d/openvpn start >> %s' % LOG)
            for item in cmdlist:
                logdata("command",str(item))
            self.session.openWithCallback(self.cleanba, ProgressScreen, title=mytitle, cmdlist=cmdlist, imagePath=self.IMAGENAME1)
        else:
            self.session.open(MessageBox, _('Sorry no device found to store backup.\nPlease check your media in devices manager.'), MessageBox.TYPE_INFO)
        logdata("Finished Time",now.strftime('%H:%M')) ## Print Finished time to log file

    def cleanba(self):
        if config.backupflashe.cleanba.value:
             if fileExists(BAINIT):
                  if fileExists(BRANDOS):
                       os.system('rm -f /sbin/init')
                       os.system('ln -s bainit /sbin/init')
                       os.system('rm -f /etc/alternatives/init')
                       os.system('ln -s /sbin/bainit /etc/alternatives/init')
                  else:
                       os.system('rm -f /sbin/init')
                       os.system('ln -s bainit /sbin/init')
             self.dofinish()
        else:
             self.dofinish()

    def dofinish(self):
    	if fileExists("/tmp/.cancelBackup"):
             os.system("rm -f /tmp/.cancelBackup")
             self.close()
    	else:
             boxtype = getboxtype()
             getname = getimage_name()
             now = datetime.datetime.now()
             DATETIME = now.strftime('%Y-%m-%d-%H-%M')
             if self.image_formats == 'xz':
                  IMAGENAME = '%s-%s-%s.tar.xz ' % (getname, boxtype, DATETIME)
             else:
                  IMAGENAME = '%s-%s-%s.tar.gz ' % (getname, boxtype, DATETIME)
             self.session.open(MessageBox, _('(%s)\non\n[%s]\n\nfinished. Press (Exit) or (Ok) Button.' % (IMAGENAME, self.device_path)), MessageBox.TYPE_INFO)
             self.close()
