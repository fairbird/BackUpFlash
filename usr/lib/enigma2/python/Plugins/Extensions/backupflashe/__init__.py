import os
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS

DBACKUP = resolveFilename(SCOPE_PLUGINS, 'Extensions/dBackup')
PLUGINROOT = resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe')

if os.path.exists(DBACKUP) and not os.path.exists(DBACKUP + '/tools/version'):
	os.system('rm -r %s' % DBACKUP)
#if os.path.exists(DBACKUP + '/tools/version') and not os.path.exists(PLUGINROOT):
#	os.system('mv %s %s' % (DBACKUP, PLUGINROOT))
