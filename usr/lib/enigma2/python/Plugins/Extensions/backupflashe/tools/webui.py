#!/usr/bin/python
# -*- coding: utf-8 -*-
# RAED (c) 2026

from __future__ import unicode_literals

import os
import datetime

from twisted.web import server, resource
from twisted.internet import reactor

from enigma import quitMainloop
from Components.config import config, configfile, ConfigSelection
from Tools.Directories import fileExists

from .bftools import getmDevices, getimage_name, getboxtype, logfile
from .backup import doBackUpInternal, doBackUpExternal
from .convert import doConvert
from .flashonline import teamsScreen, imagesScreen
from .download import imagedownloadScreen


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


def getConfiguredDevicePath():
	device_path_conf = ensureDevicePathConfig()
	return device_path_conf.value


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
<title>BackupFlash</title>
<style>
* { box-sizing:border-box; }
body {
	font-family: 'Segoe UI', sans-serif;
	margin:0;
	min-height:100vh;
	color:#eee;
	background: linear-gradient(135deg, #1e3c72 0%, #2a5298 40%, #0f2027 100%);
	background-attachment: fixed;
	padding:30px 15px 60px;
}
.wrap {
	max-width:900px;
	margin:0 auto;
	padding:25px 30px;
	background: rgba(255,255,255,0.08);
	backdrop-filter: blur(16px);
	-webkit-backdrop-filter: blur(16px);
	border: 1px solid rgba(255,255,255,0.15);
	border-radius: 18px;
	box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.header { display:flex; justify-content:space-between; align-items:flex-start; border-bottom:1px solid #333; padding-bottom:15px; margin-bottom:15px; }
.header h1 { margin:0; font-size:28px; font-weight:normal; color:#fff; }
.header .clock { text-align:right; }
.header .clock .time { font-size:34px; color:#fff; }
.header .clock .date { font-size:16px; color:#3584ba; }
.nav { margin-bottom:25px; display:flex; gap:20px; flex-wrap:wrap; }
.nav a { color:#0af; text-decoration:none; font-size:15px; }
.nav a:hover { text-decoration:underline; }
h2 { color:#0af; border-bottom:1px solid #333; padding-bottom:5px; }
select, input[type=text], button { padding:8px; font-size:14px; margin:5px 0; width:100%; background:rgba(255,255,255,0.08); color:#eee; border:1px solid rgba(255,255,255,0.2); border-radius:8px; backdrop-filter: blur(4px); }
select option { background:#1e2a3a; color:#eee; }
button { background:#0af; color:#fff; border:none; cursor:pointer; margin-top:30px; display:block; }
pre { background:#000; color:#0f0; padding:10px; height:400px; overflow:auto; border-radius:4px; }
a { color:#0af; }
.item { border-bottom:1px solid #333; padding:8px 0; display:flex; justify-content:space-between; align-items:center; }
label { display:block; margin-top:10px; color:#aaa; }
.grid { display:flex; flex-wrap:wrap; gap:30px; justify-content:center; margin-top:30px; }
.tile { display:flex; flex-direction:column; align-items:center; text-decoration:none; width:130px; }
.tile .icon { width:100px; height:100px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:44px; margin-bottom:10px; border:3px solid transparent; }
.tile:hover .icon { border-color:#0af; }
.tile .label { color:#fff; font-size:16px; text-align:center; }
.footer { position:fixed; bottom:0; left:0; right:0; background:#000c; padding:10px 20px; font-size:14px; color:#0f0; display:flex; justify-content:space-between; align-items:center; }
.footer select { width:auto; margin:0; padding:4px 8px; font-size:13px; }
</style>
<script>
function tick() {
	var d = new Date();
	var hh = ('0'+d.getHours()).slice(-2);
	var mm = ('0'+d.getMinutes()).slice(-2);
	document.getElementById('clocktime').textContent = hh+':'+mm;
	var days=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
	var months=['January','February','March','April','May','June','July','August','September','October','November','December'];
	document.getElementById('clockdate').textContent = days[d.getDay()]+' '+d.getDate()+' '+months[d.getMonth()]+' '+d.getFullYear();
}
setInterval(tick, 1000);
window.onload = tick;
</script>
</head>
<body>
<div class="wrap">
<div class="header">
<h1><a href="/" style="color:#fff; text-decoration:none;">🏠</a> BackupFlash</h1>
<div class="clock"><div class="time" id="clocktime">--:--</div><div class="date" id="clockdate"></div></div>
</div>
"""

PAGE_FOOT = """
</div>
<div class="footer">
<select id="fontsize" onchange="setFontSize(this.value)">
<option value="85">%s</option>
<option value="100">%s</option>
<option value="115">%s</option>
<option value="130">%s</option>
</select>
<span>BackupFlash Web UI</span>
</div>
<script>
function setFontSize(val) {
	document.body.style.zoom = val + "%%";
	localStorage.setItem('bf_fontsize', val);
}
(function() {
	var saved = localStorage.getItem('bf_fontsize') || '100';
	document.getElementById('fontsize').value = saved;
	setFontSize(saved);
})();
</script>
</body>
</html>
""" % (_('Small'), _('Normal'), _('Large'), _('Extra Large'))


class HomePage(resource.Resource):
	isLeaf = True

	def render_GET(self, request):
		tiles = [
			('/backup', '💾', _('Backup Image'), '#3d5a66'),
			('/convert', '🔄', _('Convert Image'), '#2e2e2e'),
			('/download', '⬇️', _('Download Image'), '#1596c7'),
			('/recovery', '♻️', _('Recovery Mode'), '#2e2e2e'),
			('/settings', '⚙️', _('Setup'), '#2e2e2e'),
			('/log', '📄', _('Log'), '#555555'),
		]
		html = PAGE_HEAD
		html += '<div class="grid">'
		for href, icon, label, color in tiles:
			html += '<a class="tile" href="%s"><div class="icon" style="background:%s">%s</div><div class="label">%s</div></a>' % (href, color, icon, label)
		html += '</div>'
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
		device = getConfiguredDevicePath()
		default_name = '%s-%s-%s' % (getimage_name(), boxtype, getDateTime())

		html = PAGE_HEAD
		if not device:
			html += '<p>%s <a href="/settings">%s</a></p>' % (_('No storage path configured.'), _('Go to Settings'))
			html += PAGE_FOOT
			return html.encode('utf-8')

		html += '<h2>%s</h2>' % _('Backup Current (Internal) Image')
		html += '<p>%s <b>%s</b></p>' % (_('Storage path:'), device)
		html += '<form action="/backup" method="get">'
		html += '<input type="hidden" name="action" value="internal">'
		html += '<label>%s</label><input type="text" name="name" value="%s">' % (_('Backup name'), default_name)
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
			html += '<button type="submit">%s</button>' % _('Start External Backup')
			html += '</form>'

		html += PAGE_FOOT
		return html.encode('utf-8')

	def runInternal(self, request):
		name = request.args.get(b'name', [b''])[0].decode('utf-8').strip()
		device = getConfiguredDevicePath()
		html = PAGE_HEAD
		if not name or not device:
			html += '<p>%s</p>' % _('Name and storage path are required.')
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
		device = getConfiguredDevicePath()
		image_path_base = detectExternalImagesPath()
		html = PAGE_HEAD
		if not source or not name or not device or not image_path_base:
			html += '<p>%s</p>' % _('Source image, name and storage path are required.')
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
		run_name = request.args.get(b'run', [b''])[0].decode('utf-8')
		if run_name:
			return self.runConvert(request, run_name)
		return self.showFiles(request)

	def showFiles(self, request):
		device = getConfiguredDevicePath()
		html = PAGE_HEAD
		if not device:
			html += '<p>%s <a href="/settings">%s</a></p>' % (_('No storage path configured.'), _('Go to Settings'))
			html += PAGE_FOOT
			return html.encode('utf-8')
		try:
			files = sorted([f for f in os.listdir(device) if f.endswith('.xz')])
		except:
			files = []
		html += '<h2>%s: %s</h2>' % (_('Images on'), device)
		if not files:
			html += '<p>%s</p>' % _('No .xz images found on this device.')
		for f in files:
			html += '<div class="item"><span>%s</span><a href="/convert?run=%s">%s</a></div>' % (f, f, _('Convert'))
		html += PAGE_FOOT
		return html.encode('utf-8')

	def runConvert(self, request, name):
		device = getConfiguredDevicePath()
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
		run = arg('run')

		if name and link and run == '1':
			return self.runDownload(name, link)
		if name and link:
			return self.showConfirm(name, link)
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

	def showConfirm(self, name, link):
		device = getConfiguredDevicePath()
		html = PAGE_HEAD
		if not device:
			html += '<p>%s <a href="/settings">%s</a></p>' % (_('No storage path configured.'), _('Go to Settings'))
			html += PAGE_FOOT
			return html.encode('utf-8')
		html += '<h2>%s: %s</h2>' % (_('Download'), name)
		html += '<p>%s <b>%s</b></p>' % (_('Save to:'), device)
		html += '<form action="/download" method="get">'
		html += '<input type="hidden" name="name" value="%s">' % name
		html += '<input type="hidden" name="link" value="%s">' % link
		html += '<input type="hidden" name="run" value="1">'
		html += '<button type="submit">%s</button>' % _('Start Download')
		html += '</form>'
		html += PAGE_FOOT
		return html.encode('utf-8')

	def runDownload(self, name, link):
		device = getConfiguredDevicePath()
		html = PAGE_HEAD
		if not device:
			html += '<p>%s</p>' % _('No storage path configured.')
		elif _session is None:
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
