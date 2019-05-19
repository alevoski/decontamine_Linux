#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - clamav.py
#@Alexandre Buissé - 2018

#Standard imports
import subprocess
import re

#Project modules imports
from commontools import prompter
from logManagement import writeLog


def init(mountPts, readOnly, logDirectory):
    '''
    Init scan with ClamAV
    '''
    logFile = logDirectory + 'tempClamAV'
    writeLog(logFile, '\n*****Scan with ClamAV - begin*****\n', 'utf-8')
    res = scan(mountPts, readOnly, logFile)
    writeLog(logFile, '*****Scan with ClamAV - finish*****\n', 'utf-8')
    if res == 1:
        virusDict = getVirus(logFile)
        # print(virusDict)
        return virusDict, logFile
    return res, logFile

def getVirus(logFile):
    '''
    Get virus dict
    '''
    f = open(logFile, mode='r', encoding='utf-8')
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
    # print(lstRemoved)
    for k, v in virusTEMP.items():
        # print(k)
        removed = 0
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
    cmdline = ['/usr/bin/clamdscan', '-v', '-m', '--fdpass', '-l', logFile, mountPts]
    if not readOnly:
        #Ask user if he wants av to autoclean the device
        rep = prompter('Do you want to automaticly clean the device ? (y/n)')
        if 'y' in str(rep):
            cmdline = ['/usr/bin/clamdscan', '-v', '-m', '--remove', '--fdpass', '-l', logFile, mountPts]
        elif 'n' in str(rep):
            pass
    print('Scan begin')
    try:
        res = str(subprocess.check_output(cmdline), 'utf-8')
        #print(res)
        # p = re.findall('Infected files:*?(\d+)', str(res))
        return 0
    except subprocess.CalledProcessError as e:#Error
        p = re.findall(r'exit status.*?(\d+)', str(e))

    return int(p[0])

def version():
    '''
    Return version number of ClamAV
    '''
    ver = str(subprocess.check_output(['/usr/bin/clamdscan', '-V']), 'utf-8')
    return ver.replace('ClamAV ', '').replace('\n', '')

if __name__ == '__main__':
    print(version())
