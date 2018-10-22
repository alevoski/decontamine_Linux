# -*- coding: utf-8 -*-
#!/usr/bin/python3
#Decontamine Linux - clamav.py
#@Alexandre Buissé - 2018

import commontools
import subprocess
import re

def init(mountPts, readOnly, logDirectory):
    '''
    Init scan with ClamAV
    '''
    # print('Scan with ClamAV - begin')
    logFile = logDirectory + 'tempClamAV'
    res = scan(mountPts, readOnly, logFile)
    # print('Scan with ClamAV - finish')
    if res == 1:
        virusDict = getVirus(logFile)
        # print(virusDict)
        return virusDict, logFile
    return res, logFile
    
def getVirus(logFile):
    '''
    Get virus dict 
    '''
    f = open(logFile, mode = 'r', encoding = 'utf-8')
    virusFound = {}
    virusTEMP = {}
    virusName = ''
    virusType = ''
    lstRemoved = []
    for line in f:
        if 'FOUND' in line:
            virusName = re.findall('(.*):', str(line))
            virusType = re.findall(':(.*)FOUND', str(line))
            virusTEMP[virusName[0]] = virusType[0]
        if 'Removed' in line:
            # print('rm : ', line)
            removedVirus = re.findall('(.*):', str(line))
            # print(removedVirus)
            lstRemoved.append(removedVirus[0])
            
    #Compare lstRemoved with virusTEMP:
    removed = 0
    # print(lstRemoved)
    for k, v in virusTEMP.items():
        # print(k)
        if k in lstRemoved:
            removed = 1
            # print('rm ok')
        virusFound[k] = {'type':str(v), 'removed':removed}
    return virusFound

def scan(mountPts, readOnly, logFile):
    '''
    Scan the mounting point in parameters.
    Return 
        a code
            0 : No virus
            1 : Virus found
            2 : Error
            3 : Scan stopped by user
    '''
    cmdline = 'clamdscan -v -m --fdpass -l ' + logFile + ' ' + mountPts
    if readOnly == False:
        #Ask user if he wants av to autoclean the device
        rep = commontools.prompter('Do you want to automaticly clean the device ? (y/n)')
        if 'y' in str(rep):
            cmdline = 'clamdscan -v -m --remove --fdpass -l ' + logFile + ' ' + mountPts
        elif 'n' in str(rep):
            pass
    print('Scan with ClamAV - begin')
    try:
        res = str(subprocess.check_output(cmdline, shell = True), 'utf-8')
        print(res)
        # p = re.findall('Infected files:*?(\d+)', str(res))
        return 0
    except subprocess.CalledProcessError as e:#Error
        p = re.findall('exit status.*?(\d+)', str(e))
        # print(p)
        # print(int(p[0]))
        # print(type(p[0]))

    return int(p[0])

def version():
    '''
    Return version number of ClamAV
    '''
    cmdline = 'clamdscan -V'
    ver = str(subprocess.check_output(cmdline, shell = True), 'utf-8')
    return ver.replace('ClamAV ','')
    
# clamdscan -v -m <directory>