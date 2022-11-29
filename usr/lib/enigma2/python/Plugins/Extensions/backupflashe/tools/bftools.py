#!/usr/bin/python
# -*- coding: utf-8 -*-
# RAED & mfaraj57 &  (c) 2018
# Code RAED & mfaraj57

# python3
from __future__ import print_function
from .compat import compat_Request, compat_urlopen

from Components.About import about
from Tools.Directories import fileExists, copyfile, createDir, resolveFilename, SCOPE_PLUGINS

import os, traceback, re, json, datetime, ssl

logfile="/tmp/backupflash.log"
backupflash_script="/tmp/backupflash.sh"

if not fileExists('/usr/lib64'):
	LIBPATH='/usr/lib'
else:
	LIBPATH='/usr/lib64'

#def logdata(label, txt):
#    try:
#        bfile=open(logfile, 'a')
#        bfile.write(str(label) + ':' + str(txt) + '\n')
#        bfile.close()
#    except:
#        pass

def logdata(label='', data=None):
    try:
        bfile=open(logfile, 'a')
        bfile.write( str(label) + ' : ' + str(data) + "\n")
        bfile.close()
    except:
        pass

def dellog():
    if os.path.exists(logfile):
        os.remove(logfile)

def copylog(device_path):
    try:
          logfile2=os.path.join(device_path,"backupflash.log")
          backupflash_script2=os.path.join(device_path,"backupflash.sh")
          if os.path.exists(logfile2):
             os.remove(logfile2)                   
          copyfile(logfile,logfile2)
          copyfile(backupflash_script, backupflash_script2)
    except:
              pass

def getimage_version():
    try:
      image_version=about.getEnigmaVersionString()
      return image_version.strip()
    except:
        return None

def getversioninfo():
    currversion = '1.0'
    enigmaos = 'all'
    lastbuild = '01012016'
    version_file = resolveFilename(SCOPE_PLUGINS, 'Extensions/backupflashe/tools/version')
    if os.path.exists(version_file):
        try:
            fp = open(version_file, 'r').readlines()
            for line in fp:
                if 'version' in line:
                    currversion = line.split('=')[1].strip()
                if 'enigmaos' in line:
                    enigmaos = line.split('=')[1].strip()
                
                if 'lastbuild' in line:
                    lastbuild = line.split('=')[1].strip()
        except:
            pass
    return (currversion, lastbuild, enigmaos)

def getboxtype():
        boxtype="dm7080hd"
        if os.path.exists('/proc/stb/info/model'):
            f = open('/proc/stb/info/model')
            boxtype = f.read()
            f.close()
            boxtype = boxtype.replace('\n', '').replace('\\l', '')
            if boxtype == "dm525":
                    boxtype="dm520"
            if boxtype == "one":
                    boxtype="dreamone"
            if boxtype == "two":
                    boxtype="dreamtwo"
        if boxtype.strip()=="":
           boxtype=getHostName()
        return boxtype

def getHostName():
    try:
        boxtype=open("/etc/hostname").read()
        return boxtype.strip()
    except:
        return ""

def get_images(url,regx):
        images = []
        logdata("images_url",url)
        try:
            req = compat_Request(url, headers={'User-Agent': 'Mozilla/5.0'}) # add [headers={'User-Agent': 'Mozilla/5.0'}] to fix HTTP Error 403: Forbidden
            response = compat_urlopen(req,timeout=20,context=ssl._create_unverified_context())
            data = response.read()
            response.close()
            match = re.findall(regx,data, re.M|re.I)
            for item1,item2 in match:
                images.append((item1,item2))
            return images
        except:
            trace_error()
            return []

def get_images2(url,regx):
        images = []
        logdata("images_url",url)
        try:
            req = compat_Request(url, headers={'User-Agent': 'Mozilla/5.0'}) # add [headers={'User-Agent': 'Mozilla/5.0'}] to fix HTTP Error 403: Forbidden
            response = compat_urlopen(req,timeout=20,context=ssl._create_unverified_context())
            try:
                data = response.read().decode('utf-8')
            except Exception as e:
                data = response.read()  
            response.close()
            match = re.findall(str(regx), data, re.M|re.I)
            for item1,item2 in match:
                images.append((item1,item2))
            return images
        except:
            trace_error()
            return []

def get_images_mediafire(url):
        images = []
        logdata("images_url",url)
        def readnet(url):
            try:
                req = compat_Request(url, headers={'User-Agent': 'Mozilla/5.0'}) # add [headers={'User-Agent': 'Mozilla/5.0'}] to fix HTTP Error 403: Forbidden
                response = compat_urlopen(req,timeout=30,context=ssl._create_unverified_context())
                data = response.read()
                return data
            except:
                trace_error()
                return None
        data=readnet(url)
        if data is None:
            return []
        jdata=json.loads(data)
        dl=jdata['response']['folder_content']['files']
        images=[]
        for item in dl:
                dl=item['links']['normal_download']
                name=os.path.split(dl)[1]
                data=readnet(dl)
                regx="href='(.*?)'"
                hrefs=re.findall(regx,data, re.M|re.I)
                print("hrefs",hrefs)
                for href in hrefs:
                        if not "download" in href:
                           continue
                        name=os.path.split(href)[1]
                        images.append((name,href))
                        break
        print(images)       
        return  images   

def trace_error():
    try:
        traceback.print_exc(file=sys.stdout)
        if os.path.exists(logfile):
            pass
        else:
            return
        traceback.print_exc(file=open(logfile, 'a'))
    except:
        pass

def getimage_name():
    GP3='%s/enigma2/python/Plugins/Bp/geminimain' % LIBPATH
    GP4='%s/enigma2/python/Plugins/GP4/geminilocale/plugin.pyo' % LIBPATH
    BLACKHOLE='%s/enigma2/python/Blackhole' % LIBPATH
    OPENBH='%s/enigma2/python/Screens/BpBlue.pyo' % LIBPATH
    MEDIASAT='%s/enigma2/python/MediaSat' % LIBPATH
    TSIMAGE='%s/enigma2/python/Plugins/TSimage' % LIBPATH
    VTI='%s/enigma2/python/Plugins/SystemPlugins/VTIPanel' % LIBPATH
    MERLIN=resolveFilename(SCOPE_PLUGINS, 'Extensions/AddOnManager')
    DREAMELITE='%s/enigma2/python/DE' % LIBPATH
    Demoni='%s/enigma2/python/Plugins/SystemPlugins/DemonisatManager' % LIBPATH
    OPENDROID='%s/enigma2/python/OPENDROID' % LIBPATH
    EGAMI='%s/enigma2/python/EGAMI' % LIBPATH
    Satdreamgr='%s/enigma2/python/Plugins/Satdreamgr' % LIBPATH
    Powerboard=resolveFilename(SCOPE_PLUGINS, 'Extensions/PowerboardCenter')
    PKT=resolveFilename(SCOPE_PLUGINS, 'Extensions/PKT')
    OPENVIX='%s/enigma2/python/Plugins/SystemPlugins/ViX' % LIBPATH
    Domica='%s/enigma2/python/Plugins/Domica' % LIBPATH
    HDMU=resolveFilename(SCOPE_PLUGINS, 'Extensions/HDMUCenter')
    OPENLD=resolveFilename(SCOPE_PLUGINS, 'Extensions/LDteam')
    TDW=resolveFilename(SCOPE_PLUGINS, 'Extensions/TDW')
    OPENHDF=resolveFilename(SCOPE_PLUGINS, 'Extensions/HDF-Toolbox')
    OPENESI=resolveFilename(SCOPE_PLUGINS, 'Extensions/ExtraAddonss')
    NonSoloSat=resolveFilename(SCOPE_PLUGINS, 'Extensions/NssPanel')
    NEWNIGMA2='%s/enigma2/python/Plugins/newnigma2' % LIBPATH
    name = 'Backup'
    if os.path.exists(GP3):
        name = 'Backup-GP3'
    elif os.path.exists(GP4):
        name = 'Backup-GP4'
    elif os.path.exists(BLACKHOLE):
        name = 'Backup-BlackHole'
    elif os.path.exists(OPENBH):
        name = 'Backup-OpenBH'
    elif os.path.exists(MEDIASAT):
        name = 'Backup-MediaSat'
    elif os.path.exists(TSIMAGE):
        name = 'Backup-TSimage'
    elif os.path.exists(VTI):
        name = 'Backup-VTI'
    elif os.path.exists(MERLIN):
        name = 'Backup-Merlin4'
    elif os.path.exists(DREAMELITE):
        name = 'Backup-DreamEiIte'
    elif os.path.exists(Demoni):
        name = 'Backup-Demonisat'
    elif os.path.exists(OPENDROID):
        name = 'Backup-OpenDroid'
    elif os.path.exists(EGAMI):
        name = 'Backup-EGAMI'
    elif os.path.exists(Satdreamgr):
        name = 'Backup-Satdreamgr'
    elif os.path.exists(Powerboard):
        name = 'Backup-Powerboard'
    elif os.path.exists(PKT):
        name = 'Backup-PKT'
    elif os.path.exists(OPENVIX):
        name = 'Backup-OpenVix'
    elif os.path.exists(Domica):
        name = 'Backup-Domica'
    elif os.path.exists(HDMU):
        name = 'Backup-HDMU'
    elif os.path.exists(OPENLD):
        name = 'Backup-OpenLD'
    elif os.path.exists(TDW):
        name = 'Backup-TDW'
    elif os.path.exists(OPENHDF):
        name = 'Backup-OpenHDF'
    elif os.path.exists(OPENESI):
        name = 'Backup-OpenESI'
    elif os.path.exists(NonSoloSat):
        name = 'Backup-NonSoloSat'
    elif os.path.exists(NEWNIGMA2):
        name = 'Backup-newnigma2'
    else:
        name=None
        if os.path.exists("/etc/image-version"):
                f=open("/etc/image-version")
                line = f.readline()                                                    
                while (line):                                             
                        line = f.readline()                                                 
                        if line.startswith("creator="):                                    
                                name=line
                f.close()
                if name:
                    name=name.replace("creator=","")
                    sp=[]
                    if len(name) > 0:
                            sp=name.split(" ")
                            if len(sp) > 0:
                                    name=sp[0]
                                    name=name.replace("\n","")
                                    name="Backup-"+name
        if name is None and os.path.exists("/etc/issue.net"):
            f=open("/etc/issue.net")
            i=f.read()
            f.close()
            if "power-Sat" in i.lower():
                    name="Backup-PowerSat"
            if "oooZooN" in i.lower():    
                    name="Backup-OoZooN"
            if "peter" in i.lower():    
                    name="Backup-PeterPan"
            if "italysat" in i.lower():    
                    name="Backup-ItalySat"
            if "openatv" in i.lower():
                    name="Backup-openATV"
            if "rudreamat" in i.lower():
                    name="Backup-ruDREAM"
            if "openeight" in i.lower():
                    name="Backup-OpenEight"
            if "oenplus" in i.lower():
                    name="Backup-OpenPlus"
            if "openpli" in i.lower():
                    name="Backup-OpenPLI"
            if "opendreambox" in i.lower():
                    name="Backup-Opendreambox"
        if name is None:
            name="Backup-dreambox"

    now = datetime.datetime.now()
    name = name + "-%s" % now.strftime('%Y-%m-%d')
    #image_version=getimage_version()
    #if image_version is not None and not image_version=="":
    #    name=name+"-"+image_version
    #return (name)

    #image_version=getimage_version()
    #if image_version is not None and not image_version=="":
    #    name=name+"-"+image_version
    #if name is None:
    #    name="Backup-"
    return (name)

def getmDevices():
        myusb = myusb1 = myhdd = myhdd2 = mysdcard = mysd = myuniverse = myba = mydata =''
        mdevices = []
        myusb=None
        myusb1=None
        myhdd=None
        myhdd2=None
        mysdcard=None
        mysd=None
        myuniverse=None
        myba=None
        mydata=None
        if fileExists('/proc/mounts'):
            f = open('/proc/mounts', 'r')
            for line in f.readlines():
                if line.find('/media/usb') != -1:
                    myusb = '/media/usb/backup'
                    if not os.path.exists('/media/usb/backup'):
                       os.system('mkdir -p /media/usb/backup')
                elif line.find('/media/usb1') != -1:
                    myusb1 = '/media/usb1/backup'
                    if not os.path.exists('/media/usb1/backup'):
                       os.system('mkdir -p /media/usb1/backup')
                elif line.find('/media/hdd') != -1:
                    myhdd = '/media/hdd/backup'
                    if not os.path.exists('/media/hdd/backup'):
                       os.system('mkdir -p /media/hdd/backup')
                elif line.find('/media/hdd2') != -1:
                    myhdd2 = '/media/hdd2/backup'
                    if not os.path.exists('/media/hdd2/backup'):
                       os.system('mkdir -p /media/hdd2/backup')
                elif line.find('/media/sdcard') != -1:
                    mysdcard = '/media/sdcard/backup'
                    if not os.path.exists('/media/sdcard/backup'):
                       os.system('mkdir -p /media/sdcard/backup')
                elif line.find('/media/sd') != -1:
                    mysd = '/media/sd/backup'
                    if not os.path.exists('/media/sd/backup'):
                       os.system('mkdir -p /media/sd/backup')
                elif line.find('/universe') != -1:
                    myuniverse = '/universe/backup'
                    if not os.path.exists('/universe/backup'):
                       os.system('mkdir -p /universe/backup')
                elif line.find('/media/ba') != -1:
                    myba = '/media/ba/backup'
                    if not os.path.exists('/media/ba/backup'):
                       os.system('mkdir -p /media/ba/backup')
                elif line.find('/data') != -1:
                    mydata = '/data/backup'
                    if not os.path.exists('/data/backup'):
                       os.system('mkdir -p /data/backup')
            f.close()
        if myusb:
            mdevices.append((myusb, myusb))
        if myusb1:
            mdevices.append((myusb1, myusb1))
        if myhdd:
            mdevices.append((myhdd, myhdd))
        if myhdd2:
            mdevices.append((myhdd2, myhdd2))
        if mysdcard:
            mdevices.append((mysdcard, mysdcard))
        if mysd:
            mdevices.append((mysd, mysd))
        if myuniverse:
            mdevices.append((myuniverse, myuniverse))
        if myba:
            mdevices.append((myba, myba))
        if mydata:
            mdevices.append((mydata, mydata))
        return mdevices
