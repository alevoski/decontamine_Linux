#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - f-secure.py
#@Alexandre Buissé - 2018

import commontools
import logManagement
import subprocess
import re

def init(mountPts, readOnly, logDirectory):
    '''
    Init scan with F-Secure
    '''
    logFile = logDirectory + 'tempF-SecureAV'
    logManagement.writeLog(logFile, '\n*****Scan with F-Secure - begin*****\n', 'utf-8')
    res = scan(mountPts, readOnly, logFile)
    logManagement.writeLog(logFile, '\n*****Scan with F-Secure - finish*****\n', 'utf-8')
    
    # Clean the log of not usefull informations
    # logManagement.deleter(logFile, 'Using IDE file')
    
    if res == 3 or res == 4 or res == 6 or res == 8:
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
    Return a code
        0      Normal exit; no viruses or suspicious files found.
        1      Fatal error; unrecoverable error.  (Usually a missing or corrupted file.)
        3      A boot virus or file virus found.
        4      Riskware (potential spyware) found.
        6      At least one virus was removed and no infected files left.
        7      Out of memory.
        8      Suspicious files found; these are not necessarily infected by a virus.
        9      Scan error, at least one file scan failed.
        64 + return code above
        Program was prematurely terminated by SIGIN after  something  abnormal  already
        had been detected. Usually this means that the user pressed CTRL-C (64 means we
        set the 7th bit to 1)
        128 + signal number
        Program was terminated by pressing CTRL-C, or by a sigterm or suspend event.
    '''
    cmdline = 'fsav --virus-action1=report --allfiles --archive --maxnested=15 --scantimeout=180 ' + mountPts + ' >> ' + logFile
    if readOnly == False:
        #Ask user if he wants av to autoclean the device
        rep = commontools.prompter('Do you want to automaticly clean the device ? (y/n)')
        if 'y' in str(rep):
            cmdline = 'fsav --virus-action1=clean --virus-action2=remove --auto --allfiles --archive --maxnested=15 --scantimeout=180 ' + mountPts + ' >> ' + logFile
    print('Scan begin')
    try:
        res = str(subprocess.check_output(cmdline, shell = True), 'utf-8')
        # print(res)
        # p = re.findall('Infected files:*?(\d+)', str(res))
        return 0
    except subprocess.CalledProcessError as e:#Error
        # print(e)
        p = re.findall('exit status.*?(\d+)', str(e))
        # print(p)
        # print(int(p[0]))
        # print(type(p[0]))

    return int(p[0])

def version():
    '''
    Return version informations of F-Secure
    '''
    cmdline = 'fsav --version | grep -e "Security version" -e "Hydra engine version" -e "Hydra database version"'
    vertemp = str(subprocess.check_output(cmdline, shell = True), 'utf-8').splitlines()
    
    finalrestemp = ""
    dictelemToreplace = {'F-Secure Linux Security version':'Prod_ver', 
    'F-Secure Corporation Hydra engine version':'/Eng_ver',
    'F-Secure Corporation Hydra database version ':'/'}
    
    for elem in vertemp:
        for k, v in dictelemToreplace.items():
            if k in elem:
                finalrestemp = finalrestemp + elem.replace(k, v)
    # print(finalrestemp)
    finalres = " ".join(finalrestemp.replace(':','').split())
    # print(finalres)
    return finalres
    
if __name__ == '__main__':
    version()
