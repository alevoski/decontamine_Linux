#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - main.py
#@Alexandre Buiss� - 2018

import stats
import config
import testPreAnalyse
import analyze
import commontools
import logManagement
from termcolor import colored
from datetime import datetime, timedelta
import time
import getch
import sys
import os

avcompatibleDict = {'ClamAV':'clamdscan',
'Sophos':'sophos'}
modulescompatibleDict = {}

logDirectory = '/home/decontamine/'

def dismount(mountPTS):
    '''
    Prompt the user to get a copy of the final log
    '''
    rep = commontools.prompter('Do you want to eject and get back your device ? (y/n)')
    if 'y' in str(rep):
        os.system("umount "+str(mountPTS))
        print('Tape a key to exit.')
        if getch.getch():
            pass
    elif 'n' in str(rep):
        pass 

def init():
    '''
    Initialisation of the cleaning station
    '''
    #Clean log directory
    stats.cleanLog(logDirectory)
    
    os.system('clear')
    # colored('install', 'red', attrs=['bold', 'reverse'])
    projectName = 'Decontamine Linux'
    projectDescription = 'Analyzing and cleaning station:'
    compatibility = '   for optical drives, USB drives, etc.'
    configPrint = 'Type "' + colored('C', 'red') + '" to enter the configurator'
    print('*'*len(projectName) + 20*('*'))
    print('*'*10 + colored(projectName, attrs=['bold']) + 10*'*')
    print('*'*len(projectName) + 20*('*'))
    print(projectDescription)
    print(compatibility)
    print(configPrint)
    now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    print("\nBegin: {d}".format(d=now) + '\n')
    
    begin = datetime.now()
    
    #Test if av or scan modules are present on the system and activated
    res = config.init() #will exit program if no tools find
    if res == -1:
        init()
    print(colored('Scanning tools activated : ', attrs=['underline']))
    #Get a clean table of scanners activated
    # columnLST = ['Name', 'Version']
    commontools.createTable(res, 'Name', 'Version')
    # print(colored('Name - Version', attrs=['bold']))
    # for tool, version in res.items():
        # print(tool + ' - ' + version) 
        
    #Print stats
    nbScan, virusdetected, virusremoved = stats.stat(logDirectory)
    if nbScan > 1:
        print("\n" + str(nbScan)+" devices have been scanned with success.")
    if (nbScan > 1) and (virusdetected > 1):
        phrase = "And "+str(virusdetected)+" viruses have been detected !"
        if (virusremoved > 1):
            phrase = phrase + " ( "+str(virusremoved)+ " removed !)\n"
        print(phrase)
    
    while True:

        #Test if drives to analyze
        chosen = 0
        print('\nPlease insert a drive to analyze')
        while chosen == 0:

            if commontools.mykbhit():
                rep = getch.getch()
                print(rep)
                if 'c' in str(rep):#enter config mode
                    os.system('clear')
                    rep = config.configurator(avcompatibleDict)
                    init()
                
            chosen, deviceDict = testPreAnalyse.init()
        # print(deviceDict)
        
        #Get device attributs
        label, mountpoint, readonly = testPreAnalyse.depackedDeviceDict(deviceDict)
        
        if mountpoint != '':
            
            logFilePath1 = logDirectory + '/LOGS/' + str(datetime.now().strftime('%Y/%m/%d')) + '/' + datetime.now().strftime("%d%m%y%H%M%S")
            logFilePath = logFilePath1+"Log.txt "
        
            print('Device ' + label + ' detected')
            if readonly == 1:
                print('\n' + label + ' is read-only, it will be impossible to remove viruses !')

            element1 = "-------------------------Device scanned : ''"+str(label)+"'' --------------\n"
            element1b = "-------------------------Read-only : "+str(readonly)+" --------------\n"
            element1c = "-------------------------Station : ''"+os.uname()[1]+"'' --------------\n"
            element2 = "-------------------------"+str(datetime.now().strftime("%A %d %B %Y %H:%M:%S"))+"--------------\n"
            element = element1+element1b+element1c+element2
            logManagement.writeLog(logFilePath, element, 'utf-8')#write logfile
        
            #Get files
            test = 1
            while test < 30: 
                beginScan = time.time()
                filesLst = testPreAnalyse.getFiles(mountpoint)
                if len(filesLst) > 0:
                    # print(filesLst)
                    filePrint = str(len(filesLst)) + ' files to analyze on the device "' + label + '"'
                    print(filePrint)
                    logManagement.writeLog(logFilePath, filePrint+'\n', 'utf-8')
                    for files in filesLst:
                        logManagement.writeLog(logFilePath, files+'\n', 'utf-8')
                    test = 30
                    break
                if test == 29:#no files
                    print('No files to analyze on the device "' + label + '"')
                time.sleep(0.5) #Let the time for the system to get the files
                test +=1
            if len(filesLst) > 0:
                print('Beginning of the analyze, please wait !')
                # 1 - init scanning tools
                lstnotRM, lstrm, lstLogAV = analyze.init(res, mountpoint, readonly, logFilePath1)
                
                # 2 - print scan results
                logFinalTemp = analyze.final(lstnotRM, lstrm, logFilePath1)
                
                endScan = time.time()
                totalTimeScan = endScan - beginScan
                totalTime = 'Device analyze in '+str(round(totalTimeScan, 5)) + ' seconds.'
                print(totalTime)
                logManagement.writeLog(logFinalTemp, '\n'+totalTime, 'utf-8')
                
                # 3 - concat all logs in one final log
                allLogs = []
                allLogs = logManagement.concat(logFilePath, allLogs)
                allLogs = logManagement.concat(lstLogAV, allLogs)
                allLogs = logManagement.concat(logFinalTemp, allLogs)
                # print(allLogs)
                finalLog = os.path.dirname(logFilePath) + "/" + os.uname()[1] + "_FINAL-" + os.path.basename(logFilePath)
                # print(finalLog)
                logManagement.writeFinalLog(finalLog, allLogs)               
                
                # 4 - Prompt the user to read the detail of the final result
                logManagement.readLog(finalLog)
                
                # 5 - Prompt the user to get a copy of the final result
                if readonly == 0:
                    logManagement.getLog(finalLog, mountpoint)
                
                # 6 - Prompt the user to dismount and take back his device
                dismount(mountpoint)
                
                # sys.exit()
                init()
    

if __name__ == '__main__':
    init()
    
