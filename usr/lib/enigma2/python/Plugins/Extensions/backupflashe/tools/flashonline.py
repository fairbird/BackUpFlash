#!/usr/bin/python
# -*- coding: utf-8 -*-
# RAED & mfaraj57 (c) 2015 - 2025

# python3
from .compat import PY3

from enigma import eTimer
from Components.ActionMap import ActionMap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Screens.ChoiceBox import ChoiceBox
import requests,re
import os
from Components.config import config

from .skin import *
from .Console import Console
from .download import imagedownloadScreen
from .bftools import logdata, getboxtype, get_images, url_exists, get_images_mediafire, copylog, trace_error

headers = {
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
}

class teamsScreen(Screen):
	def __init__(self, session,device_path):
		Screen.__init__(self, session)
		self.skin = SKIN_doFlash
		self.device_path=device_path
		self.list = []
		self['key_red'] = Label(_('Cancel'))
		self['key_green'] = Label(_('Select'))
		self['lab1'] = Label('Select team')
		self['list'] = MenuList([])
		self['path'] = Label(" ")
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'red': self.close,
		 	'green': self.load_images,
		 	'ok': self.load_images,							       
		 	'back': self.close})
		self['key_green'].hide()
		self.teams = []
		self.list = []
		self.timer = eTimer()
		try:
			self.timer.callback.append(self.layoutFinished)
		except:
			self.timer_conn = self.timer.timeout.connect(self.layoutFinished)
		self.timer.start(6, 1)

	def layoutFinished(self):
		self.timer.stop()
		self.list = []
		self.setTitle("Images Team Download")
		self.updateList()

	def updateList(self):
		list1 = []
		list1.append(("DreamOS OE2.5 Images", "DreamOS OE2.5 Images"))
		list1.append(("Open Source OE2.0 Images", "Open Source OE2.0 Images"))
		list1.append(("Neutrino Images", "Neutrino Images"))
		self.session.openWithCallback(self.get_teams, ChoiceBox, _('select image type'), list1)

	def get_teams(self,select):
		self.list=[]
		if select:
			if select[0] == "DreamOS OE2.5 Images":
				self.teams=self.DreamOS()
			elif select[0] == "Open Source OE2.0 Images":
				self.teams=self.opensource()
			else:
				self.teams=self.neutrino()
			logdata("self.teams",self.teams)
			self['list'].setList(self.teams)
			self['key_green'].show()
		else:
			self.close()

	def DreamOS(self):
		boxtype=getboxtype()
		logdata("boxtype",boxtype)
		teams = []
		teams.append((_("Dreamboxupdates-Stable"), "Dreamboxupdates-Stable"))
		teams.append((_("Dreamboxupdates-UnStable"), "Dreamboxupdates-UnStable"))
		teams.append((_("Gemini4"), "Gemini4"))
		teams.append((_("DreamElite"), "DreamElite"))
		teams.append((_("Merlin4"), "Merlin4"))
		teams.append((_("Satlodge"), "Satlodge"))
		teams.append((_("Newnigma2"), "Newnigma2"))
		#teams.append((_("OoZooN"), "OoZooN")) ## No more Team
		#teams.append((_("Demonisat"), "Demonisat")) ## Server down
		#teams.append((_("Powersat"), "Powersat")) ## No more Team
		return teams

	def opensource(self):
		boxtype=getboxtype()
		logdata("boxtype",boxtype)
		teams = []
		#teams.append((_("________________ Python3 Images ________________"), ))
		teams.append((_("BlackHole"), "BlackHole"))
		teams.append((_("OpenTSimage"), "OpenTSimage"))
		teams.append((_("OpenPLI-Unoffical"), "OpenPLI-Unoffical"))
		teams.append((_("OpenPLi9xstar-japhar"), "OpenPLi9xstar-japhar"))
		teams.append((_("OpenBH-Unoffical"), "OpenBH-Unoffical"))
		teams.append((_("OpenATV"), "OpenATV-Python3"))
		teams.append((_("OpenVIX"), "OpenVIX"))
		teams.append((_("OpenVIX-Unoffical"), "OpenVIX-Unoffical"))
		teams.append((_("PurE2"), "PurE2"))
		teams.append((_("OpenDroid"), "OpenDroid"))
		teams.append((_("OpenSatlodge"), "OpenSatlodge"))
		teams.append((_("TeamBlue"), "TeamBlue"))
		teams.append((_("OpenHDF"), "OpenHDF"))
		teams.append((_("AFF-TitanNit"), "AFF-TitanNit"))
		teams.append((_("OpenVision"), "OpenVision"))
		#teams.append((_("Open-cobralibero"), "Open-cobralibero Python3"))
		#teams.append((_("________________ Python2 Images ________________"), ))
		#teams.append((_("OpenATV"), "OpenATV-Python2"))
		#teams.append((_("NonSoloSat"), "NonSoloSat"))
		#teams.append((_("ArEaDeLtA-SaT"), "ArEaDeLtA-SaT")) ## No more Team
		#teams.append((_("OpenESI"), "OpenESI")) ## No more Team
		#teams.append((_("Openeight-Unoffical"), "Openeight-Unoffical")) ## No more update images
		#teams.append((_("PKTeam"), "PKTeam")) ## No more Url download
		#teams.append((_("OpenVision"), "OpenVision Python2")) ## No more Url download
		return teams

	def neutrino(self):
		boxtype=getboxtype()
		logdata("boxtype",boxtype)
		teams = []
		teams.append(("BPanther", "BPanther"))
		return teams

	def load_images(self):
		idx = self['list'].getSelectionIndex()
		teamName = self.teams[idx][0]
		imagesPath = self.teams[idx][1]
		self.session.open(imagesScreen,self.device_path,teamName, imagesPath)


class imagesScreen(Screen):
	def __init__(self, session,device_path,teamName, imagesPath):
		Screen.__init__(self, session)
		self.skin = SKIN_doFlash
		self.teamName = imagesPath
		self.imagesPath = imagesPath
		self.device_path=device_path
		self.list = []
		self['key_red'] = Label(_('Cancel'))
		self['key_green'] = Label(_('Download'))
		self['key_green'].hide()
		self['lab1'] = Label('Loading images,please wait...')
		self['list'] = MenuList([])
		self['path'] = Label(" ")
		self.imageok=False
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'red': self.close,
			'green': self.download,
			'ok': self.download,							       
			'back': self.close})
		self.teams = []
		self.imageok=False
		self.canflash=True
		self.timer=eTimer()
		try:
			self.timer.callback.append(self.updateList)
		except:
			self.timer_conn = self.timer.timeout.connect(self.updateList)
		self.timer.start(6, 1)
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(self.teamName)
	   
	def updateList(self):
		self.images=[]
		self.images=self.getteam_images()
		logdata("self.images",self.images)
		if len(self.images)>0:
			self['list'].setList(self.images)
			self['key_green'].show()
			self.imageok=True
			self['lab1'].setText('select image to download')
		else:
			self['lab1'].setText("Unable to get images,internet down or server unresponsive")
			self['key_green'].hide()
			self.imageok=False

	def getteam_images(self):
		images = []
		boxtype = getboxtype()
		self.urlimage = ''

		if self.teamName == "BlackHole":
			if boxtype == "dm920":
				key = 'cdmen9tqtpwxk'
			elif boxtype == "dm520":
				key = 'gkhsdcxiikosk'
			elif boxtype == "dm7080":
				key = '5cmni3i0rch9e'
			elif boxtype == "dm820":
				key = '60ptu82mgakx6'
			else:
				return []
			imagesPath = 'https://www.mediafire.com/api/1.4/folder/get_content.php?r=cfgd&content_type=files&filter=all&order_by=name&order_direction=asc&chunk=1&version=1.5&folder_key=%s&response_format=json' % key
			rimages = get_images_mediafire(imagesPath)
			for item in rimages:
				imageName = item[0]
				imagePath = item[1]
				images.append((imageName, imagePath))

		if self.teamName == "OpenTSimage":
			if boxtype == "dm920":
				key = 'sbrjw60if73re'
			elif boxtype == "dm520":
				key = 'gnxuy5xl3vmjo'
			elif boxtype == "dm7080":
				key = 'tb1x6tmtglyw4'
			else:
				return []
			imagesPath = 'https://www.mediafire.com/api/1.4/folder/get_content.php?r=cfgd&content_type=files&filter=all&order_by=name&order_direction=asc&chunk=1&version=1.5&folder_key=%s&response_format=json' % key
			rimages = get_images_mediafire(imagesPath)
			for item in rimages:
				imageName = item[0]
				imagePath = item[1]
				images.append((imageName,imagePath))

		if self.teamName == "OpenATV-Python2":
			imagesPath = "https://images.mynonpublic.com/openatv/6.4/index.php?open="+boxtype
			regx = b'''<a href='(.*?)'>(.*?)</a>'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				imageName2 = item[0]
				if PY3:
					imageName = imageName.decode()
					imageName2 = imageName2.decode()
				imagePath =  os.path.join('https://images.mynonpublic.com/openatv/6.4/', imageName2)
				images.append((imageName,imagePath))

		if self.teamName == "OpenATV-Python3":
			imagesPath = "https://images.mynonpublic.com/openatv/7.6/index.php?open="+boxtype
			regx = b'''<a href='(.*?)'>(.*?)</a>'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				imageName2 = item[0]
				if PY3:
					imageName = imageName.decode()
					imageName2 = imageName2.decode()
				imagePath =  os.path.join('https://images.mynonpublic.com/openatv/7.6/', imageName2)
				images.append((imageName,imagePath))

		if self.teamName == "OpenPLI-Unoffical":
			imagesPath='https://www.mediafire.com/api/1.4/folder/get_content.php?r=cfgd&content_type=files&filter=all&order_by=name&order_direction=asc&chunk=1&version=1.5&folder_key=5mqob16bb176n&response_format=json'
			rimages=get_images_mediafire(imagesPath)
			for item in rimages:
				imageName = item[0]
				imagePath = item[1]
				if not boxtype in imageName:
					continue
				images.append((imageName,imagePath))

		if self.teamName == "OpenPLi9xstar-japhar":
			imagesPath = "http://openpli9xstar.japhar.net/OpenPLi9xstar/"
			regx = b'''<a href="http://openpli9xstar.japhar.net/OpenPLi9xstar/(.*?)">(.*?)</a>'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				imageName = imageName.replace(b" (Original)", b"").replace(b" (Japhar)", b"")
				logdata("imageName",imageName)
				if PY3:
					imageName = imageName.decode()
				imagePath = os.path.join("http://openpli9xstar.japhar.net/OpenPLi9xstar/", imageName)
				if not boxtype in imageName:
					continue
				images.append((imageName,imagePath))

		if self.teamName == "Openeight-Unoffical":
			imagesPath='https://www.mediafire.com/api/1.4/folder/get_content.php?r=cfgd&content_type=files&filter=all&order_by=name&order_direction=asc&chunk=1&version=1.5&folder_key=10ipmypb5ura9&response_format=json'
			rimages=get_images_mediafire(imagesPath)
			for item in rimages:
				imageName = item[0]
				imagePath = item[1]
				if not boxtype in imageName:
					continue
				images.append((imageName,imagePath))

		if self.teamName == "TeamBlue":
			imagesPath='https://www.mediafire.com/api/1.4/folder/get_content.php?r=cfgd&content_type=files&filter=all&order_by=name&order_direction=asc&chunk=1&version=1.5&folder_key=nzy14rrzawbw4&response_format=json'
			rimages=get_images_mediafire(imagesPath)
			for item in rimages:
				imageName = item[0]
				imagePath = item[1]
				if not boxtype in imageName:
					continue
				images.append((imageName,imagePath))

		if self.teamName == "OpenBH-Unoffical":
			imagesPath='https://www.mediafire.com/api/1.4/folder/get_content.php?r=cfgd&content_type=files&filter=all&order_by=name&order_direction=asc&chunk=1&version=1.5&folder_key=sdvi12arjgsuj&response_format=json'
			rimages=get_images_mediafire(imagesPath)
			for item in rimages:
				imageName = item[0]
				imagePath = item[1]
				if not boxtype in imageName:
					continue
				images.append((imageName,imagePath))

		if self.teamName == "ArEaDeLtA-SaT":
			imagesPath = "http://areadeltasat.net/upload/E2%20Images/Dreambox/"
			regx = b'''<font color="#ffffff"><b>(.*?)</b></font>.*?<a href="(.*?)" target="_blank">'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[0]
				if PY3:
					imageName = imageName.decode()
					imagePath = (item[1].decode()).replace(" ","%20")
				else:
					imagePath = item[1].replace(" ","%20")
				if not boxtype in imageName:
					continue
				images.append((imageName+".zip",imagePath))

		if self.teamName == "OpenESI": 
			imagesPath = "http://www.openesi.eu/images/index.php?dir=Dreambox/" +boxtype + "/"
			regx = b'''<a class="autoindex_a" href="(.*?)&amp;file=(.*?)">'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				if PY3:
					imageName = imageName.decode()
				imagePath="http://www.openesi.eu/images/Dreambox" + "/" + boxtype + "/" + imageName
				images.append((imageName,imagePath))

		if self.teamName == "DreamElite":
			if boxtype == "dm520" or boxtype == "dm525":
				boxtype='DM520-DM525'
			else:
				boxtype = boxtype.upper()
			imagesPath = "https://images.dream-elite.net/DEP/index.php?dir=" + boxtype + "/"
			regx = b'''<a class="autoindex_a" href="(.*?)&amp;file=(.*?)">'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				if PY3:
					imageName = imageName.decode()
				imagePath="https://images.dream-elite.net/DEP/"+boxtype.upper()+'/'+imageName
				images.append((imageName,imagePath.strip()))

		if self.teamName == "Dreamboxupdates-Stable":
			if boxtype == "dreamone" or boxtype == "dreamtwo":
				imagesPath = "http://www.dreamboxupdate.com/opendreambox/2.6/stable/images/"+boxtype+"/index.php"
			else:
				imagesPath = "http://www.dreamboxupdate.com/opendreambox/2.5/stable/images/"+boxtype+"/index.php"
			regx = b'''<a class="tarxz" href="(.*?)">(.*?)</a>'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				if PY3:
					imageName = imageName.decode()
				if boxtype == "dreamone" or boxtype == "dreamtwo":
					imagePath = os.path.join("http://www.dreamboxupdate.com/opendreambox/2.6/stable/images/"+boxtype+'/', imageName)
				else:
					imagePath = os.path.join("http://www.dreamboxupdate.com/opendreambox/2.5/stable/images/"+boxtype+'/', imageName)
				if "sig" in imageName:
					continue
				images.append((imageName,imagePath))

		if self.teamName == "Dreamboxupdates-UnStable":
			if boxtype == "dreamone" or boxtype == "dreamtwo":
				imagesPath = "http://www.dreamboxupdate.com/opendreambox/2.6/unstable/images/"+boxtype+"/index.php"
			else:
				imagesPath = "http://www.dreamboxupdate.com/opendreambox/2.5/unstable/images/"+boxtype+"/index.php"
			regx = b'''<a class="tarxz" href="(.*?)">(.*?)</a>'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				if PY3:
					imageName = imageName.decode()
				if boxtype == "dreamone" or boxtype == "dreamtwo":
					imagePath = os.path.join("http://www.dreamboxupdate.com/opendreambox/2.6/unstable/images/"+boxtype+'/', imageName)
				else:
					imagePath = os.path.join("http://www.dreamboxupdate.com/opendreambox/2.5/unstable/images/"+boxtype+'/', imageName)
				if "sig" in imageName:
					continue
				images.append((imageName,imagePath))

		if self.teamName == "Merlin4":
			if boxtype == "dreamone" or boxtype == "dreamtwo":
				imagesPath = "https://merlinfeed.boxpirates.to/images_oe_2.6/"
				regx = b'''<a href="/images_oe_2.6/(.*?)">(.*?)</a>'''
			else:
				imagesPath = "https://merlinfeed.boxpirates.to/images_oe_2.5/"
				regx = b'''<a href="/images_oe_2.5/(.*?)">(.*?)</a>'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				if PY3:
					imageName = imageName.decode()
				if boxtype == "dreamone" or boxtype == "dreamtwo":
					imagePath = os.path.join("https://merlinfeed.boxpirates.to/images_oe_2.6/", imageName)
				else:
					imagePath = os.path.join("https://merlinfeed.boxpirates.to/images_oe_2.5/", imageName)
				if not boxtype in imageName:
					continue
				images.append((imageName,imagePath))

		if self.teamName == "OoZooN":
			imagesPath = "http://www.oozoon-download.de/opendreambox/images/"+boxtype+"/unstable/index.html"
			regx = b'''<a href="(.*?)">(.*?)</a>'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				if PY3:
					imageName = imageName.decode()
				imagePath = os.path.join("http://www.oozoon-download.de/opendreambox/images/"+boxtype+"/unstable/", imageName)
				if ".nfo" in  imageName or not "oozoon" in imageName:
					continue
				images.append((imageName,imagePath))

		if self.teamName == "Newnigma2":
			imagesPath = "http://feed.newnigma2.to/daily/images/"
			regx = b'''<a href="(.*?)">(.*?)</a>'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				if PY3:
					imageName = imageName.decode()
				imagePath = os.path.join("http://feed.newnigma2.to/daily/images/", imageName)
				if not boxtype in imageName:
					continue
				images.append((imageName,imagePath))

		if self.teamName == "Demonisat":
			if boxtype == "dm520":
				boxtype = "520"
			elif boxtype == "dm820":
				boxtype = "820"
			elif boxtype == "dm900":
				boxtype = "900"
			elif boxtype == "dm920":
				boxtype = "920"
			elif boxtype == "dm7080":
				boxtype = "7080"
			elif boxtype == "dreamone":
				boxtype = "dreamone"
			elif boxtype == "dreamtwo":
				boxtype = "dreamtwo"
			else:
				pass
			if boxtype == "dreamone" or boxtype == "dreamtwo": 
				imagesPath = "http://demonisat.info/demonisat-e2Img-OE2.0/Image-OE2.6/"+boxtype+"/"
				regx = b'<a href="(.*?)">(.*?)..&gt;</a></td><td align="right">(.*?)  </td>'
			else:
				imagesPath = "http://demonisat.info/demonisat-e2Img-OE2.0/Image-oe2.5/"+boxtype+"/"
			regx = b'<a href="(.*?)">(.*?)-..&gt;</a></td><td align="right">(.*?)</td>'
			data = requests.get(imagesPath, headers=headers).content
			info = re.findall(regx, data)
			rimages = []
			for href, title, cdate in info:
				cdate = (cdate.decode("utf-8")).split(" ")[0]
				title = title.decode("utf-8") + "-" + cdate
				if PY3:
					title = imagesPath + href.decode("utf-8")
					rimages.append((href.decode("utf-8"), title))
				else:
					title = imagesPath + href
					rimages.append((href, title))
			images = []
			for item in rimages:
				imageName = item[0]
				imagePath = item[1]
				images.append((imageName,imagePath))

		if self.teamName == "Powersat":
			imagesPath = "http://www.power-sat.org/power-plus/index.php?dir=Powersat_2.5/immagini_powersat_"+boxtype+"_OE2.5/"
			regx = b'''<a class="autoindex_a" href="(.*?)&amp;file=(.*?)">'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				if PY3:
					imageName = imageName.decode()
				imagePath = os.path.join("http://www.power-sat.org/power-plus/Powersat_2.5/immagini_powersat_"+boxtype+"_OE2.5/", imageName)
				if not boxtype in imageName:
					continue
				images.append((imageName,imagePath))

		if self.teamName == "Satlodge":
			if boxtype == "dreamone" or boxtype == "dreamtwo":
				imagesPath = "http://webplus.sat-lodge.it/index.php?dir=dreamone2.6/"
			else:
				imagesPath = "http://webplus.sat-lodge.it/index.php?dir=Satlodge%202.5/"
			regx = b'''<a class="autoindex_a" href="(.*?)&amp;file=(.*?)">'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				if PY3:
					imageName = imageName.decode()
				if boxtype == "dreamone" or boxtype == "dreamtwo":
					imagePath = os.path.join('http://webplus.sat-lodge.it/dreamone2.6/', imageName)
				else:
					imagePath = os.path.join('http://webplus.sat-lodge.it/Satlodge%202.5/', imageName)
				if not boxtype in imageName:
					continue
				images.append((imageName,imagePath))

		if self.teamName == "OpenSatlodge":
			imagesPath = "http://webplus.sat-lodge.it/index.php?dir=Dreambox920/"
			regx = b'''<a class="autoindex_a" href="(.*?)&amp;file=(.*?)">'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				if PY3:
					imageName = imageName.decode()
				imagePath = os.path.join('http://webplus.sat-lodge.it/Dreambox920/', imageName)
				if not item[1].endswith(b"unstable.tar.bz2"):
					continue
				images.append((imageName,imagePath))

		if self.teamName == "PurE2":
			if boxtype == "dreamone" or boxtype == "dreamtwo":
				imagesPath = "https://www.pur-e2.club/OU/images/index.php?dir=6.5/dreambox/TEST-alpha/"
			elif boxtype == "dm900" or boxtype == "dm920":
				imagesPath = "https://www.pur-e2.club/OU/images/index.php?dir=7.4/dreambox/"
			else:
				imagesPath = "https://www.pur-e2.club/OU/images/index.php?dir=6.5/dreambox/"
			regx = b'''<a class="autoindex_a" href="(.*?)&amp;file=(.*?)">'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				if PY3:
					imageName = imageName.decode()
				if boxtype == "dreamone" or boxtype == "dreamtwo":
					imagePath = os.path.join('https://www.pur-e2.club/OU/images/6.5/dreambox/TEST-alpha/', imageName)
				elif boxtype == "dm900" or boxtype == "dm920":
					imagePath = os.path.join('https://www.pur-e2.club/OU/images/7.4/dreambox/', imageName)
				else:
					imagePath = os.path.join('https://www.pur-e2.club/OU/images/6.5/dreambox/', imageName)
				if boxtype == "dreamone" or boxtype == "dreamtwo":
					if not boxtype in imageName:
						continue
				if boxtype == "dm900" or boxtype == "dm920":
					if "mmc.zip" in imageName or not boxtype in imageName:
						continue
				if boxtype == "dm520" or boxtype == "dm820":
					if "web.zip" in imageName or not boxtype in imageName:
						continue
				images.append((imageName,imagePath))

		if self.teamName == "PKTeam":
			imagesPath = "http://e2.pkteam.pl/index.php?dir=IMAGE%20DREAMBOX/HYPERION%206.1/"
			regx = b'''<a class="autoindex_a" href="(.*?)&amp;file=(.*?)">'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				if PY3:			     
					imageName = imageName.decode()
				imagePath = os.path.join("http://e2.pkteam.pl/IMAGE%20DREAMBOX/HYPERION%206.1/", imageName)
				if not boxtype in imageName:
					continue
				images.append((imageName,imagePath))

		if self.teamName == "AFF-TitanNit":
			if boxtype == "dm520":
				boxtype = 'DM520'
			elif boxtype == "dm900":
				boxtype = 'DM900'
			elif boxtype == "dm920":
				boxtype = 'DM920'
			else:
				pass
			imagesPath = "http://atemio.dyndns.tv/nightly-images/Dreambox/"+boxtype+"/v2.04/"
			regx = b'''<a href="(.*?)">(.*?)</a>'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				if PY3:
					imageName = imageName.decode()
				imagePath = os.path.join("http://atemio.dyndns.tv/nightly-images/Dreambox/"+boxtype+"/v2.04/", imageName)
				if not item[0].endswith(b".zip"):
					continue
				images.append((imageName,imagePath))

		if self.teamName == "Gemini4":
			if boxtype == "dreamone" or boxtype == "dreamtwo":
				imagesPath = "https://download.blue-panel.com/pyro/gemini4-unstable/developer/images/"
			else:
				imagesPath = "https://download.blue-panel.com/gemini4/krogoth-gemini4-unstable/developer/images/"
			regx = b'''<a href="(.*?)" class="xz" download='(.*?)'>'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				if PY3:
					imageName = imageName.decode()
				if boxtype == "dreamone" or boxtype == "dreamtwo":
					imagePath = os.path.join('https://download.blue-panel.com/pyro/gemini4-unstable/developer/images/', imageName)
				else:
					imagePath = os.path.join('https://download.blue-panel.com/gemini4/krogoth-gemini4-unstable/developer/images/', imageName)
				# Skip if boxtype not in filename
				if boxtype not in imageName:
					continue
				images.append((imageName,imagePath))

		if self.teamName == "OpenVision":
			imagesPath = "https://images.openvision.dedyn.io/13.1/Develop/Vision/Dreambox/"+boxtype+"/"
			regx = ('''<a href="/13.1/Develop/Vision/Dreambox/%s/(.*?)">(.*?)</a>''' % boxtype).encode()
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				if PY3:
					imageName = imageName.decode()
				imagePath = os.path.join("https://images.openvision.dedyn.io/13.1/Develop/Vision/Dreambox/"+boxtype+"/", imageName)
				if not item[0].endswith(b".zip"):
					continue
				images.append((imageName,imagePath))

		if self.teamName == "OpenHDF":
			imagesPath = "http://v7.hdfreaks.cc/" + boxtype + "/"
			regx = b'''<a href="(.*?)">(.*?)</a>'''
			rimages = get_images(imagesPath,regx)
			for item in rimages:
				imageName = item[1]
				if PY3:
					imageName = imageName.decode()
				imagePath = os.path.join("http://v7.hdfreaks.cc/" + boxtype + "/", imageName)
				if not item[0].endswith(b".zip"):
					continue
				images.append((imageName, imagePath))

		if self.teamName == "NonSoloSat":
			imagesPath = "https://www.nonsolosat.net/upload/index.php?dir=Dreambox/Nonsolosat%2028/&file="
			regx = b'''<a class="autoindex_a" href="(.*?)&amp;file=(.*?)">'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				if PY3:
					imageName = imageName.decode()
				imagePath = os.path.join('https://www.nonsolosat.net/upload/Image-Nonsolosat/Dreambox/Nonsolosat%2028/', imageName)
				if not boxtype in imageName:
					continue
				images.append((imageName,imagePath))

		if self.teamName == "Open-cobralibero":
			imagesPath = "https://cobraliberosat.net/UPLOAD/index.php?dir=Dreambox/20.09.2023/"
			regx = b'''<a class="autoindex_a" href="(.*?)&amp;file=(.*?)">'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				if PY3:
					imageName = imageName.decode()
				imagePath = os.path.join('https://cobraliberosat.net/UPLOAD/IMAGE-COBRALIBEROSAT/Dreambox/20.09.2023/', imageName)
				if not boxtype in imageName:
					continue
				images.append((imageName,imagePath))

		if self.teamName == "BPanther":
			imagesPath = "https://%s.mbremer.de/FLASH/" % boxtype
			regx = b'''<a href="(.*?)">(.*?)</a>.*?Neutrino Image'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[1]
				if PY3:
					imageName = imageName.decode()
				imagePath = os.path.join('https://'+ boxtype +'.mbremer.de/FLASH/', imageName)
				images.append((imageName,imagePath))

		if self.teamName == "OpenVIX":
			imagesPath = "https://www.openvix.co.uk/openvix-builds/%s/" % boxtype
			regx = b'''<a href="(.*?)">(.*?).rele..&gt;</a>'''
			rimages = get_images(imagesPath, regx)
			for item in rimages:
				imageName = item[0]
				if PY3:
					imageName = imageName.decode()
				imagePath = os.path.join('https://www.openvix.co.uk/openvix-builds/'+ boxtype +'/', imageName)
				images.append((imageName,imagePath))

		if self.teamName == "OpenVIX-Unoffical":
			imagesPath='https://www.mediafire.com/api/1.4/folder/get_content.php?r=cfgd&content_type=files&filter=all&order_by=name&order_direction=asc&chunk=1&version=1.5&folder_key=q1ds8bogfa994&response_format=json'
			rimages=get_images_mediafire(imagesPath)
			for item in rimages:
				imageName = item[0]
				imagePath = item[1]
				if not boxtype in imageName:
					continue
				images.append((imageName,imagePath))

		if self.teamName == "OpenDroid":
			imagesPath = "https://opendroid.org/8.0/Dreambox/index.php?open=%s" % boxtype
			#logdata("imagesPath",imagesPath)
			regx = b'''<a href='.*?/(.*?)'>(.*?)</a><br>'''
			rimages = get_images(imagesPath, regx)
			#logdata("rimages",rimages)
			for item in rimages:
				imageName = item[0]
				if PY3:
					imageName = imageName.decode()
				imagePath = os.path.join('https://opendroid.org/8.0/Dreambox/%s/' % boxtype, imageName)
				images.append((imageName,imagePath))

		return images

	def download(self):
		idx = self['list'].getSelectionIndex()
		imageLink = self.images[idx][1]
		IMAGENAME = self.images[idx][0]
		IMAGEPATH = os.path.join(self.device_path,IMAGENAME)
		logdata("imageLink", imageLink)
		logdata("IMAGENAME", IMAGENAME)
		logdata("IMAGEPATH", IMAGEPATH)
		self.session.openWithCallback(self.downloadback, imagedownloadScreen, IMAGENAME, imageLink, IMAGEPATH, self.canflash)

	def downloadback(self,success):
		#if success:
		#	self.doFlash()
		#else:
		#	pass
		pass

	def doFlash(self):
		k=open("/proc/cmdline","r")
		cmd=k.read()
		k.close()
		boxtype =getboxtype()
		if boxtype == "dm520":
				if cmd.find("root=/dev/sda1") != -1:
						rootfs="root=/dev/sda1"
				else:
						rootfs="root=ubi0:dreambox-rootfs"
		else:
				rootfs="root=/dev/mmcblk0"
		if not config.backupflashe.flashAllow.value and (os.path.exists("/.bainfo") or os.path.exists("/.lfinfo") or cmd.find(rootfs) == -1):
			self.session.open(MessageBox, "You Disable To flash new image from External image.\nSo Flashing works only in Flash image", MessageBox.TYPE_ERROR)
		#if os.path.exists("/.bainfo"):
				#self.session.open(MessageBox, "Sorry, Flashing works only in Flash image", MessageBox.TYPE_ERROR)
		#elif os.path.exists("/.lfinfo"):
		#        self.session.open(MessageBox, "Sorry, Flashing works only in Flash image", MessageBox.TYPE_ERROR)
		#elif cmd.find(rootfs) == -1:
		#        self.session.open(MessageBox, "Sorry, Flashing works only in Flash image", MessageBox.TYPE_ERROR)
		else:
			from Plugins.Extensions.backupflashe.tools.flash import flashScript
			if self.imageok == False:
					return
			mytitle = _('Do Flash Images')
			idx = self['list'].getSelectionIndex()
			imageLink = self.images[idx][1]
			IMAGENAME = os.path.split(imageLink)[1]
			IMAGEPATH =self.device_path+IMAGENAME
			command=flashScript(IMAGENAME,self.device_path)
			script_backupflash="/tmp/backupflash.sh"
			self.session.open(Console, title=mytitle, cmdlist=[script_backupflash])
			copylog(self.device_path)
