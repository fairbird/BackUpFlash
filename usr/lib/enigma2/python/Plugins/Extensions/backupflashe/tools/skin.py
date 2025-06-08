# RAED (c) 2015 - 2025

from enigma import getDesktop
from Screens.Screen import Screen
from Components.Pixmap import Pixmap
import os
from Tools.Directories import resolveFilename, SCOPE_PLUGINS


def DreamOS():
	if os.path.exists('/var/lib/dpkg/status'):
		return DreamOS

#### main menu screen
sz_w = getDesktop(0).size().width()
if sz_w == 1280 :
	SKIN_full_main = """
<screen name="full_main" position="center,center" size="902,400" title="Flash And Full Backup" backgroundColor="#16000000" >
  <widget source="Title" render="Label" font="Regular;35" foregroundColor="#00bab329" position="30,5" size="838,40" transparent="1"/>
  <widget name="config" position="30,48" size="840,186" scrollbarMode="showOnDemand" foregroundColor="#00ffffff" backgroundColor="#16000000"/>
  <widget source="help" render="Label" position="30,239" size="840,79" font="Regular;25" foregroundColor="#00ff2525" backgroundColor="#16000000" valign="center" transparent="1" zPosition="1"/>
  <widget name="lab1" position="30,325" size="840,30" font="Regular;24" valign="center" foregroundColor="#00ffc435" backgroundColor="#16000000" transparent="1"/>
  <ePixmap pixmap="{0}/buttons/red35x35.png" position="35,362" size="35,35" alphatest="blend"/>
  <ePixmap pixmap="{0}/buttons/green35x35.png" position="242,362" size="35,35" alphatest="blend"/>
  <ePixmap pixmap="{0}/buttons/yellow35x35.png" position="455,362" size="35,35" alphatest="blend"/>
  <ePixmap pixmap="{0}/buttons/blue35x35.png" position="665,362" size="35,35" alphatest="blend"/>
  <widget name="key_red" position="70,360" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#ff1f771f" transparent="1"/>
  <widget name="key_green" position="280,360" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#ff9f1313" transparent="1"/>
  <widget name="key_yellow" position="492,360" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#ff9f1313" transparent="1"/>
  <widget name="key_blue" position="700,360" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#ff1f771f" transparent="1"/>
</screen>
""".format(resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe'))
else:
	if DreamOS():
		SKIN_full_main = """
<screen name="full_main" position="center,center" size="1442,888" title="Flash And Full Backup" backgroundColor="#16000000" >
  <widget source="Title" render="Label" font="Regular;35" foregroundColor="#00bab329" position="25,5" size="1408,85" transparent="1"/>
  <widget name="config" position="25,55" size="1406,460" scrollbarMode="showOnDemand" foregroundColor="#00ffffff" backgroundColor="#16000000" zPosition="1"/>
  <widget source="help" render="Label" position="25,560" size="1397,150" font="Regular;30" foregroundColor="#00ff2525" backgroundColor="#16000000" valign="center" transparent="1" zPosition="1"/>
  <widget name="lab1" position="25,715" size="1397,115" font="Regular;30" valign="center" foregroundColor="#00ffc435" backgroundColor="#16000000" transparent="1" zPosition="1"/>
  <ePixmap pixmap="{0}/buttons/red35x35.png" position="25,846" size="35,35" alphatest="blend"/>
  <ePixmap pixmap="{0}/buttons/green35x35.png" position="385,846" size="35,35" alphatest="blend"/>
  <ePixmap pixmap="{0}/buttons/yellow35x35.png" position="744,846" size="35,35" alphatest="blend"/>
  <ePixmap pixmap="{0}/buttons/blue35x35.png" position="1104,846" size="35,35" alphatest="blend"/>
  <widget name="key_red" position="68,843" zPosition="1" size="300,40" font="Regular;30" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#ff9f1313" transparent="1"/>
  <widget name="key_green" position="433,843" zPosition="1" size="300,40" font="Regular;30" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#ff9f1313" transparent="1"/>
  <widget name="key_yellow" position="791,843" zPosition="1" size="300,40" font="Regular;30" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#ff9f1313" transparent="1"/>
  <widget name="key_blue" position="1149,843" zPosition="1" size="300,40" font="Regular;30" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#ff1f771f" transparent="1"/>
</screen>
""".format(resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe'))
	else:
		SKIN_full_main = """
<screen name="full_main" position="center,center" size="1442,888" title="Flash And Full Backup" backgroundColor="#16000000" >
  <widget source="Title" render="Label" font="Regular;35" foregroundColor="#00bab329" position="25,5" size="1408,85" transparent="1"/>
  <widget name="config" position="25,55" size="1406,460" font="Regular;32" secondfont="Regular;32" itemHeight="40" scrollbarMode="showOnDemand" foregroundColor="#00ffffff" backgroundColor="#16000000" zPosition="1"/>
  <widget source="help" render="Label" position="25,560" size="1397,150" font="Regular;30" foregroundColor="#00ff2525" backgroundColor="#16000000" valign="center" transparent="1" zPosition="1"/>
  <widget name="lab1" position="25,715" size="1397,115" font="Regular;30" valign="center" foregroundColor="#00ffc435" backgroundColor="#16000000" transparent="1" zPosition="1"/>
  <ePixmap pixmap="{0}/buttons/red35x35.png" position="25,846" size="35,35" alphatest="blend"/>
  <ePixmap pixmap="{0}/buttons/green35x35.png" position="385,846" size="35,35" alphatest="blend"/>
  <ePixmap pixmap="{0}/buttons/yellow35x35.png" position="744,846" size="35,35" alphatest="blend"/>
  <ePixmap pixmap="{0}/buttons/blue35x35.png" position="1104,846" size="35,35" alphatest="blend"/>
  <widget name="key_red" position="68,843" zPosition="1" size="300,40" font="Regular;30" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#ff9f1313" transparent="1"/>
  <widget name="key_green" position="433,843" zPosition="1" size="300,40" font="Regular;30" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#ff9f1313" transparent="1"/>
  <widget name="key_yellow" position="791,843" zPosition="1" size="300,40" font="Regular;30" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#ff9f1313" transparent="1"/>
  <widget name="key_blue" position="1149,843" zPosition="1" size="300,40" font="Regular;30" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#ff1f771f" transparent="1"/>
</screen>
""".format(resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe'))

#### doFlash screen
sz_w = getDesktop(0).size().width()
if sz_w == 1280 :
	SKIN_doFlash = """
<screen position="center,center" size="902,380" title="Flash image" backgroundColor="#16000000" >
<widget source="Title" render="Label" font="Regular;35" foregroundColor="#00bab329" position="30,5" size="838,40" transparent="1"/>
<widget name="list" position="20,45" size="875,250" scrollbarMode="showOnDemand" foregroundColor="#00ffffff" backgroundColor="#16000000"/>
<widget name="lab1" position="30,300" size="840,30" font="Regular;24" valign="center"  foregroundColor="#00ffc435" backgroundColor="#16000000" transparent="1"/>
<ePixmap pixmap="{0}/buttons/red35x35.png" position="200,342" size="35,35" alphatest="blend"/>
<ePixmap pixmap="{0}/buttons/green35x35.png" position="550,342" size="35,35" alphatest="blend"/>
<widget name="key_red" position="210,340" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#9f1313" transparent="1"/>
<widget name="key_green" position="570,340" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#1f771f" transparent="1"/>
</screen>
""".format(resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe'))
else:
	if DreamOS():
		SKIN_doFlash = """
<screen name="Flash image" position="center,center" size="1146,734" title="Flash image" backgroundColor="#16000000" >
<widget source="Title" render="Label" font="Regular;35" foregroundColor="#00bab329" position="20,5" size="1264,82" transparent="1"/>
  <widget name="list" position="20,95" size="1259,681" scrollbarMode="showOnDemand" foregroundColor="#00ffffff" backgroundColor="#16000000"/>
  <widget name="lab1" position="20,785" size="1255,108" font="Regular;35" valign="center" foregroundColor="#00ffc435" backgroundColor="#16000000" transparent="1"/>
  <ePixmap pixmap="{0}/buttons/red35x35.png" position="209,919" size="35,35" alphatest="blend"/>
  <ePixmap pixmap="{0}/buttons/green35x35.png" position="730,919" size="35,35" alphatest="blend"/>
  <widget name="key_red" position="255,916" zPosition="1" size="300,40" font="Regular;30" valign="center" foregroundColor="#00ffffff" backgroundColor="#ff9f1313" transparent="1"/>
  <widget name="key_green" position="776,916" zPosition="1" size="300,40" font="Regular;30" valign="center" foregroundColor="#00ffffff" backgroundColor="#ff1f771f" transparent="1"/>
</screen>
""".format(resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe'))
	else:
		SKIN_doFlash = """
<screen name="Flash image" position="center,center" size="1146,734" title="Flash image" backgroundColor="#16000000" >
<widget source="Title" render="Label" font="Regular;35" foregroundColor="#00bab329" position="20,5" size="1264,82" transparent="1"/>
  <widget name="list" font="Regular;30" itemHeight="40" position="20,95" size="1259,681" scrollbarMode="showOnDemand" foregroundColor="#00ffffff" backgroundColor="#16000000"/>
  <widget name="lab1" position="20,785" size="1255,108" font="Regular;35" valign="center" foregroundColor="#00ffc435" backgroundColor="#16000000" transparent="1"/>
  <ePixmap pixmap="{0}/buttons/red35x35.png" position="209,919" size="35,35" alphatest="blend"/>
  <ePixmap pixmap="{0}/buttons/green35x35.png" position="730,919" size="35,35" alphatest="blend"/>
  <widget name="key_red" position="255,916" zPosition="1" size="300,40" font="Regular;30" valign="center" foregroundColor="#00ffffff" backgroundColor="#ff9f1313" transparent="1"/>
  <widget name="key_green" position="776,916" zPosition="1" size="300,40" font="Regular;30" valign="center" foregroundColor="#00ffffff" backgroundColor="#ff1f771f" transparent="1"/>
</screen>
""".format(resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe'))

#### imagedownloadScreen screen
sz_w = getDesktop(0).size().width()
if sz_w == 1280 :
	SKIN_imagedownloadScreen = """
<screen name="imagedownloadScreen" position="center,center" size="560,160" title="Downloading image..." backgroundColor="#16000000">
<!--widget name="activityslider" position="20,40" size="510,15" pixmap="skin_default/progress_big.png" /-->
<widget name="activityslider" position="20,45" size="510,20" borderWidth="1" transparent="1"/>
<widget name="package" position="20,10" size="510,29" font="Regular;18" halign="center" valign="center" transparent="1"/>
<widget name="status" position="20,70" size="510,28" font="Regular;16" foregroundColor="#00ffffff" backgroundColor="#16000000" halign="center" valign="center" transparent="1"/>
<widget name="status2" position="20,10" size="510,142" font="Regular;25" foregroundColor="#00bab329" backgroundColor="#16000000" halign="center" valign="center" transparent="1"/>
<widget name="info" position="11,109" size="534,40" font="Regular;25" foregroundColor="#00ff2525" backgroundColor="#16000000" halign="center" valign="center" transparent="1"/>
<!--widget name="key_green" position="8,107" zPosition="2" size="532,22" font="Regular;22" halign="center" valign="center" foregroundColor="#00389416" backgroundColor="#16000000" transparent="1"/-->
<!--ePixmap pixmap="{0}/buttons/green35x35.png" position="180,125" size="35,35" alphatest="blend"/-->
</screen>
""".format(resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe'))
else:
	SKIN_imagedownloadScreen = """
<screen name="imagedownloadScreen" position="center,center" size="805,232" title="Downloading image..." backgroundColor="#16000000">
<!--widget name="activityslider" position="30,60" size="765,22" pixmap="skin_default/progress_big.png" /-->
<widget name="activityslider" position="30,48" size="755,30" borderWidth="1" transparent="1"/>
<widget name="package" position="30,7" size="755,35" font="Regular;27" halign="center" valign="center" transparent="1"/>
<widget name="status" position="30,90" size="755,40" font="Regular;24" foregroundColor="#00ffffff" backgroundColor="#16000000" halign="center" valign="center" transparent="1"/>
<widget name="status2" position="14,10" size="771,217" font="Regular;30" foregroundColor="#00bab329" backgroundColor="#16000000" halign="center" valign="center" transparent="1"/>
<widget name="info" position="11,185" size="784,40" font="Regular;28" foregroundColor="#00ff2525" backgroundColor="#16000000" halign="center" valign="center" transparent="1"/>
<!--widget name="key_green" position="11,139" zPosition="2" size="784,40" font="Regular;28" halign="center" valign="center" foregroundColor="#00389416" backgroundColor="#16000000" transparent="1"/-->
<!--ePixmap pixmap="{0}/buttons/green35x35.png" position="290,190" size="35,35" alphatest="blend"/-->
</screen>
""".format(resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe'))

#### progress screen
sz_w = getDesktop(0).size().width()
if sz_w == 1280 :
	SKIN_Progress = """
<screen name="Progress..." position="center,center"  size="550,178" title="Downloading image..." backgroundColor="#16000000" >
<widget source="Title" render="Label" font="Regular;24" foregroundColor="#00bab329" backgroundColor="#16000000" position="10,5" size="530,25" transparent="1"/>
<eLabel text="" position="10,31" zPosition="3" size="531,1" font="Regular;5" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#00ffffff"/>
<widget name="text" position="10,32" size="530,75" font="Regular;18" backgroundColor="#16000000"/>
<eLabel text="Press Exit Button to cancel job" position="10,108" zPosition="2" size="531,26" font="Regular;22" halign="center" valign="center" foregroundColor="#00ff2525" backgroundColor="#16000000"/>
<eLabel text="Press Ok Button to Hide/Show Screen" position="10,133" zPosition="2" size="531,26" font="Regular;22" halign="center" valign="center" foregroundColor="#00bab329" backgroundColor="#16000000"/>
<widget name="slider" position="0,162" size="550,15" borderWidth="1" transparent="1" />
</screen>"""
else:
	SKIN_Progress = """
<screen name="Progress..." position="center,center" size="850,259" title="Downloading image..." backgroundColor="#16000000" >
<widget source="Title" render="Label" font="Regular;30" foregroundColor="#00bab329" backgroundColor="#16000000" position="20,5" size="815,35" transparent="1"/>
<eLabel text="" position="20,41" zPosition="3" size="815,2" font="Regular;5" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#00ffffff"/>
<widget name="text" position="20,45" size="815,115" font="Regular;28" backgroundColor="#16000000"/>
<eLabel text="Press Exit Button to cancel job" position="32,163" zPosition="2" size="784,35" font="Regular;28" halign="center" valign="center" foregroundColor="#00ff2525" backgroundColor="#16000000"/>
<eLabel text="Press Ok Button to Hide/Show Screen" position="32,200" zPosition="2" size="784,35" font="Regular;28" halign="center" valign="center" foregroundColor="#00bab329" backgroundColor="#16000000"/>
<widget name="slider" position="0,238" size="850,20" borderWidth="1" transparent="1"/>
</screen>"""

#### Selection Screen
if sz_w == 1280 :
	SKIN_SelectionScreen = """
<screen name="SelectionScreen" position="center,center" size="560,400" title="Select Options">
        <widget source="list" render="Listbox" position="10,10" size="540,300" scrollbarMode="showOnDemand">
            <convert type="TemplatedMultiContent">
                {
                    "template": [
                        MultiContentEntryText(pos=(50,0), size=(450,50), font=0, text=0),
                        MultiContentEntryPixmapAlphaBlend(pos=(0,0), size=(50,50), png=1)
                    ],
                    "fonts": [gFont("Regular", 24)],
                    "itemHeight": 50
                }
            </convert>
        </widget>
<ePixmap pixmap="%s/buttons/red35x35.png" position="35,362" size="35,35" alphatest="blend"/>
<ePixmap pixmap="%s/buttons/green35x35.png" position="317,362" size="35,35" alphatest="blend"/>
<widget name="key_red" position="70,360" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="right" foregroundColor="#00ffffff" backgroundColor="#ff1f771f" transparent="1"/>
<widget name="key_green" position="350,360" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="right" foregroundColor="#00ffffff" backgroundColor="#ff9f1313" transparent="1"/>
</screen>
""" % (resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe'), resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe'))
else:
	SKIN_SelectionScreen = """
<screen name="SelectionScreen" position="center,center" size="738,524" title="Select Options">
        <widget source="list" render="Listbox" position="10,10" size="716,461" scrollbarMode="showOnDemand">
            <convert type="TemplatedMultiContent">
                {
                    "template": [
                        MultiContentEntryText(pos=(85,10), size=(650,50), font=0, text=0),
                        MultiContentEntryPixmapAlphaBlend(pos=(0,0), size=(50,50), png=1)
                    ],
                    "fonts": [gFont("Regular", 35)],
                    "itemHeight": 60
                }
            </convert>
        </widget>
<ePixmap pixmap="%s/buttons/red35x35.png" position="35,487" size="35,35" alphatest="blend"/>
<ePixmap pixmap="%s/buttons/green35x35.png" position="407,487" size="35,35" alphatest="blend"/>
<widget name="key_red" position="70,480" zPosition="1" size="246,40" font="Regular;35" halign="center" valign="right" foregroundColor="#00ffffff" backgroundColor="#ff1f771f" transparent="1"/>
<widget name="key_green" position="445,480" zPosition="1" size="246,40" font="Regular;35" halign="center" valign="right" foregroundColor="#00ffffff" backgroundColor="#ff9f1313" transparent="1"/>
</screen>
""" % (resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe'), resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe'))
