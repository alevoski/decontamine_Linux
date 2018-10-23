#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - analyze.py
#@Alexandre Buissé - 2018

import commontools
import logManagement
from datetime import datetime, timedelta

def init(toolsDict, mountPoint, readOnly, logDirectory):
    '''
    Take the av list and the mounting point to be scan in params,
    Init the scan
    '''
    lstnotRM = []
    lstrm = []
    lstLogAV = []
    for k, v in toolsDict.items():
        print('Init of the scan with ' + k + ' - begin')
        tool = k.lower()
        # try:
        tocall = commontools.import_from(tool, 'init')
        res, logAVTemp = tocall(mountPoint, readOnly, logDirectory)
        lstLogAV.append(logAVTemp)
        if type(res) is dict:
            print(k + ' found something !')
            lstnotRM, lstrm = result(res, lstnotRM, lstrm)
        else:
            print('No virus found with ' + k)
        print('Scan with ' + k + ' - finish')
    return lstnotRM, lstrm, lstLogAV
    
def final(lstnotRM, lstrm, logDirectory):
    '''
    Print the final scan results
    '''
    # print('notRM : ' + str(len(lstnotRM)) + str(lstnotRM))
    # print('RM : ' + str(len(lstrm)) + str(lstrm))
    logFile = logDirectory + 'tempRes'
    finalSummary = '\n' + '-'*5 + ' *****FINAL RESULT***** ' + 5* '-' + '\n'
    logManagement.writeLog(logFile, finalSummary, 'utf-8')
    allVirus = len(lstnotRM) + len(lstrm)
    # print('allvirus : ', allVirus)
    if allVirus > 0:
        if len(lstnotRM) == 0:
            resToShow = 'The ' + str(allVirus) + ' found virus(es) have been removed.'
            for elem in lstrm:
                logManagement.writeLog(logFile, elem + '\n', 'utf-8')
        else:
            resToShow = '\n' + str(allVirus) + ' virus(es) have been detected, ' + str(len(lstrm)) + ' have been removed.'
            for elem in lstnotRM:
                logManagement.writeLog(logFile, elem + '\n', 'utf-8')
            for elem in lstrm:
                logManagement.writeLog(logFile, elem + '\n', 'utf-8')
    else:
        resToShow = 'No virus found on your device.'
        
    allVirusWrite = 'Nb virus found : ' + str(allVirus)
    rmVirusWrite = 'Nb virus removed : ' + str(len(lstrm))
    notrmVirusWrite = 'Nb virus not removed : ' + str(len(lstnotRM))
    logManagement.writeLog(logFile, allVirusWrite + '\n' + rmVirusWrite + '\n' + notrmVirusWrite, 'utf-8')
    logManagement.writeLog(logFile, '\n' + resToShow, 'utf-8')
    print(resToShow)
    
    return logFile
        
def result(res, notRM, rm):
    '''
    Take a virus dictionary and two lists of previously not removed virus and removed virus
    Return lists of virus not removed and virus removed 
    '''
    # print('****')
    # print('res : ', str(res))
    # print('****')
    for k, v in res.items():
        removed = v['removed']
        if removed == 1:
            # print(k, 'removed')
            rm.append(k)
        else:
            # print(k, 'not removed')
            notRM.append(k)
        
    return notRM, rm
        
if __name__ == '__main__':
    lstnotRM = []
    lstrm = []
    dictTestFoundAndDel = {'/media/dev/Win7-AIO-64Bits/virusTest': {'removed': 1, 'type': ' Eicar-Test-Signature '}, '/media/dev/Win7-AIO-64Bits/asdzd': {'removed': 1, 'type': ' Eicar-Test-Signature '}}
    dictTestFoundAndDel2 = {'/media/dev/autres/virusTest55': {'removed': 1, 'type': ' Eicar-Test-Signature '}, '/media/dev/test/machin': {'removed': 1, 'type': ' Eicar-Test-Signature '}}
    dictTestFound = {'/media/dev/Win7-AIO-64Bits/film/waynesworld.avi': {'removed': 0, 'type': ' Trojan_horse '}, '/media/dev/Win7-AIO-64Bits/docs/balance_sheet.xls': {'removed': 0, 'type': ' Malicious VBA '}}
    dictTestFoundPartialDel = {'/media/dev/Win7-AIO-64Bits/docs/other.txt': {'removed': 1, 'type': ' Eicar-Test-Signature '}, '/media/dev/Win7-AIO-64Bits/docs/sdfdfrfd': {'removed': 0, 'type': ' Eicar-Test-Signature '}}
    # lstnotRM, lstrm = result(dictTestFoundAndDel, lstnotRM, lstrm)
    # lstnotRM, lstrm = result(dictTestFoundAndDel2, lstnotRM, lstrm)
    # lstnotRM, lstrm = result(dictTestFound, lstnotRM, lstrm)
    # lstnotRM, lstrm = result(dictTestFoundPartialDel, lstnotRM, lstrm)
    # print(lstnotRM)
    # print(lstrm)
    # final(lstnotRM, lstrm)
    logFilePath1 = "/home/decontamine/LOGS/"+str(datetime.now().strftime('%Y/%m/%d')) + '/' + datetime.now().strftime("%d%m%y%H%M%S")
    logFilePath = logFilePath1+"Log.txt "
    print(logFilePath1)
    print(logFilePath)
    # result(dictTestFound)
    # result(dictTestFoundPartialDel)
    
    
    