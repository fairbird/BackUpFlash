#!/usr/bin/python
# -*- coding: utf-8 -*-
# RAED & mfaraj57 &  (c) 2018
# Code RAED & mfaraj57

# python3
from __future__ import print_function

from enigma import eConsoleAppContainer, eTimer
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from Screens.MessageBox import MessageBox
from Components.ProgressBar import ProgressBar
from Components.Slider import Slider
from Screens.Standby import TryQuitMainloop
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import os
from .skin import *
from .bftools import logdata, copylog, getboxtype, getimage_name

backup_progress = 0
flash_progress = 0
imagename = getimage_name()

def rootspace():
    try:
        diskSpace = os.statvfs("/")
        capacity = float(diskSpace.f_bsize * diskSpace.f_blocks)
        available = float(diskSpace.f_bsize * diskSpace.f_bavail)
        fspace = round(float(available / 1048576.0), 2)
        tspace = round(float(capacity / 1048576.0), 1)
        spacestr = 'Free space(' + str(fspace) + 'MB) Total space(' + str(tspace) + 'MB)'
        rused=capacity-available
        return rused
    except:
        return

class ProgressScreen(Screen):
    def __init__(self, session, title = 'Console', cmdlist = None, finishedCallback = None, closeOnSuccess = False, endstr = '', imagePath = ''):
        Screen.__init__(self, session)
        self.skin = SKIN_Progress
        self.session = session
        if endstr == '':
            self.processType = 'backup'
        else:
            self.processType = 'flash'
        st = os.statvfs('/')
        self.root_size =(st.f_blocks - st.f_bfree) * st.f_frsize
        self.endstr = endstr
        self.imagePath = str(imagePath).strip()
        try:
            self.image_size = os.path.getsize(str(self.imagePath).strip())
        except:
            pass
        self.device_path = os.path.split(self.imagePath)[0]
        self.finishedCallback = finishedCallback
        self.closeOnSuccess = closeOnSuccess
        self['text'] = ScrollLabel('')
        self.slider = Slider(0, 100)
        self['slider'] = self.slider
        self.shown = True
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions', 'ColorActions'], {'ok': self.hideshow,
         'back': self.cancel,
         'blue': self.restartenigma,
         'up': self['text'].pageUp,
         'down': self['text'].pageDown}, -1)
        self.cmdlist = cmdlist
        self.newtitle = title
        self.onShown.append(self.updateTitle)
        self.container = eConsoleAppContainer()
        self.run = 0
        self.finished = False
        try:
            self.container.appClosed.append(self.runFinished)
            self.container.dataAvail.append(self.dataAvail)
        except:
            self.appClosed_conn = self.container.appClosed.connect(self.runFinished)
            self.dataAvail_conn = self.container.dataAvail.connect(self.dataAvail)
        self.onLayoutFinish.append(self.startRun)

    def updateTitle(self):
        self.setTitle(self.newtitle)

    def checkflashProgress(self):
        self.image_size=0
        self.flashingtime = self.flashingtime + 10
        if self.process_finished == False:
            rsize = 0
            tarimage = '%s/tmp/rootfs.tar' % self.device_path
            try:
                self.tarimage_size = os.path.getsize(str(tarimage).strip())
            except:
                trace_error()
                pass
            try:
                self.image_size = os.path.getsize(str(self.imagePath).strip())
            except:
                trace_error()
                pass
            boxtype = getboxtype()
            gfactor=1
            xfactor=1
            if boxtype == 'dm520':
                gfactor=.23
                xfactor=.6
            elif boxtype == 'dm900' or boxtype=='dm920':
                gfactor=.43
                xfactor=.26
            else: #dm820,dm7080
                gfactor=3
                xfactor=4.5
            self.setTitle('Extracting ' + str(float(self.tarimage_size / 1067008)) + ' MB')
            gfactor=.3
            xfactor=.3
            if self.tarimage_size > 0:
                if self.imagePath.endswith(".gz"):
                   flash_progress=int(100*gfactor*self.tarimage_size /self.image_size)
                else:
                   flash_progress=int(100*xfactor*self.tarimage_size /self.image_size)
                self.slider.setValue( flash_progress)
                self.TimerFlashing.start(1000, True)
        else:
            flash_progress_progress = 0
            self.TimerFlashing = eTimer()
            self.TimerFlashing.stop()

    def checkbackupProgress(self):
        global backup_progress
        self.backuptime = self.backuptime + 2
        boxtype = getboxtype()
        if self.process_finished == False:
            rsize = 0
            try:
                self.image_size = os.path.getsize(self.imagePath)
            except:
                self.image_size=0
            root_size = self.root_size
            gfactor = 1
            xfactor = 1
            if boxtype == 'dm520':             
                gfactor = 4.20
                xfactor = 4.12
            elif boxtype == 'dm900' or boxtype=='dm920':
                gfactor = 3
                xfactor = 4.5
            else: #dm820,dm7080
                gfactor = 3.3
                xfactor = 5
            if self.root_size < 1:
                self.root_size = 0
                backup_progress = 3
            if self.image_size > 0:
                if self.imagePath.endswith(".gz"):
                   backup_progress =  int(550*gfactor*self.image_size /(root_size))
                else:
                   backup_progress =  int(500*xfactor*self.image_size /(root_size))
                self.setTitle('Backup ' + str(int(float(self.image_size / 1067008)))+" MB")
                self.slider.setValue( backup_progress)
            self.TimerBackup.start(2000, True)
        else:
            backup_progress = 0
            self.slider.setValue(0)
            self.TimerBackup = eTimer()
            self.TimerBackup.stop()

    def startRun(self):
        global backup_progress
        global flash_progress
        self.process_finished = False
        backup_progress = 0
        flash_progress = 0
        if self.processType == 'backup':
            self.backuptime = 0
            self.TimerBackup = eTimer()
            try:
                self.TimerBackup.stop()
            except:
                pass

            if not os.path.exists('/var/lib/opkg/status'):
                self.TimerBackup_conn = self.TimerBackup.timeout.connect(self.checkbackupProgress)
            else:
                self.TimerBackup.callback.append(self.checkbackupProgress)
            self.TimerBackup.start(10000, True)
            startstr = 'Backup started for (%s)' % imagename.replace("Backup-","")
        else:
            self.flashingtime = 0
            self.TimerFlashing = eTimer()
            self.TimerFlashing.stop()
            if not os.path.exists('/var/lib/opkg/status'):
                self.TimerFlashing_conn = self.TimerFlashing.timeout.connect(self.checkflashProgress)
            else:
                self.TimerFlashing.callback.append(self.checkflashProgress)
            self.TimerFlashing.start(1000, True)
            startstr = 'Flash started'
        self['text'].setText(_(startstr) + '\n\n')
        print('Console: executing in run', self.run, ' the command:', self.cmdlist[self.run])
        if self.container.execute(self.cmdlist[self.run]):
            self.runFinished(-1)

    def runFinished(self, retval):
        self.run += 1
        if self.run != len(self.cmdlist):
            if self.container.execute(self.cmdlist[self.run]):
                self.runFinished(-1)
        else:
            self.finished = True
            self.process_finished = True
            str = self['text'].getText()
            self.instance.show()
            if retval and not self.processType == 'backup':
                pass
            elif not retval and self.processType == 'flash':
                str = self.endstr
                self['text'].setText(str)
            else:
                str += _('Backup finished!!\nPress exit Button')
                #print('[backupflash] found finished process ...')
            if os.path.exists('/tmp/bbackup.scr'):
                os.remove('/tmp/bbackup.scr')
            if retval :
                tarimage="%s/tmp/rootfs.tar" % self.device_path
                if os.path.exists(self.imagePath):
                     os.remove(self.imagePath)
                if os.path.exists(tarimage):
                     os.remove(tarimage)
            copylog(self.device_path)
            backupflash_progress = 0
            self.slider.setValue(0)
            if self.processType == 'flash':
                self.TimerFlashing = eTimer()
                self.TimerFlashing.stop()
            else:
                self.TimerBackup = eTimer()
                self.TimerBackup.stop()
            print('finished process')
            self['text'].setText(str)
            self['text'].lastPage()
            if self.finishedCallback is not None:
                self.finishedCallback(retval)
            if not retval and self.closeOnSuccess:
                self.cancel()
            self.cancel()
        return

    def hideshow(self):
        if self.finished:
            return
        if self.shown:
            self.hide()
        else:
            self.show()

    def cancel(self):
        if self.run == len(self.cmdlist):
            try:
                self.appClosed_conn = None
                self.dataAvail_conn = None
            except:
                self.container.appClosed.remove(self.runFinished)
                self.container.dataAvail.remove(self.dataAvail)
            self.close()
        else:
            self.session.openWithCallback(self.abort, MessageBox, _('Are you sure to cancel %s' % self.processType), MessageBox.TYPE_YESNO)
        return

    def abort(self, answer = False):
        os.system("touch /tmp/.cancelBackup")
        PLUGINROOT = resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe')
        PLUGINBACKUP = resolveFilename(SCOPE_PLUGINS, 'Extensions/dBackup')
        if answer:
            tarimage = '%s/tmp/rootfs.tar' % self.device_path
            os.system("kill -9 $(ps aux | grep backupflash.sh | awk '{print $2}')")
            self.container.sendCtrlC()
            self.container.sendEOF()
            if os.path.exists(PLUGINBACKUP):
                os.system('mv %s %s' % (PLUGINBACKUP, PLUGINROOT))
            #if os.path.exists(self.imagePath): #these lines delete image from path of image (not recommanded)
            #    os.remove(self.imagePath)
            if os.path.exists(tarimage):
                os.remove(tarimage)
            try:
                self.appClosed_conn = None
                self.dataAvail_conn = None
            except:
                self.container.appClosed.remove(self.runFinished)
                self.container.dataAvail.remove(self.dataAvail)
            self.close()

    def dataAvail(self, str):
        self['text'].setText(self['text'].getText()) ## PY3
        #self['text'].setText(self['text'].getText() + str)

    def processAnswer(self, retval):
        if retval:
            self.container.write('Y', 1)
        else:
            self.container.write('n', 1)
        self.dataSent_conn = self.container.dataSent.connect(self.processInput)

    def processInput(self, retval):
        self.container.sendEOF()

    def restartenigma(self):
        self.session.open(TryQuitMainloop, 3)
