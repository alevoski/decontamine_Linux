#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - f-secure.py
#@Alexandre Buissé - 2018

#Standard imports
import subprocess
import re

#Project modules imports
from commontools import prompter
from logManagement import writeLog

def init(mountPts, readOnly, logDirectory):
    '''
    Init scan with F-Secure
    '''
    logFile = logDirectory + 'tempF-SecureAV'
    writeLog(logFile, '\n*****Scan with F-Secure - begin*****\n', 'utf-8')
    scan(mountPts, readOnly, logFile)
    writeLog(logFile, '\n*****Scan with F-Secure - finish*****\n', 'utf-8')

    virusDict = getVirus(logFile)
    # print(virusDict)
    return virusDict, logFile

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
        if 'Infected:' in line:
            virusName = re.findall('(.*): Infected', str(line))
            virusType = re.findall('Infected: (.*)', str(line))
            # print(virusName, virusType)
            virusTEMP[virusName[0]] = virusType[0]
        if '[deleted]' in line:
            # print('rm : ', line)
            # removedVirus = re.findall('file (.*)', str(line))
            # print(removedVirus)
            lstRemoved.append(virusName[0])

    #Compare lstRemoved with virusTEMP:
    # print('F-Secure - virus detected\n')
    # print(virusTEMP)
    # print('F-Secure - virus removed\n')
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
    '''
    cmdline = ['/usr/bin/fsav', '--virus-action1=report', '--allfiles', '--archive', '--maxnested=15', '--scantimeout=180', mountPts]
    if not readOnly:
        #Ask user if he wants av to autoclean the device
        rep = prompter('Do you want to automaticly clean the device ? (y/n)')
        if 'y' in str(rep):
            cmdline = ['/usr/bin/fsav', '--virus-action1=clean', '--virus-action2=remove', '--auto', '--allfiles', '--archive', '--maxnested=15', '--scantimeout=180', mountPts]
    print('Scan begin')
    with open(logFile, mode='w', encoding='utf-8') as flog:
        subprocess.call(cmdline, stdout=flog)

def version():
    '''
    Return version informations of F-Secure
    '''
    try:
        # cmdline = 'fsav --version | grep -e "Security version" -e "Hydra engine version" -e "Hydra database version"'
        vertemp = str(subprocess.check_output(['/usr/bin/fsav', '--version']), 'utf-8')

        # Get Product version
        pver = 'Prod_ver ' + str(re.findall('F-Secure Linux Security version (.*)', vertemp)[0])

        # Get Engine version
        ever = '/Eng_ver ' + str(re.findall('F-Secure Corporation Hydra engine version (.*)', vertemp)[0])

        # Get last update date
        vdata = '/VirusDAT_ver ' + str(re.findall('F-Secure Corporation Hydra database version (.*)', vertemp)[0])

        finalres = pver + ever + vdata

        # print(finalres)
        return finalres
    except subprocess.CalledProcessError as e:
        # print(e)
        return "Evaluation version"


if __name__ == '__main__':
    version()
