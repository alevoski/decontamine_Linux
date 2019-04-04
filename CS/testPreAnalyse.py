#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - testPreAnalyse.py
#@Alexandre Buissé - 2018

#Standard imports
import time
import getpass
import os
import getch
import dbus

def deviceInfo():
    '''
    Get informations of all detected drives.
    Use devicesList() to get devices list of drives.
    '''
    bus = dbus.SystemBus()
    obj = bus.get_object('org.freedesktop.UDisks2', '/org/freedesktop/UDisks2')
    iface = dbus.Interface(obj, 'org.freedesktop.DBus.ObjectManager')
    # i = 0
    objDict = {}
    # for items in iface.GetManagedObjects():
    for k, v in iface.GetManagedObjects().items():
        # print(i, items)
        # print(str(items))
        try:
            # 1 - Get all drives
            # objItems = bus.get_object('org.freedesktop.UDisks2', items)
            objItems = v.get('org.freedesktop.UDisks2.Drive', {})
            # print(objItems)
            # ifaceItems = dbus.Interface(objItems, 'org.freedesktop.DBus.Properties')
            # print(ifaceItems.GetAll('org.freedesktop.UDisks2.Drive'))
            # objID = ifaceItems.Get('org.freedesktop.UDisks2.Drive', 'Id')
            objID = objItems.get('Id')
            # driveType = ifaceItems.Get('org.freedesktop.UDisks2.Drive', 'Media') #usb drive key or other
            driveType = objItems.get('Media') #usb drive key or other
            # ejectable = ifaceItems.Get('org.freedesktop.UDisks2.Drive', 'Ejectable')
            ejectable = objItems.get('Ejectable')
            # driveBus = ifaceItems.Get('org.freedesktop.UDisks2.Drive', 'ConnectionBus') #usb, cd, etc
            driveBus = objItems.get('ConnectionBus') #usb, cd, etc

            # available = objItems.get('MediaAvailable') #usb, cd, etc
            # print('available : ', available)

            # 2 - Get devices list of the founded drive
            # print('driveType :', driveType)
            # print('driveTypeLen :', len(driveType))
            # print(str(k))
            # if len(driveType) != 0:#Do nothing if no driveType
            if len(str(k)) != 0:    #Do nothing if no driveType
                devices = devicesList(str(k), str(driveType), str(driveBus), str(ejectable))
                # print('devices',devices)
                if len(devices) > 0:
                    # print('id', str(k))
                    # print('id', k)
                    # print('ejectable', int(ejectable))
                    # print('driveType', str(driveType))
                    # print('driveBus', str(driveBus))
                    objDict[str(objID)] = {'ejectable':int(ejectable),
                                           'type':str(driveType),
                                           'bus':str(driveBus),
                                           'devices':devices}
                    # print(objDict)

            # print('\n')
        except Exception:
            pass

    return objDict

def devicesList(objID, driveType, driveBus, ejectable):
    '''
    Get devices list of a drive passed in parameter.
    Use mountPtsList() to get mounts points of devices
    Return the devices list find
    '''
    bus = dbus.SystemBus()
    obj = bus.get_object('org.freedesktop.UDisks2', '/org/freedesktop/UDisks2')
    iface = dbus.Interface(obj, 'org.freedesktop.DBus.ObjectManager')

    # print('driveType', driveType)
    # print('ejectable', ejectable)
    # print('driveBus', driveBus)
    # print('id', objID)

    devices = {}
    testHDD = 29
    if driveBus == 'usb' and len(driveType) == 0 and ejectable == '0':#Maybe an hard drive disk so maybe more than one device on it
        # print('HDD detected')
        testHDD = 1
    if driveType != '' or driveBus != '':
        while testHDD < 30:
            oldDeviceDict = devices
            for k, v in iface.GetManagedObjects().items():
                drive_info = v.get('org.freedesktop.UDisks2.Block', {})
                # devices = {}
                # print(str(objID))
                # print(str(drive_info.get('Drive')))
                if str(objID) in str(drive_info.get('Drive')):
                    if drive_info.get('IdUsage') == "filesystem" and not drive_info.get('HintSystem'):# and not drive_info.get('ReadOnly'):
                        # print('\nok\n')
                        device = drive_info.get('Device')
                        readOnly = drive_info.get('ReadOnly')
                        label = drive_info.get('IdLabel')
                        device = bytearray(device).replace(b'\x00', b'').decode('utf-8')
                        # print('device', device)
                        # print('readOnly', readOnly)
                        # print('drive', drive_info.get('Drive'))
                        # print('label', str(label))

                        # print('lenlabel : ', len(label))
                        if len(label) != 0:
                            # print('label ok')
                            # Get mount points lists of the founded drive devices
                            test = 0
                            while test < 30: #Try several times to have the mountPts
                                # print('in test')
                                mountPts = '?'
                                # For optical drives
                                if mountPts == '?' and 'optical' in driveType:
                                    # print('optical drive')
                                    mountPts = mountPtsOptical()
                                else:
                                    try:
                                        mountPts = mountPtsList(str(label))
                                    except Exception:
                                        pass

                                # For drives with more than 1 devices
                                if mountPts == '?':
                                    try:
                                        mountPts = mountPtsDIR(str(label))
                                    except Exception:
                                        pass

                                if mountPts != '?':
                                    test = 30
                                    break
                                # print(test)
                                time.sleep(1)
                                test += 1

                            devices[str(device)] = {'label':str(label),
                                                    'readOnly':int(readOnly),
                                                    'mountPts':str(mountPts)}
            # print(devices)
            testHDD += 1
            if len(devices) > 0:
                time.sleep(1)
            # print(len(devices),len(oldDeviceDict))
            #Compare old devices dict with new devices dict
            if len(devices) > len(oldDeviceDict):
                # print('n device')
                testHDD = 1
            else:
                testHDD += 5
            # print(testHDD)

    return devices

def mountPtsList(device):
    '''
    Get mount point of a device label passed in parameter.
    Return the device label mount point.
    Won't work on drives with multiple partitions (it only detects one) neither on optical disk
    '''
    # print(device, ' tested')
    mntptsRt = '?'

    # Method 1 - Filesystem (UDisks2)

    bus = dbus.SystemBus()
    obj = bus.get_object('org.freedesktop.UDisks2', '/org/freedesktop/UDisks2')
    iface = dbus.Interface(obj, 'org.freedesktop.DBus.ObjectManager')

    for k, v in iface.GetManagedObjects().items():
        mount_point = ''
        drive_info = v.get('org.freedesktop.UDisks2.Filesystem', {})
        # devices = {}
        # print(str(objID))
        mntpts = drive_info.get('MountPoints')
        for letter in mntpts[0]:
            mount_point += chr(letter)
        # print('mount_point :', mount_point)
        # dbus_name = mount_point[:-1].split(os.sep)
        # print('mount_point :', str(mount_point[:-1]))
        # print('type',type(drive_info.get('MountPoints')))
        # print('before condition')
        if str(device) in str(mount_point):
            # print('mount point find')
            # print(str(device), str(mount_point))
            # print(str(mount_point))
            mntptsRt = str(mount_point[:-1])
            return mntptsRt

def mountPtsDIR(device):
    '''
    Method 2 - /media/ to get mount points
    '''
    mntptsRt = '?'
    mounted = os.listdir('/media/'+getpass.getuser())
    if device in mounted:
        mntptsRt = '/media/'+getpass.getuser()+'/'+device
        # print(mntptsRt)

    return mntptsRt

def mountPtsOptical():
    '''
    Method 3 - /media/cdrom/ to get mount points
    '''
    mntptsRt = '?'
    mounted = os.listdir('/media/cdrom/')
    if len(mounted) > 1:
        mntptsRt = '/media/cdrom/'
        # print(mntptsRt)

    return mntptsRt

def userChoiceFT(theLST, elem):
    '''
    Prompt the user
    '''
    print(theLST)
    userChoice = -1
    while userChoice not in theLST:
        try:
            print('Please select a ' + elem + ' to analyze : ')
            userChoice = int(getch.getch())
            # userChoice = int(input('Please select a ' + elem + ' to analyze : '))
            # print(userChoice)
            # print(type(userChoice))
            if isinstance(userChoice, int) and userChoice in theLST:
                return userChoice
            else:
                continue
        except Exception:
            continue

    return userChoice

def choseDrive(theDict):
    '''
    Prompt user to chose a drive, return the drive chosen.
    '''
    print('Multiple drives detected')
    lstKeys = []
    i = 0
    for drives in theDict.keys():
        try:#python2
            print('{} - {}'.format(theDict.keys().index(drives), drives))
            lstKeys.append(theDict.keys().index(drives))
        except Exception:#python3
            print('{} - {}'.format(i, drives))
            lstKeys.append(i)
            i += 1
    userChoice = userChoiceFT(lstKeys, 'drive')
    try:#python2
        print('\nYou chose the drive {}'.format(theDict.keys()[userChoice]))
        return theDict.keys()[userChoice]
    except Exception:#python3
        print('\nYou chose the drive {}'.format(list(theDict.keys())[userChoice]))
        return list(theDict.keys())[userChoice]

def choseDevice(theDict, theDrive):
    '''
    If multiple devices, prompt the user to chose one, return the device chosen
    '''
    allDevices = {}
    for key, values in theDict[theDrive].items():
        # print(key, values)
        if key == 'devices':
            # print(len(values))
            i = 0
            for deviceKey, deviceValues in values.items():
                # print(deviceValues)
                allDevices[i] = deviceValues
                i += 1

    tempDict = {}
    tempDict = allDevices #by default => one device
    if len(allDevices) > 1:#more than one device on the drive
        lstDevices = []
        print('Multiple devices detected for drive '+theDrive)
        i = 0
        for k, values in allDevices.items():
            try:#python2
                print('{} - {}'.format(allDevices.keys().index(k), values['label']))
                lstDevices.append(allDevices.keys().index(k))
            except Exception:#python3
                print("{} - {}".format(i, values['label']))
                lstDevices.append(i)
                i += 1

        userChoice = userChoiceFT(lstDevices, 'device')
        #Get infos of the device (label, read-only and mountpoint)
        tempDict = {}
        tempDict[0] = allDevices[userChoice]
    # print(tempDict)

    return tempDict

def getFiles(media):
    '''
    Get files of the device selected, return filesLst
    '''
    deviceFiles = []
    # for rootDir, subdir, files in os.walk(unicode(media, 'utf-8')):
    for rootDir, subdir, files in os.walk(media):
        # print(rootDir, subdir, files)
        for filename in files:
            # print(rootDir)
            if 'System Volume Information' not in rootDir:
                # print(os.path.join(rootDir, filename))
                deviceFiles.append(os.path.join(rootDir, filename))
    return deviceFiles

def depackedDeviceDict(deviceDict):
    '''
    Return label, mountpoint and readonly state of a device dictionnary passed in parameter
    '''
    for k, values in deviceDict.items():
        label = values['label']
        mountpoint = values['mountPts']
        readonly = values['readOnly']

    # print(label)
    # print(mountpoint)
    # print(readonly)

    return label, mountpoint, readonly

def init():
    '''
    Init the process of finding (and choosing) devices to scan,
    Return the device chosen (automaticly if one device found) and its informations dict
    '''
    #Get all detected drives
    objDict = deviceInfo()

    #Chose a drive (if only 1 drive = autochose this one)
    if len(objDict.keys()) > 1:
        chosen = choseDrive(objDict)
        # print(chosen)
    elif len(objDict.keys()) == 1:
        try: #python2
            chosen = objDict.keys()[0]
            # print('one drive : '+chosen)
        except Exception: #python3
            # print(objDict)
            chosen = list(objDict.keys())
            # print('one drive : '+chosen[0])
    else:
        return 0, 0

    #Get devices of the drive selected
    try:
        deviceDict = choseDevice(objDict, chosen)#python2
    except Exception:
        deviceDict = choseDevice(objDict, chosen[0]) #python3

    return chosen, deviceDict

if __name__ == '__main__':
    deviceDict = init()
    print('You selected ', deviceDict)

#sources
# https://linuxmeerkat.wordpress.com/2014/11/12/python-detection-of-usb-storage-device/
# https://stackoverflow.com/questions/22615750/how-can-the-directory-of-a-usb-drive-connected-to-a-system-be-obtained
# https://stackoverflow.com/questions/23244245/listing-details-of-usb-drives-using-python-and-udisk2#
# http://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.Block.html
# https://www.programcreek.com/python/example/99877/uuid.uuid3 (exemple 38)
