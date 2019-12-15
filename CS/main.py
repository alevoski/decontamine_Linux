#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - main.py
#@Alexandre Buissé - 2018

#Standard imports
from datetime import datetime
import time
import os
import subprocess
from sys import exit
import getch
from termcolor import colored

#Project modules imports
import stats
import config
import testPreAnalyse
import analyze
import commontools
import logManagement

avcompatibleDict = {'ClamAV':'clamdscan',
                    'Sophos':'savscan',
                    'F-Secure':'fsav'}
# modulescompatibleDict = {}

logDirectory = '/home/decontamine/'

def dismount(mountPTS):
    '''
    Prompt the user to dismount and take back his device
    '''
    rep = commontools.prompter('Do you want to eject and get back your device ? (y/n)')
    if rep in ['y', 'Y']:
        if subprocess.call(['/bin/umount', str(mountPTS)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            print('Success to umount your device !')
        else:
            print('Cannot umount your device !')
        print('Press any key to exit.')
        if getch.getch():
            pass
    elif rep in ['n', 'N']:
        pass

def init():
    '''
    Initialization of the cleaning station
    It's the main function
    '''
    # Verify if logDirectory exists
    if os.path.exists(logDirectory):
        # Clean log directory
        stats.cleanLog(logDirectory)
    else:
        print('ERROR !')
        print('You should create "/home/decontamine" directory to store the logs and the conf file !')
        exit(1)

    print("\x1b[2J\x1b[H",end="") # clear
    # colored('install', 'red', attrs=['bold', 'reverse'])
    projectName = 'Decontamine Linux'
    projectDescription = 'Analyzing and cleaning station:'
    compatibility = '   for optical drives, USB drives, etc.\n'
    configPrint = 'Type "' + colored('C', 'red') + '" to enter the configurator'
    exitPrint = 'Type "' + colored('E', 'red') + '" to exit program'
    print('*'*len(projectName) + 20*('*'))
    print('*'*10 + colored(projectName, attrs=['bold']) + 10*'*')
    print('*'*len(projectName) + 20*('*'))
    print(projectDescription)
    print(compatibility)
    print(configPrint)
    print(exitPrint)
    now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    print("\nBegin: {d}".format(d=now) + '\n')

    #Test if av or scan modules are present on the system and activated
    res = config.init() #will exit program if no tools find
    while res == -1 or res == False:
        init()
    print(colored('Scanning tools activated : ', attrs=['underline']))
    #Get a clean table of scanners activated
    # columnLST = ['Name', 'Version']
    commontools.createTable(res, 'Name', 'Version')

    #Print stats
    nbScan, virusdetected, virusremoved = stats.stat(logDirectory)
    if nbScan > 1:
        print("\n" + colored(str(nbScan), 'yellow') + " devices have been scanned with success.")
    if (nbScan > 1) and (virusdetected > 1):
        phrase = "And " + colored(str(virusdetected), 'yellow') + " viruses have been detected !"
        if virusremoved > 1:
            phrase = phrase + " ( " + colored(str(virusremoved), 'yellow') + " removed !)\n"
        print(phrase)

    while True:
        # Test if drives to analyze
        chosen = 0
        print('\nPlease insert a drive to analyze')
        while chosen == 0:
            rep = commontools.mykbhit()
            if rep in ['c', 'C']:   # Enter config mode
                print("\x1b[2J\x1b[H",end="") # clear
                rep = config.configurator(avcompatibleDict)
                init()
            if rep in ['e', 'E']:   # Exit
                exit(1)

            chosen, deviceDict = testPreAnalyse.init() # Will not take any user input during the test
        # print(chosen, deviceDict)

        # Get device attributs
        label, mountpoint, readonly = testPreAnalyse.depackedDeviceDict(deviceDict)

        if mountpoint != '':
            logFilePath1 = logDirectory + 'LOGS/{}'.format(datetime.now().strftime('%Y/%m/%d'))
            logFilePath1 += '/' + datetime.now().strftime("%d%m%y%H%M%S")
            logFilePath = logFilePath1+"Log.txt"

            print('\n' + '_'*30 + '\n')
            print('Device {} detected'.format(label))
            if readonly == 1:
                print('\n {} is read-only, '.format(label) + colored('it will be impossible to remove viruses !', attrs=['bold']))

            element1 = "-------------------------Device scanned : ''"+str(label)+"'' --------------\n"
            element1b = "-------------------------Read-only : "+str(readonly)+" --------------\n"
            element1c = "-------------------------Station : ''"+os.uname()[1]+"'' --------------\n"
            element2 = "-------------------------"+str(datetime.now().strftime("%A %d %B %Y %H:%M:%S"))+"--------------\n"
            element = element1+element1b+element1c+element2
            logManagement.writeLog(logFilePath, element, 'utf-8')#write logfile

            # Get files
            test = 1
            while test < 30:
                beginScan = time.time()
                filesLst = testPreAnalyse.getFiles(mountpoint)
                if len(filesLst) > 0:
                    # print(filesLst)
                    filePrint = '{} files to analyze on the device "{}"'.format(len(filesLst), label)
                    print(colored(str(len(filesLst)), 'yellow') + ' files to analyze on the device "{}"'.format(label))
                    logManagement.writeLog(logFilePath, filePrint+'\n', 'utf-8')
                    for files in filesLst:
                        logManagement.writeLog(logFilePath, files+'\n', 'utf-8')
                    test = 30
                    break
                if test == 29:#no files
                    print('No files to analyze on the device "{}"'.format(label))
                time.sleep(0.5) #Let the time for the system to get the files
                test += 1
            if len(filesLst) > 0:
                print('\nBeginning of the analyze, please wait !')
                # 1 - init scanning tools
                lstnotRM, lstrm, lstLogAV = analyze.init(res, mountpoint, readonly, logFilePath1)

                # 2 - print scan results
                print('\n' + '_'*30 + '\n')
                print(colored('Analyze is finished !', attrs=['bold']))
                logFinalTemp = analyze.final(lstnotRM, lstrm, logFilePath1)

                endScan = time.time()
                totalTimeScan = endScan - beginScan
                totalTime = 'Device analyzed in {} seconds.'.format(round(totalTimeScan, 5))
                print('Device analyzed in ' + colored(str(round(totalTimeScan, 5)), 'yellow') + ' seconds.\n')
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

                # 7 - Reload the process
                init()

if __name__ == '__main__':
    init()
