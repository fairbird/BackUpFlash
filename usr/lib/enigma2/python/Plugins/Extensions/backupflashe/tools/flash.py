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
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS
from enigma import eTimer
import datetime
import os

from .progress import ProgressScreen
from .skin import *
from .bftools import logdata, getboxtype, dellog, getversioninfo, copylog

Ver, lastbuild, enigmaos = getversioninfo()

logfile="/tmp/backupflash.log"
backupflash_script="/tmp/backupflash.sh"
PLUGINROOT = '/usr/lib/enigma2/python/Plugins/Extensions/backupflashe'
PLUGINBACKUP = '/usr/lib/enigma2/python/Plugins/Extensions/dBackup'
#PLUGINROOT = resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe') ## Do not use it (some image still did not work correctly with lib64)
#PLUGINBACKUP = resolveFilename(SCOPE_PLUGINS, 'Extensions/dBackup') ## Do not use it (some image still did not work correctly with lib64)

def flashScript(IMAGENAME,device_path):
        boxtype = getboxtype()
        IMAGEPATH =os.path.join(device_path,IMAGENAME)
        cmdlist = []
        tarimage = ''
        os.system('rm -rf %s/tmp' % device_path)
        os.system('mkdir -p %s/tmp' % device_path)
        command ="" # 'echo Box will auto reboot after flash finished\n\n'
        command += 'echo extracting image,please wait...\n\n'
        command += "#!/bin/sh -x\n"
        command +="set -e\n"
        if IMAGENAME.endswith('.tar.gz'):
            tarimage = '%s/tmp/rootfs.tar' % device_path
            command += "sync; sync; sync; echo 3 > /proc/sys/vm/drop_caches\n"
            command += 'pigz -d -f -c "%s" > "%s"\n' % (IMAGEPATH, tarimage)
        elif IMAGENAME.endswith('.tar.xz'):
            tarimage = '%s/tmp/rootfs.tar' % device_path
            command += "sync; sync; sync; echo 3 > /proc/sys/vm/drop_caches\n"
            command += 'xz -d -c "%s" > "%s"\n' % (IMAGEPATH, tarimage)
            logdata('commandxz', command)
        elif IMAGENAME.endswith('.tar.bz2'):
            tarimage = '%s/tmp/rootfs.tar' % device_path
            command += "sync; sync; sync; echo 3 > /proc/sys/vm/drop_caches\n"
            command += 'bunzip2 -c -f "%s" > "%s"\n' % (IMAGEPATH, tarimage)
        elif IMAGENAME.endswith('.zip'):
                 command += 'echo unzipping image,please wait...\n\n'
                 command += "unzip \"%s\" -d %s/tmp\n" % (IMAGEPATH, device_path)
                 bz2image = "%s/tmp/%s/rootfs.tar.bz2" % (device_path,boxtype)
                 tarimage = "%s/tmp/rootfs.tar" % device_path
                 command += "if [ -e %s/tmp/%s ]; then\n" % (device_path,boxtype)
                 command += 'sync; sync; sync; echo 3 > /proc/sys/vm/drop_caches\n'
                 command += 'bunzip2 -c -f \"%s\" > \"%s\"\n' % (bz2image,tarimage)
                 command += 'else\n'
                 sp=[]
                 sp=IMAGEPATH.split("/")
                 ll=len(sp)
                 flashimagename=sp[ll-1]
                 command += 'xz -d -c \"%s/tmp/%s\" > \"%s\"\n' % (device_path, flashimagename.replace('.zip','.rootfs.tar.xz'),tarimage)
                 command += "fi\n"
        command += 'set +e\n'
        #command += 'mv %s %s\n' % (PLUGINROOT, PLUGINBACKUP)
        command += swaproot(device_path,tarimage)+'\n'         
        command += 'exit 0\n'
        logdata('command', command)
        sfile=open(backupflash_script,"w")
        sfile.write(command)
        sfile.close()
        os.chmod(backupflash_script,755)
        copylog(device_path)
        return command

def swaproot(device_path,tarimage):
            boxtype = getboxtype()
            logdata("boxtype",boxtype)
            os.system('mkdir -p %s' % PLUGINBACKUP)
            if boxtype == "dm900" or boxtype == "dm920":
                os.system('cp -r %s/armhf %s' % (PLUGINROOT, PLUGINBACKUP))
                DBSWAPROOT = '/usr/lib/enigma2/python/Plugins/Extensions/dBackup/armhf'
                JOBSWAPROOT = "/sbin/start-stop-daemon -S -b -n swaproot -x %s/armhf/swaproot %s" % (PLUGINBACKUP,tarimage)
            elif boxtype == "dreamone" or boxtype == "dreamtwo":
                os.system('cp -r %s/arm64 %s' % (PLUGINROOT, PLUGINBACKUP))
                DBSWAPROOT = '/usr/lib/enigma2/python/Plugins/Extensions/dBackup/arm64'
                JOBSWAPROOT = "/sbin/start-stop-daemon -S -b -n swaproot -x %s/arm64/swaproot %s" % (PLUGINBACKUP,tarimage)
            else:
                os.system('cp -r %s/mipsel %s' % (PLUGINROOT, PLUGINBACKUP))
                DBSWAPROOT = '/usr/lib/enigma2/python/Plugins/Extensions/dBackup/mipsel'
                JOBSWAPROOT = "/sbin/start-stop-daemon -S -b -n swaproot -x %s/mipsel/swaproot %s" % (PLUGINBACKUP,tarimage)
            #command = 'mkdir -p %s\n' % DBSWAPROOT
            #command += 'cp %s %s\n' % (SWAPROOT, DBSWAPROOT)
            command = 'chmod 0755 %s\n' %(DBSWAPROOT + '/swaproot')
            command += '%s \n' % JOBSWAPROOT
            return command

class doFlash(Screen):
    def __init__(self, session, device_path = None):
        Screen.__init__(self, session)
        self.skin = SKIN_doFlash
        self.list = []
        self['key_red'] = Label(_('Cancel'))
        self['key_green'] = Label(_('Flash'))
        self['lab1'] = Label('')
        self['list'] = MenuList([])
        self['path'] = Label(device_path)
        self.device_path = device_path
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'red': self.close,
         'green': self.doFlash,
         'back': self.close})
        self['key_green'].hide()
        self.images = []
        self.timer = eTimer()
        try:
            self.timer.callback.append(self.updateList)
        except:
            self.timer_conn = self.timer.timeout.connect(self.updateList)
        self.timer.start(6, 1)

    def layoutFinished(self):
        self.setTitle("Backup And Flash by RAED & mfaraj57   V" + Ver)

    def updateList(self):
        self.timer.stop()
        self.images = self.get_images()
        boxtype =getboxtype()
        print('self.images', self.images)
        if boxtype == "dm900" or boxtype == "dm920":
            SWAPROOT = '/usr/lib/enigma2/python/Plugins/Extensions/backupflashe/armhf/swaproot'
            SWAPROOTDIR = '/usr/lib/enigma2/python/Plugins/Extensions/backupflashe/armhf'
        elif boxtype == "dreamone":
            SWAPROOT = '/usr/lib/enigma2/python/Plugins/Extensions/backupflashe/arm64/swaproot'
            SWAPROOTDIR = '/usr/lib/enigma2/python/Plugins/Extensions/backupflashe/arm64'
        else:
            SWAPROOT = '/usr/lib/enigma2/python/Plugins/Extensions/backupflashe/mipsel/swaproot'
            SWAPROOTDIR = '/usr/lib/enigma2/python/Plugins/Extensions/backupflashe/mipsel'
        if not fileExists(SWAPROOT):
            #self.session.open(MessageBox, _('swaproot Not found it.\nPlease send it to %s' % SWAPROOTDIR), MessageBox.TYPE_INFO)
            self.session.open(MessageBox, _('swaproot Not found it.\nPlease install plugin again'), MessageBox.TYPE_INFO)
            self.close()
        if len(self.images) > 0:
            self['list'].setList(self.images)
            self['key_green'].show()
            self.deviceok = True
            self['lab1'].setText(_('Select image and do flash.'))
        else:
            self['lab1'].setText(_('Sorry no images found to flash.\nPlease put image  in %s.' % self.device_path))
            self['key_green'].hide()
            self.deviceok = False
            return

    def get_images(self):
        images = []
        print('self.device_path', self.device_path)
        if os.path.exists(self.device_path):
            for name in os.listdir(self.device_path):
                if (name.endswith('.tar.gz') or name.endswith('.tar.xz') or name.endswith('.tar.bz2') or name.endswith('.tar') or name.endswith('.zip')) and not name.startswith('enigma2settings') and not name.endswith('enigma2settingsbackup.tar.gz'):
                    name2 = name.replace('.tar.gz', '').replace('.tar.xz', '').replace('.tar.bz2', '').replace('.tar', '').replace('.zip', '')
                    image_path = os.path.join(self.device_path, name)
                    if os.path.isfile(image_path):
                        images.append((name2, image_path))
        return images

    def doFlash(self):
        self.session.openWithCallback(self.startdoFlash, MessageBox, _('Are you sure to Flash image.'), MessageBox.TYPE_YESNO)

    def startdoFlash(self, answer=True):
        if answer==False:
            return
        if self.deviceok == False:
            return
        idx = self['list'].getSelectionIndex()
        IMAGEPATH = self.images[idx][1]
        IMAGENAME = os.path.split(IMAGEPATH)[1]       
        mytitle = _('Flash image')
        try:
                rsize=os.path.getsize(str(IMAGEPATH).strip())
                msize=float(rsize/(1024*1024))
                if msize<51 :
                   self.session.open(MessageBox, _('seem the image is corrupted,please select another image.'), MessageBox.TYPE_INFO,timeout=4)
                   return               
        except:
                pass
        command=flashScript(IMAGENAME,self.device_path)
        script_backupflash="/tmp/backupflash.sh"
        self.session.open(ProgressScreen, title=mytitle, cmdlist=[script_backupflash],endstr="Swapping image to root started,box will reboot in a moment,please wait...",imagePath=IMAGEPATH)
