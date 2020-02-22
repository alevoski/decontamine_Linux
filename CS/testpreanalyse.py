#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - testpreanalyse.py
#@Alexandre Buissé - 2018/2020

#Standard imports
import time
import getpass
import os

#Third party imports
import getch
import dbus

def device_info():
    '''
    Get informations of all detected drives.
    Use list_devices() to get devices list of drives.
    '''
    bus = dbus.SystemBus()
    obj = bus.get_object('org.freedesktop.UDisks2', '/org/freedesktop/UDisks2')
    iface = dbus.Interface(obj, 'org.freedesktop.DBus.ObjectManager')
    # i = 0
    obj_dict = {}
    # for items in iface.GetManagedObjects():
    for key, values in iface.GetManagedObjects().items():
        # print(i, items)
        # print(str(items))
        try:
            # 1 - Get all drives
            # obj_items = bus.get_object('org.freedesktop.UDisks2', items)
            obj_items = values.get('org.freedesktop.UDisks2.Drive', {})
            # print(obj_items)
            # ifaceItems = dbus.Interface(obj_items, 'org.freedesktop.DBus.Properties')
            # print(ifaceItems.GetAll('org.freedesktop.UDisks2.Drive'))
            # obj_id = ifaceItems.Get('org.freedesktop.UDisks2.Drive', 'Id')
            obj_id = obj_items.get('Id')
            # drive_type = ifaceItems.Get('org.freedesktop.UDisks2.Drive', 'Media') #usb drive key or other
            drive_type = obj_items.get('Media') #usb drive key or other
            # ejectable = ifaceItems.Get('org.freedesktop.UDisks2.Drive', 'Ejectable')
            ejectable = obj_items.get('Ejectable')
            # drive_bus = ifaceItems.Get('org.freedesktop.UDisks2.Drive', 'ConnectionBus') #usb, cd, etc
            drive_bus = obj_items.get('ConnectionBus') #usb, cd, etc

            # available = obj_items.get('MediaAvailable') #usb, cd, etc
            # print('available : ', available)

            # 2 - Get devices list of the founded drive
            # print('drive_type :', drive_type)
            # print('driveTypeLen :', len(drive_type))
            # print(str(key))
            # if len(drive_type) != 0:#Do nothing if no drive_type
            if len(str(key)) != 0:    #Do nothing if no drive_type
                devices = list_devices(str(key), str(drive_type), str(drive_bus), str(ejectable))
                # print('devices',devices)
                if len(devices) > 0:
                    # print('id', str(key))
                    # print('id', key)
                    # print('ejectable', int(ejectable))
                    # print('drive_type', str(drive_type))
                    # print('drive_bus', str(drive_bus))
                    obj_dict[str(obj_id)] = {'ejectable':int(ejectable),
                                             'type':str(drive_type),
                                             'bus':str(drive_bus),
                                             'devices':devices}
                    # print(obj_dict)

            # print('\n')
        except Exception:
            pass

    return obj_dict

def list_devices(obj_id, drive_type, drive_bus, ejectable):
    '''
    Get devices list of a drive passed in parameter.
    Use mount_pts_dbus() to get mounts points of devices
    Return the devices list find
    '''
    bus = dbus.SystemBus()
    obj = bus.get_object('org.freedesktop.UDisks2', '/org/freedesktop/UDisks2')
    iface = dbus.Interface(obj, 'org.freedesktop.DBus.ObjectManager')

    # print('drive_type', drive_type)
    # print('ejectable', ejectable)
    # print('drive_bus', drive_bus)
    # print('id', obj_id)

    devices = {}
    test_hdd = 29
    if drive_bus == 'usb' and len(drive_type) == 0 and ejectable == '0': # Maybe an HDD so maybe more than one device on it
        # print('HDD detected')
        test_hdd = 1
    if drive_type != '' or drive_bus != '':
        while test_hdd < 30:
            old_devices_dict = devices
            for _, values in iface.GetManagedObjects().items():
                drive_info = values.get('org.freedesktop.UDisks2.Block', {})
                # devices = {}
                # print(str(obj_id))
                # print(str(drive_info.get('Drive')))
                if str(obj_id) in str(drive_info.get('Drive')):
                    if drive_info.get('IdUsage') == "filesystem" and not drive_info.get('HintSystem'):
                        # print('\nok\n')
                        device = drive_info.get('Device')
                        read_only = drive_info.get('ReadOnly')
                        label = drive_info.get('IdLabel')
                        # drive = drive_info.get('Drive')
                        iduid = drive_info.get('IdUUID')
                        device = bytearray(device).replace(b'\x00', b'').decode('utf-8')
                        # print('device', device)
                        # print('read_only', read_only)
                        # print('drive', drive)
                        # print('label', str(label))
                        # print('hintname', str(hintname))
                        # print('test', drive_info.get('Id'))
                        # print('test', drive_info.get('DeviceNumber'))
                        # print('test', iduid)

                        # print('lenlabel : ', len(label))
                        if len(label) != 0 or len(iduid) != 0:
                            # print('label ok')
                            # Get mount points lists of the founded drive devices
                            test = 0
                            while test < 30: # Try several times to have the mount_pts
                                # print('in test')
                                mount_pts = '?'
                                # For optical drives
                                if mount_pts == '?' and 'optical' in drive_type:
                                    # print('optical drive')
                                    mount_pts = mount_pts_optical()
                                # For USB drives with label
                                elif len(label) != 0:
                                    try:
                                        # print('usb ?')
                                        mount_pts = mount_pts_dbus(str(label))#, str(iduid))
                                        # print('USB mount_pts_dbus : ' + mount_pts)
                                    except Exception:
                                        pass

                                # For drives with more than 1 devices or USB drives without label
                                if mount_pts == '?':
                                    try:
                                        # print('other usb')
                                        mount_pts = mount_pts_dir(str(label), str(iduid))
                                        # print('other USB mount_pts : ' + mount_pts)
                                    except Exception:
                                        pass

                                if mount_pts != '?':
                                    test = 30
                                    break
                                # print(test)
                                time.sleep(1)
                                test += 1
                            if len(label) == 0:
                                label = iduid
                            devices[str(device)] = {'device':str(device),
                                                    'label':str(label),
                                                    'read_only':int(read_only),
                                                    'mount_pts':str(mount_pts)}
            # print(devices)
            test_hdd += 1
            if len(devices) > 0:
                time.sleep(1)
            # print(len(devices),len(old_devices_dict))
            #Compare old devices dict with new devices dict
            if len(devices) > len(old_devices_dict):
                # print('n device')
                test_hdd = 1
            else:
                test_hdd += 5
            # print(test_hdd)

    if mount_pts == '?': # it will be '?' if the usb device is plugged but unmounted
        devices = {}
    # print('devices')
    # print(devices)
    return devices

def mount_pts_dbus(device):
    '''
    Get mount point of a device label passed in parameter.
    Return the device label mount point.
    Won't work on drives with multiple partitions (it only detects one) neither on optical disk
    Update 2019/12 : won't work anymore, all drives goes to mount_pts_dir() instead
    '''
    # print(device, ' tested')
    mount_pts = '?'

    # Method 1 - Filesystem (UDisks2)

    bus = dbus.SystemBus()
    obj = bus.get_object('org.freedesktop.UDisks2', '/org/freedesktop/UDisks2')
    iface = dbus.Interface(obj, 'org.freedesktop.DBus.ObjectManager')

    # print('before for loop')
    for _, values in iface.GetManagedObjects().items():
        mount_point = ''
        drive_info = values.get('org.freedesktop.UDisks2.Filesystem', {})
        # devices = {}
        # print(str(drive_info))
        mntpts = drive_info.get('MountPoints')
        # print(mntpts)
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
            mount_pts = str(mount_point[:-1])
    return mount_pts

def mount_pts_dir(device, iduid):
    '''
    Method 2 - /media/ to get mount points
    '''
    # print('len(device)', len(device))
    # print('device', device)
    # print('len(iduid)', len(iduid))
    # print('iduid', iduid)
    mount_pts = '?'
    mounted = os.listdir('/media/' + getpass.getuser())
    # print('mount : ', mounted)
    if device in mounted: # For USB
        # print('usb')
        mount_pts = '/media/' + getpass.getuser() + '/'+ device
        # print(mount_pts)
    if iduid in mounted and len(device) == 0: # For USB without label
        # print('other usb')
        mount_pts = '/media/' + getpass.getuser() + '/'+ iduid
    # print(mount_pts)
    return mount_pts

def mount_pts_optical():
    '''
    Method 3 - /media/cdrom/ to get mount points
    '''
    mount_pts = '?'
    mounted = os.listdir('/media/cdrom/')
    if len(mounted) > 1:
        mount_pts = '/media/cdrom/'
    return mount_pts

def prompt_choice(the_list, elem):
    '''
    Prompt the user
    '''
    user_choice = -1
    while user_choice not in the_list:
        try:
            print('Please select a ' + elem + ' to analyze : ')
            user_choice = int(getch.getch())
            if isinstance(user_choice, int) and user_choice in the_list:
                break
        except Exception:
            continue
    return user_choice

def chose_drive(obj_dict):
    '''
    Prompt user to chose a drive, return the drive chosen.
    '''
    print('Multiple drives detected')
    keys_list = []
    i = 0
    for drives in obj_dict.keys():
        print('{} - {}'.format(i, drives))
        keys_list.append(i)
        i += 1
    user_choice = prompt_choice(keys_list, 'drive')
    print('\nYou chose the drive {}'.format(list(obj_dict.keys())[user_choice]))
    return list(obj_dict.keys())[user_choice]

def chose_device(obj_dict, chosen):
    '''
    If multiple devices, prompt the user to chose one, return the device chosen
    '''
    all_devices_dict = {}
    for key, values in obj_dict[chosen].items():
        # print(key, values)
        if key == 'devices':
            # print(len(values))
            i = 0
            for _, device_values in values.items():
                # print('device : ' + device)
                # print(device_values)
                all_devices_dict[i] = device_values
                i += 1

    device_dict = {}
    part_list = []
    device_dict = all_devices_dict # by default => one device
    if len(all_devices_dict) > 1: # more than one device on the drive
        devices_list = []
        print('Multiple devices detected for drive ' + chosen)
        i = 0
        for key, values in all_devices_dict.items():
            print("{} - {}".format(i, values['label']))
            devices_list.append(i)
            part_list.append(values['device'])
            i += 1

        user_choice = prompt_choice(devices_list, 'device')
        #Get infos of the device (label, read-only and mount_pts)
        device_dict = {}
        device_dict[0] = all_devices_dict[user_choice]
    # print(device_dict)

    return device_dict, part_list

def get_files(media, files_list):
    '''
    Get files of the device selected, return files_list
    '''
    try:
        for elems in os.scandir(media):
            if 'System Volume Information' not in media:
                try:
                    if elems.is_dir(follow_symlinks=False):
                        get_files(elems.path, files_list)
                    else:
                        files_list.append(os.path.join(elems.path, elems.name))
                except PermissionError:
                    pass
    except PermissionError:
        print(media + ' is not ready, please wait.')
        time.sleep(2)
        get_files(media, files_list)
    return files_list

def depack_device(device_dict):
    '''
    Return label, mount_pts and read_only state of a device dictionnary passed in parameter
    '''
    for _, values in device_dict.items():
        device = [values['device']]
        label = values['label']
        mount_pts = values['mount_pts']
        read_only = values['read_only']
    return device, label, mount_pts, read_only

def init():
    '''
    Init the process of finding (and choosing) devices to scan,
    Return the device chosen (automaticly if one device found) and its informations dict
    '''
    # Get all detected drives
    obj_dict = device_info()

    # Chose a drive (if only 1 drive = autochose this one)
    if len(obj_dict.keys()) > 1:
        chosen = chose_drive(obj_dict)
    elif len(obj_dict.keys()) == 1:
        chosen = list(obj_dict.keys())
    else:
        return 0, 0, 0

    # Get devices of the drive selected
    try:
        device_dict, part_list = chose_device(obj_dict, chosen)
    except TypeError:
        device_dict, part_list = chose_device(obj_dict, chosen[0])

    return chosen, device_dict, part_list

if __name__ == '__main__':
    print(init())

#sources
# https://linuxmeerkat.wordpress.com/2014/11/12/python-detection-of-usb-storage-device/
# https://stackoverflow.com/questions/22615750/how-can-the-directory-of-a-usb-drive-connected-to-a-system-be-obtained
# https://stackoverflow.com/questions/23244245/listing-details-of-usb-drives-using-python-and-udisk2#
# http://storaged.org/doc/udisks2-api/latest/gdbus-org.freedesktop.UDisks2.Block.html
# https://www.programcreek.com/python/example/99877/uuid.uuid3 (exemple 38)
