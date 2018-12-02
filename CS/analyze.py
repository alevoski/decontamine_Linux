#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - analyze.py
#@Alexandre Buissé - 2018

from commontools import import_from
import logManagement
from datetime import datetime, timedelta
from termcolor import colored

def init(toolsDict, mountPoint, readOnly, logDirectory):
    '''
    Take the av list and the mounting point to be scan in params,
    Init the scan
    '''
    detected = []
    lstrm = []
    lstLogAV = []
    for k, v in toolsDict.items():
        print('\n' + colored('Init of the scan with ' + colored(k, 'green'), attrs=['bold']))
        tool = k.lower()
        toolPath = 'tools_scripts'
        # try:
        tocall = import_from(toolPath, tool)
        res, logAVTemp = tocall.init(mountPoint, readOnly, logDirectory)
        lstLogAV.append(logAVTemp)
        if type(res) is dict:
            print('\n'+colored(k, 'green') + ' found something !')
            detected, lstrm = result(res, detected, lstrm)
        else:
            print('\nNo virus found with ' + colored(k, 'green'))
        print(colored('Scan finished with ' + colored(k, 'green'), attrs=['bold']))
    return detected, lstrm, lstLogAV
    
def final(detected, lstrm, logDirectory):
    '''
    Print the final scan results
    '''
    # print('notRM : ' + str(len(detected)) + str(detected))
    # print('RM : ' + str(len(lstrm)) + str(lstrm))
    logFile = logDirectory + 'tempRes'
    finalSummary = '\n' + '-'*5 + ' *****FINAL RESULT***** ' + 5* '-' + '\n'
    logManagement.writeLog(logFile, finalSummary, 'utf-8')
    
    allVirus = len(detected)
    # allVirus = 0
    # for notrmvirus in detected:
        # if notrmvirus not in lstrm:
            # allVirus +=1
            
    
    # print('allvirus : ', allVirus)
    if allVirus > 0:
        if len(lstrm) == len(detected):
            resToShow = 'The ' + str(allVirus) + ' found virus(es) was/were removed.'
            for elem in lstrm:
                logManagement.writeLog(logFile, elem + '\n', 'utf-8')
        else:
            resToShow = '\n' + str(allVirus) + ' virus(es) detected, ' + str(len(lstrm)) + ' removed.'
            for elem in detected:
                logManagement.writeLog(logFile, elem + '\n', 'utf-8')
            for elem in lstrm:
                logManagement.writeLog(logFile, elem + '\n', 'utf-8')
    else:
        resToShow = 'No virus found on your device.'
        
    allVirusWrite = 'Nb virus found : ' + str(allVirus)
    rmVirusWrite = 'Nb virus removed : ' + str(len(lstrm))
    notremove = len(detected) - len(lstrm)
    notrmVirusWrite = 'Nb virus not removed : ' + str(notremove)
    logManagement.writeLog(logFile, allVirusWrite + '\n' + rmVirusWrite + '\n' + notrmVirusWrite, 'utf-8')
    logManagement.writeLog(logFile, '\n' + resToShow, 'utf-8')
    print(colored(resToShow, attrs=['bold']))
    
    return logFile
        
def result(res, detected, rm):
    '''
    Take a virus dictionary and two lists of previously not removed virus and removed virus
    Return lists of virus detected and virus removed 
    '''
    # print('****')
    # print('res : ', str(res))
    # print('****')
    for k, v in res.items():
        # Patched to avoid double counts when multiple av tools scan a device
        # print(k)
        removed = v['removed']
        if removed == 1:
            if k not in rm: 
                # print(k, 'removed')
                rm.append(k)
        # else:
        if k not in detected:
            # print(k, 'detected')
            detected.append(k)
        
    return detected, rm
        
if __name__ == '__main__':
    detected = []
    lstrm = []
    dictTestFoundAndDel = {'/media/dev/Win7-AIO-64Bits/virusTest': {'removed': 1, 'type': ' Eicar-Test-Signature '}, '/media/dev/Win7-AIO-64Bits/asdzd': {'removed': 1, 'type': ' Eicar-Test-Signature '}}
    dictTestFoundAndDel2 = {'/media/dev/autres/virusTest55': {'removed': 1, 'type': ' Eicar-Test-Signature '}, '/media/dev/test/machin': {'removed': 1, 'type': ' Eicar-Test-Signature '}}
    dictTestFound = {'/media/dev/Win7-AIO-64Bits/film/waynesworld.avi': {'removed': 0, 'type': ' Trojan_horse '}, '/media/dev/Win7-AIO-64Bits/docs/balance_sheet.xls': {'removed': 0, 'type': ' Malicious VBA '}}
    dictTestFoundPartialDel = {'/media/dev/Win7-AIO-64Bits/docs/other.txt': {'removed': 1, 'type': ' Eicar-Test-Signature '}, '/media/dev/Win7-AIO-64Bits/docs/sdfdfrfd': {'removed': 0, 'type': ' Eicar-Test-Signature '}}
    # detected, lstrm = result(dictTestFoundAndDel, detected, lstrm)
    # detected, lstrm = result(dictTestFoundAndDel2, detected, lstrm)
    # detected, lstrm = result(dictTestFound, detected, lstrm)
    # detected, lstrm = result(dictTestFoundPartialDel, detected, lstrm)
    # print(detected)
    # print(lstrm)
    # final(detected, lstrm)
    logFilePath1 = "/home/decontamine/LOGS/"+str(datetime.now().strftime('%Y/%m/%d')) + '/' + datetime.now().strftime("%d%m%y%H%M%S")
    logFilePath = logFilePath1+"Log.txt "
    print(logFilePath1)
    print(logFilePath)
    # result(dictTestFound)
    # result(dictTestFoundPartialDel)
    
    
    