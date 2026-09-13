#!/usr/bin/python
# -*- coding: utf-8 -*-
# RAED (c) 2026

import os
import datetime

from twisted.web import server, resource
from twisted.internet import reactor

from Components.config import config, configfile, ConfigSelection
from Tools.Directories import fileExists

from .bftools import getmDevices, getimage_name, getboxtype, logfile
from .backup import doBackUpInternal, doBackUpExternal
from .convert import doConvert
from .flashonline import teamsScreen, imagesScreen
from .download import imagedownloadScreen
from enigma import quitMainloop

try:
	from urllib.parse import quote
except ImportError:
	from urllib import quote

import socket

WEBPORT = 1001

boxtype = getboxtype()


def getLocalIP():
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		ip = s.getsockname()[0]
		s.close()
		return ip
	except:
		return "127.0.0.1"

_session = None


def setWebSession(session):
	global _session
	_session = session


def getDateTime():
	return datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')


def getCompressionValue():
	if config.backupflashe.image_format.value == "xz":
		return config.backupflashe.xzcompression.value
	else:
		return config.backupflashe.bz2compression.value


def ensureDevicePathConfig():
	if not hasattr(config.backupflashe, 'device_path'):
		devices = getmDevices()
		config.backupflashe.device_path = ConfigSelection(choices=devices if devices else [("", "")])
	return config.backupflashe.device_path


def detectExternalImagesPath():
	if os.path.isdir("/media/ba/ba"):
		return "/media/ba/ba"
	if os.path.isdir("/media/at"):
		return "/media/at"
	if os.path.isdir("/media/egamiboot/EgamiBootI"):
		return "/media/egamiboot/EgamiBootI"
	if fileExists("/proc/mounts"):
		for line in open("/proc/mounts"):
			if "/dev/sd" in line or "/dev/disk/by-uuid/" in line or "/dev/mmc" in line:
				parts = line.split()[1].replace("\\040", " ").split(",")
				for dirName in parts:
					if os.path.isdir(dirName + "/open-multiboot"):
						return dirName + "/open-multiboot"
					elif os.path.isdir(dirName + "/ImageBoot"):
						return dirName + "/ImageBoot"
	return ""


def getCategoryList():
	cats = []
	if boxtype in ("dreamone", "dreamtwo"):
		cats.append(('aio', 'DreamOS AIO Images'))
	cats.append(('dreamos', 'DreamOS OE2.5 Images'))
	cats.append(('opensource', 'Open Source OE2.0 Images'))
	cats.append(('neutrino', 'Neutrino Images'))
	return cats


def fetchTeamsList(category):
	method_map = {'aio': 'AIO', 'dreamos': 'DreamOS', 'opensource': 'opensource', 'neutrino': 'neutrino'}
	methodname = method_map.get(category)
	if not methodname:
		return []
	helper = teamsScreen.__new__(teamsScreen)
	try:
		return getattr(helper, methodname)()
	except:
		return []


def fetchTeamImages(teamKey):
	helper = imagesScreen.__new__(imagesScreen)
	helper.teamName = teamKey
	try:
		return helper.getteam_images()
	except:
		return []


PAGE_HEAD = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BackUpFlash</title>
<style>
body { font-family: sans-serif; background:#111; color:#eee; padding:20px; max-width:700px; margin:0 auto; }
h1 { color:#0af; }
h2 { color:#0af; border-bottom:1px solid #333; padding-bottom:5px; }
select, input[type=text], button { padding:8px; font-size:14px; margin:5px 0; width:100%%; box-sizing:border-box; }
button { background:#0af; color:#fff; border:none; cursor:pointer; border-radius:4px; }
pre { background:#000; color:#0f0; padding:10px; height:400px; overflow:auto; }
a { color:#0af; text-decoration:none; }
.nav { margin-bottom:20px; }
.nav a { margin-right:15px; }
.item { border-bottom:1px solid #333; padding:8px 0; display:flex; justify-content:space-between; align-items:center; }
label { display:block; margin-top:10px; color:#aaa; }
</style>
</head>
<body>
<h1>BackUpFlash</h1>
<div class="nav">
<a href="/">%s</a>
<a href="/backup">%s</a>
<a href="/convert">%s</a>
<a href="/download">%s</a>
<a href="/recovery">%s</a>
<a href="/settings">%s</a>
<a href="/log">%s</a>
</div>
""" % (_('Home'), _('Backup'), _('Convert'), _('Download'), _('Recovery'), _('Settings'), _('Log'))

PAGE_FOOT = """
</body>
</html>
"""


class HomePage(resource.Resource):
	isLeaf = True

	def render_GET(self, request):
		html = PAGE_HEAD
		html += '<p>%s</p>' % _('Welcome. Use the menu above to Backup, Convert, change Settings, or view the Log.')
		html += PAGE_FOOT
		return html.encode('utf-8')


class BackupPage(resource.Resource):
	isLeaf = True

	def render_GET(self, request):
		action = request.args.get(b'action', [b''])[0].decode('utf-8')
		if action == 'internal':
			return self.runInternal(request)
		if action == 'external':
			return self.runExternal(request)
		return self.showForm(request)

	def showForm(self, request):
		devices = getmDevices()
		dev_options = ''.join(['<option value="%s">%s</option>' % (d[0], d[0]) for d in devices])
		if not dev_options:
			dev_options = '<option value="">%s</option>' % _('No device found')
		default_name = '%s-%s-%s' % (getimage_name(), boxtype, getDateTime())

		html = PAGE_HEAD
		html += '<h2>%s</h2>' % _('Backup Current (Internal) Image')
		html += '<form action="/backup" method="get">'
		html += '<input type="hidden" name="action" value="internal">'
		html += '<label>%s</label><input type="text" name="name" value="%s">' % (_('Backup name'), default_name)
		html += '<label>%s</label><select name="device">%s</select>' % (_('Target device'), dev_options)
		html += '<button type="submit">%s</button>' % _('Start Internal Backup')
		html += '</form>'

		image_path = detectExternalImagesPath()
		if image_path:
			try:
				files = sorted([f for f in os.listdir(image_path) if not f.startswith('.')])
			except:
				files = []
			file_options = ''.join(['<option value="%s">%s</option>' % (f, f) for f in files])
			if not file_options:
				file_options = '<option value="">%s</option>' % _('No image found')
			html += '<h2>%s</h2>' % _('Backup External Image')
			html += '<form action="/backup" method="get">'
			html += '<input type="hidden" name="action" value="external">'
			html += '<label>%s</label><select name="source">%s</select>' % (_('Source image'), file_options)
			html += '<label>%s</label><input type="text" name="name" value="%s">' % (_('Backup name'), default_name)
			html += '<label>%s</label><select name="device">%s</select>' % (_('Target device'), dev_options)
			html += '<button type="submit">%s</button>' % _('Start External Backup')
			html += '</form>'

		html += PAGE_FOOT
		return html.encode('utf-8')

	def runInternal(self, request):
		name = request.args.get(b'name', [b''])[0].decode('utf-8').strip()
		device = request.args.get(b'device', [b''])[0].decode('utf-8')
		html = PAGE_HEAD
		if not name or not device:
			html += '<p>%s</p>' % _('Name and device are required.')
		elif _session is None:
			html += '<p>%s</p>' % _('Session not ready yet, try again in a moment.')
		else:
			configfile.save()
			_session.open(doBackUpInternal, name, device, getCompressionValue())
			html += '<p>%s %s</p>' % (_('Internal backup started on:'), device)
		html += '<p><a href="/log">%s</a></p>' % _('View live log')
		html += PAGE_FOOT
		return html.encode('utf-8')

	def runExternal(self, request):
		source = request.args.get(b'source', [b''])[0].decode('utf-8')
		name = request.args.get(b'name', [b''])[0].decode('utf-8').strip()
		device = request.args.get(b'device', [b''])[0].decode('utf-8')
		image_path_base = detectExternalImagesPath()
		html = PAGE_HEAD
		if not source or not name or not device or not image_path_base:
			html += '<p>%s</p>' % _('Source image, name and device are required.')
		elif _session is None:
			html += '<p>%s</p>' % _('Session not ready yet, try again in a moment.')
		else:
			image_path = image_path_base + "/" + source
			_session.open(doBackUpExternal, name, image_path, device, getCompressionValue())
			html += '<p>%s %s</p>' % (_('External backup started on:'), device)
		html += '<p><a href="/log">%s</a></p>' % _('View live log')
		html += PAGE_FOOT
		return html.encode('utf-8')


class ConvertPage(resource.Resource):
	isLeaf = True

	def render_GET(self, request):
		device = request.args.get(b'device', [b''])[0].decode('utf-8')
		run_name = request.args.get(b'run', [b''])[0].decode('utf-8')
		if run_name and device:
			return self.runConvert(request, device, run_name)
		if device:
			return self.showFiles(request, device)
		return self.showDevices(request)

	def showDevices(self, request):
		devices = getmDevices()
		html = PAGE_HEAD
		html += '<h2>%s</h2>' % _('Select device to convert images from')
		if not devices:
			html += '<p>%s</p>' % _('No device found')
		else:
			for d in devices:
				html += '<div class="item"><span>%s</span><a href="/convert?device=%s">%s</a></div>' % (d[0], d[0], _('Open'))
		html += PAGE_FOOT
		return html.encode('utf-8')

	def showFiles(self, request, device):
		try:
			files = sorted([f for f in os.listdir(device) if f.endswith('.xz')])
		except:
			files = []
		html = PAGE_HEAD
		html += '<h2>%s: %s</h2>' % (_('Images on'), device)
		if not files:
			html += '<p>%s</p>' % _('No .xz images found on this device.')
		for f in files:
			html += '<div class="item"><span>%s</span><a href="/convert?device=%s&run=%s">%s</a></div>' % (f, device, f, _('Convert'))
		html += '<p><a href="/convert">%s</a></p>' % _('Back to devices')
		html += PAGE_FOOT
		return html.encode('utf-8')

	def runConvert(self, request, device, name):
		html = PAGE_HEAD
		if _session is None:
			html += '<p>%s</p>' % _('Session not ready yet, try again in a moment.')
		else:
			_session.open(doConvert, device, name)
			html += '<p>%s %s</p>' % (_('Convert started for:'), name)
		html += '<p><a href="/log">%s</a></p>' % _('View live log')
		html += PAGE_FOOT
		return html.encode('utf-8')


class RecoveryPage(resource.Resource):
	isLeaf = True

	def render_GET(self, request):
		confirm = request.args.get(b'confirm', [b''])[0].decode('utf-8')
		if confirm == '1':
			return self.doReboot(request)
		html = PAGE_HEAD
		html += '<h2>%s</h2>' % _('Recovery Mode')
		html += '<p>%s</p>' % _('This will reboot the receiver into Recovery Mode now.')
		html += '<form action="/recovery" method="get">'
		html += '<input type="hidden" name="confirm" value="1">'
		html += '<button type="submit">%s</button>' % _('Reboot to Recovery Mode')
		html += '</form>'
		html += PAGE_FOOT
		return html.encode('utf-8')

	def doReboot(self, request):
		try:
			b = open("/proc/stb/fp/boot_mode", "w")
			b.write("rescue")
			b.close()
		except:
			pass
		html = PAGE_HEAD
		html += '<p>%s</p>' % _('Rebooting into Recovery Mode...')
		html += PAGE_FOOT
		reactor.callLater(1, quitMainloop, 2)
		return html.encode('utf-8')


class DownloadPage(resource.Resource):
	isLeaf = True

	def render_GET(self, request):
		def arg(key):
			return request.args.get(key.encode('utf-8'), [b''])[0].decode('utf-8')

		category = arg('category')
		team = arg('team')
		name = arg('name')
		link = arg('link')
		device = arg('device')
		run = arg('run')

		if name and link and device and run == '1':
			return self.runDownload(name, link, device)
		if name and link:
			return self.showDeviceForm(name, link)
		if category and team:
			return self.showImages(category, team)
		if category:
			return self.showTeams(category)
		return self.showCategories()

	def showCategories(self):
		html = PAGE_HEAD
		html += '<h2>%s</h2>' % _('Select image category')
		for key, label in getCategoryList():
			html += '<div class="item"><span>%s</span><a href="/download?category=%s">%s</a></div>' % (label, key, _('Open'))
		html += PAGE_FOOT
		return html.encode('utf-8')

	def showTeams(self, category):
		teams = fetchTeamsList(category)
		html = PAGE_HEAD
		html += '<h2>%s</h2>' % _('Select team')
		if not teams:
			html += '<p>%s</p>' % _('No teams available for this category on your device.')
		for tname, tkey in teams:
			html += '<div class="item"><span>%s</span><a href="/download?category=%s&team=%s">%s</a></div>' % (tname, category, quote(tkey), _('Open'))
		html += '<p><a href="/download">%s</a></p>' % _('Back to categories')
		html += PAGE_FOOT
		return html.encode('utf-8')

	def showImages(self, category, team):
		images = fetchTeamImages(team)
		html = PAGE_HEAD
		html += '<h2>%s: %s</h2>' % (_('Images for'), team)
		if not images:
			html += '<p>%s</p>' % _('Unable to get images, internet down or server unresponsive.')
		for item in images:
			iname, ilink = item[0], item[1]
			html += '<div class="item"><span>%s</span><a href="/download?category=%s&team=%s&name=%s&link=%s">%s</a></div>' % (
				iname, category, quote(team), quote(iname), quote(ilink, safe=''), _('Select'))
		html += '<p><a href="/download?category=%s">%s</a></p>' % (category, _('Back to teams'))
		html += PAGE_FOOT
		return html.encode('utf-8')

	def showDeviceForm(self, name, link):
		devices = getmDevices()
		dev_options = ''.join(['<option value="%s">%s</option>' % (d[0], d[0]) for d in devices])
		if not dev_options:
			dev_options = '<option value="">%s</option>' % _('No device found')
		html = PAGE_HEAD
		html += '<h2>%s: %s</h2>' % (_('Download'), name)
		html += '<form action="/download" method="get">'
		html += '<input type="hidden" name="name" value="%s">' % name
		html += '<input type="hidden" name="link" value="%s">' % link
		html += '<input type="hidden" name="run" value="1">'
		html += '<label>%s</label><select name="device">%s</select>' % (_('Target device'), dev_options)
		html += '<button type="submit">%s</button>' % _('Start Download')
		html += '</form>'
		html += PAGE_FOOT
		return html.encode('utf-8')

	def runDownload(self, name, link, device):
		html = PAGE_HEAD
		if _session is None:
			html += '<p>%s</p>' % _('Session not ready yet, try again in a moment.')
		else:
			imagePath = os.path.join(device, name)
			_session.open(imagedownloadScreen, name, link, imagePath, True)
			html += '<p>%s %s</p>' % (_('Download started:'), name)
		html += '<p><a href="/log">%s</a></p>' % _('View live log')
		html += PAGE_FOOT
		return html.encode('utf-8')


class SettingsPage(resource.Resource):
	isLeaf = True

	def render_GET(self, request):
		if request.args.get(b'save', [b''])[0] == b'1':
			return self.saveSettings(request)
		return self.showForm(request)

	def showForm(self, request):
		device_path_conf = ensureDevicePathConfig()
		devices = getmDevices()
		dev_options = ''.join(['<option value="%s"%s>%s</option>' % (d[0], ' selected' if d[0] == device_path_conf.value else '', d[0]) for d in devices]) if devices else ''

		def yesno_options(current):
			return '<option value="1"%s>%s</option><option value="0"%s>%s</option>' % (
				' selected' if current else '', _('Yes'),
				' selected' if not current else '', _('No'))

		fmt_options = ''.join(['<option value="%s"%s>%s</option>' % (v, ' selected' if v == config.backupflashe.image_format.value else '', v) for v in ('xz', 'bz2')])

		max_level = 4 if boxtype == "dm520" else 6
		xz_opts = ''.join(['<option value="%s"%s>%s</option>' % (i, ' selected' if str(i) == config.backupflashe.xzcompression.value else '', i) for i in range(1, max_level + 1)])

		html = PAGE_HEAD
		html += '<h2>%s</h2>' % _('Settings')
		html += '<form action="/settings" method="get">'
		html += '<input type="hidden" name="save" value="1">'
		html += '<label>%s</label><select name="device_path">%s</select>' % (_('Path to store Full Backup'), dev_options)
		html += '<label>%s</label><select name="update">%s</select>' % (_('Enable online update'), yesno_options(config.backupflashe.update.value))
		html += '<label>%s</label><select name="image_format">%s</select>' % (_('Compression format'), fmt_options)
		html += '<label>%s</label><select name="xzcompression">%s</select>' % (_('xz compression level'), xz_opts)
		html += '<label>%s</label><select name="zipcompression">%s</select>' % (_('Compress image as Zip'), yesno_options(config.backupflashe.Zipcompression.value))
		html += '<label>%s</label><select name="shutdown">%s</select>' % (_('Shutdown box after backup'), yesno_options(config.backupflashe.shutdown.value))
		html += '<label>%s</label><select name="cleanba">%s</select>' % (_('Clean BarryAllen symlink before backup'), yesno_options(config.backupflashe.cleanba.value))
		html += '<button type="submit">%s</button>' % _('Save Settings')
		html += '</form>'
		html += PAGE_FOOT
		return html.encode('utf-8')

	def saveSettings(self, request):
		device_path_conf = ensureDevicePathConfig()

		def arg(key, default=b''):
			return request.args.get(key.encode('utf-8'), [default])[0].decode('utf-8')

		device_path = arg('device_path')
		if device_path:
			device_path_conf.value = device_path
		config.backupflashe.update.value = (arg('update') == '1')
		config.backupflashe.image_format.value = arg('image_format') or config.backupflashe.image_format.value
		config.backupflashe.xzcompression.value = arg('xzcompression') or config.backupflashe.xzcompression.value
		config.backupflashe.Zipcompression.value = (arg('zipcompression') == '1')
		config.backupflashe.shutdown.value = (arg('shutdown') == '1')
		config.backupflashe.cleanba.value = (arg('cleanba') == '1')

		device_path_conf.save()
		for entry in (config.backupflashe.update, config.backupflashe.image_format, config.backupflashe.xzcompression,
					  config.backupflashe.Zipcompression, config.backupflashe.shutdown, config.backupflashe.cleanba):
			entry.save()
		configfile.save()

		html = PAGE_HEAD
		html += '<p>%s</p>' % _('Settings saved.')
		html += PAGE_FOOT
		return html.encode('utf-8')


class LogPage(resource.Resource):
	isLeaf = True

	def render_GET(self, request):
		try:
			f = open(logfile, 'r')
			content = f.read()
			f.close()
		except:
			content = _('No log yet.')
		html = PAGE_HEAD
		html += '<meta http-equiv="refresh" content="3">'
		html += '<pre>%s</pre>' % content
		html += PAGE_FOOT
		return html.encode('utf-8')


def startWebServer():
	root = resource.Resource()
	root.putChild(b'', HomePage())
	root.putChild(b'backup', BackupPage())
	root.putChild(b'convert', ConvertPage())
	root.putChild(b'recovery', RecoveryPage())
	root.putChild(b'download', DownloadPage())
	root.putChild(b'settings', SettingsPage())
	root.putChild(b'log', LogPage())
	site = server.Site(root)
	reactor.listenTCP(WEBPORT, site)
