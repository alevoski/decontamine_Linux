# -*- coding: utf-8 -*-
#!/usr/bin/python

import os
import time
import sys
from datetime import datetime, timedelta
try:
    from os import scandir, walk
except ImportError:
    from scandir import scandir, walk

def getFiles(media):
    '''
    Method 1 : os.walk
    Get files of the device selected, return filesLst
    '''
    deviceFiles = []
    for dir, subdir, files in os.walk(media):
        # print(dir, subdir, files)
        for filename in files:
            # print(dir)
            if 'System Volume Information' not in dir:
                # print(os.path.join(dir, filename))
                deviceFiles.append(os.path.join(dir, filename))
    for elem in deviceFiles:
        if 'é' in elem:
            print(elem)
    return deviceFiles
		
def getFiles2(media, deviceFiles):
    '''
    Method 2 : os.scandir
    Get files of the device selected, return filesLst
    '''
    # deviceFiles = []
    for entry in scandir(media):
        # print(type(entry))
        if entry.is_dir():
            # print('directory find : ', entry)
            getFiles2(entry.path, deviceFiles)
        else:
            # print('file find : ', entry)
            deviceFiles.append(entry.path)
    # search(media, deviceFiles)
    # print(deviceFiles)
    return deviceFiles

if __name__ == '__main__':
    #Method1
    beginScan1 = time.time()
    deviceFiles = getFiles('/media/dev/Win7-AIO-64Bits')
    print(len(deviceFiles), 'files on the device')
    endScan1 = time.time()
    totalTimeScan1 = endScan1 - beginScan1
    print('os.walk : device analyze in '+str(round(totalTimeScan1, 10)))
    min = totalTimeScan1
    
    # sys.exit()
    
    #Method2
    beginScan2 = time.time()
    deviceFiles = getFiles2('/media/dev/Win7-AIO-64Bits', [])
    # print(deviceFiles)
    print(len(deviceFiles), 'files on the device')
    endScan2 = time.time()
    totalTimeScan2 = endScan2 - beginScan2
    print('os.scandir : device analyze in '+str(round(totalTimeScan2, 10)))
    max = totalTimeScan2

    # sys.exit()
    
    #Compare
    if totalTimeScan2 < min:
        print('os.scandir is faster')
        min = totalTimeScan2
        max = totalTimeScan1
    elif totalTimeScan2 > min:
        print('os.walk is faster')
    else:
        print('Both method are equal')
    print('Difference in sec : ', max-min)
    print('Difference in % : ', ((max/min)-1)*100)