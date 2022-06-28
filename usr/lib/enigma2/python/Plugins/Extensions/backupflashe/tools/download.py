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
from Components.ConfigList import ConfigListScreen
from enigma import eTimer, eConsoleAppContainer
from Components.GUIComponent import *
from Components.HTMLComponent import *
from Components.ProgressBar import ProgressBar
from Tools.Downloader import downloadWithProgress
from os import system as os_system
from os import path as os_path

import datetime
import os
import time

from .skin import *
from .bftools import logdata, copylog

class imagedownloadScreen(Screen):
    def __init__(self, session, name='', url='', target='',canflash=True):
        Screen.__init__(self, session)
        self.skin = SKIN_imagedownloadScreen
        self.canflash=canflash
        self.target = target
        self.name=name
        self.url=url
        self.shown=True
        self.count_success = 0
        self.success=False 
        self['activityslider'] = ProgressBar()
        self['activityslider'].setRange((0, 100))
        self['activityslider'].setValue(0)
        self['status'] = Label()
        self['package'] = Label()
        if self.canflash:
           self['key_green'] = Label('Press Green Button to Flash image')
        else:
           self['key_green'] = Label(' ') 
        self['key_green'].hide()
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'green': self.doFlash,
          'ok': self.okclicked,
         'cancel': self.dexit}, -1)
        self['status'].setText(_('Waiting to get resouces free...'))
        self.downloading = False
        self.downloader = None
        self.setTitle(_('Connecting') + '...')
        self.timer = eTimer()
        try:
            self.timer.callback.append(self.startDownload)
        except:
            self.timer_conn = self.timer.timeout.connect(self.startDownload)
        self.timer.start(100, 1)

    def startDownload(self):
        try:
            self.timer.stop()
            del self.timer
        except:
            pass
        self.currentIndex = 0
        self.count_success = 0
        self.count_failed = 0
        self.downloading = True
        self.downloadimage()

    def progress(self, current, total):
        p = int(100 * (float(current) / float(total)))
        self['activityslider'].setValue(p)
        info = _('Downloading') + ' ' + '%d of %d kBytes' % (current / 1024, total / 1024)
        self['package'].setText(self.name)
        self['status'].setText(info)
        self.setTitle(_('Downloading') + ' ' + str(p) + '%...')

    def responseCompleted(self, data = None):
        print('[BackUpFlash downloader] Download succeeded. ')
        logdata("download data",str(data))
        logdata("download status","Download succeeded.")
        info = 'Download completed successfully,press (green) to start flashing   '
        self['status'].setText(info)
        self.setTitle(_('Download completed successfully.'))
        self.downloading = False
        if self.canflash:
           self['key_green'].show()
        else:
           self['key_green'].hide() 
        self.success=True
        self.instance.show()

    def responseFailed(self, failure_instance = None, error_message = ''):
        print('[BackUpFlash downloader] Download failed. ')
        logdata("download status","Download failed."+error_message)
        self.error_message = error_message
        if error_message == '' and failure_instance is not None:
            self.error_message = failure_instance.getErrorMessage()
        info = self.error_message
        self['status'].setText(info)
        self.setTitle(_('Download failed Press Exit'))
        cmd = "echo 'message' > /tmp/.download_error.log"
        cmd = cmd.replace('message', info)
        self.container = eConsoleAppContainer()
        self.container.execute(cmd)
        self.downloading = False
        self.success=False
        self['key_green'].hide()
        self.instance.show()
        self.remove_target()
        return

    def dexit(self):
        try:
            path=os.path.split(self.target)[0]
            copylog(path)
        except:
            pass
        
        if self.downloading:
            self.session.openWithCallback(self.abort, MessageBox, _('Are you sure to stop download.'), MessageBox.TYPE_YESNO)
        else:
            self.close(False)

    def remove_target(self):
            try:
                if os.path.exists(self.target):
                    os.remove(self.target)
            except:
                pass

    def abort(self,answer=True):
        if answer==False:
            return
        if not self.downloading:
            if os_path.exists('/tmp/download_install.log'):
               os.remove('/tmp/download_install.log')
            self.close(False)
        elif self.downloader is not None:
            self.downloader.stop
            info = _('Aborting...')
            self['status'].setText(info)
            cmd = 'echo canceled > /tmp/.download_error.log ; rm target'
            cmd = cmd.replace('target', self.target)
            self.remove_target()
            try:
                self.close(False)
            except:
                pass
        else: 
            self.close(False)
        return

    def AbortOnClose(self, result):
        self.close(False)

    def downloadimage(self):
        debug = True
        if True:
                self['package'].setText(self.name)
                self.setTitle(_('Connecting') + '...')
                self['status'].setText(_('Connecting') + ' to server....')
                self.downloading = True
                logdata('image link',self.url)
                self.downloader = downloadWithProgress(self.url, self.target)
                self.downloader.addProgress(self.progress)
                self.downloader.start().addCallback(self.responseCompleted).addErrback(self.responseFailed)

    def doFlash(self):
        if not self.canflash:
            return
        if not self.downloading and self.success:
            self.close(True)

    def okclicked(self):
        if not self.downloading:
           self.instance.show()
           self.shown=True
           return
        if self.shown:
            self.shown=False
            self.instance.hide()
        else:
            self.instance.show()
            self.shown=True
