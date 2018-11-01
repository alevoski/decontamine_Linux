#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - sophos.py
#@Alexandre Buissé - 2018

import commontools
import logManagement
import subprocess
import re

def init(mountPts, readOnly, logDirectory):
    '''
    Init scan with Sophos
    '''
    logFile = logDirectory + 'tempSophosAV'
    logManagement.writeLog(logFile, '\n*****Scan with Sophos - begin*****\n', 'utf-8')
    res = scan(mountPts, readOnly, logFile)
    logManagement.writeLog(logFile, '\n*****Scan with Sophos - finish*****\n', 'utf-8')
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
    cmdline = 'savscan -f -all -rec -sc --stay-on-filesystem --stay-on-machine --backtrack-protection --preserve-backtrack --no-reset-atime --no-reset-atime ' + mountPts + ' > ' + logFile
    # if readOnly == False:
        # Ask user if he wants av to autoclean the device
        # rep = commontools.prompter('Do you want to automaticly clean the device ? (y/n)')
        # if 'y' in str(rep):
            # cmdline = 'clamdscan -v -m --remove --fdpass -l ' + logFile + ' ' + mountPts
        # elif 'n' in str(rep):
            # pass
    print('Scan with Sophos - begin')
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
    Return version informations of Sophos
    '''
    cmdline = 'savscan -v | grep -e "Product version" -e "Engine version" -e "Virus data version" -e "Released"'
    vertemp = str(subprocess.check_output(cmdline, shell = True), 'utf-8').splitlines()
    
    finalrestemp = ""
    dictelemToreplace = {'Product version':'Prod_ver', 
    'Engine version':'/Eng_ver',
    'Virus data version':'/VirusDAT_ver',
    'Released':'/'}
    
    for elem in vertemp:
        for k, v in dictelemToreplace.items():
            if k in elem:
                finalrestemp = finalrestemp + elem.replace(k, v)

    # print(" ".join(finalrestemp.replace(':','').split()))
    return(" ".join(finalrestemp.replace(':','').split()))
    
if __name__ == '__main__':
    version()
