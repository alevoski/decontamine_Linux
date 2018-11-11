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
    
    # Clean the log of not usefull informations
    logManagement.deleter(logFile, 'Using IDE file')
    
    if res == 3:
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
        if '>>> Virus' in line:
            virusName = re.findall('file (.*)', str(line))
            virusType = re.findall("'(.*)'", str(line))
            # print(virusName, virusType)
            virusTEMP[virusName[0]] = virusType[0]
        if 'Removal successful' in line:
            # print('rm : ', line)
            # removedVirus = re.findall('file (.*)', str(line))
            # print(removedVirus)
            lstRemoved.append(virusName[0])
            
    #Compare lstRemoved with virusTEMP:
    # print('Sophos - virus detected\n')
    # print(virusTEMP)
    # print('Sophos - virus removed\n')
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
            0 : No virus and no errors
            1 : Scan interruption
            2 : Errors encounter
            3 : Virus found
    '''
    cmdline = 'savscan -f -all -rec -sc --stay-on-filesystem --stay-on-machine --backtrack-protection --preserve-backtrack --no-reset-atime --no-reset-atime ' + mountPts + ' >> ' + logFile
    if readOnly == False:
        cmdline = 'savscan -remove -f -all -rec -sc --stay-on-filesystem --stay-on-machine --backtrack-protection --preserve-backtrack --no-reset-atime --no-reset-atime ' + mountPts + ' >> ' + logFile
    print('Scan with Sophos - begin')
    try:
        res = str(subprocess.check_output(cmdline, shell = True), 'utf-8')
        print(res)
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
    Return version informations of Sophos
    '''
    # cmdline = 'savscan -v | grep -e "Product version" -e "Engine version" -e "Virus data version" -e "Released"'
    cmdline = 'savscan -v | grep -e "Product version" -e "Engine version" -e "Virus data version" -e "Data file date"'
    vertemp = str(subprocess.check_output(cmdline, shell = True), 'utf-8').splitlines()
    
    finalrestemp = ""
    dictelemToreplace = {'Product version':'Prod_ver', 
    'Engine version':'/Eng_ver',
    'Virus data version':'/VirusDAT_ver',
    'Data file date':'/'}
    
    for elem in vertemp:
        for k, v in dictelemToreplace.items():
            if k in elem:
                if 'Data file date' not in elem:
                    finalrestemp = finalrestemp + elem.replace(k, v)
                else: #'Data file date' in elem
                    lastDatetemp = elem.replace(k, v) #we only want last date in result
    lastDate = re.findall(':(.*)', lastDatetemp)[0]
    # print(lastDate)
    finalres = " ".join(finalrestemp.replace(':','').split()) + '/' + lastDate
    # print(finalres)
    return finalres
    
if __name__ == '__main__':
    version()
