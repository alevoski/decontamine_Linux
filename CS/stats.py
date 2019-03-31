#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - stats.py
#@Alexandre Buissé - 2018

#Standard imports
import os

#Project modules imports
from commontools import extractNumber

def stat(fileLogs):
    '''
    Count and return the number of files and the number of virus in the directory passed in parameter with globalStat()
    '''
    nbcount = []
    statVirusD = 0
    statVirus = 0
    for root, dirnames, filenames in os.walk(fileLogs + 'LOGS/'):
        for files in filenames:
            # print(files)
            theDir = str(dirnames).replace("[]", "/")
            filePath = os.path.abspath(str(root)+str(theDir)+str(files))
            if "FINAL" in files:
                nbcount.append(files)
            # print(nbcount)
            # print(filePath)
            #removed viruses
            try:
                nbVirusDetect, nbVirusDel = globalStat(filePath)
            except UnicodeDecodeError:
                continue
            # print("virus per files  : ", nbVirusDel, filePath)
            statVirusD = statVirusD + nbVirusDetect
            statVirus = statVirus + nbVirusDel
    return len(nbcount), statVirusD, statVirus

def globalStat(files):
    '''
    Get and return the number of virus detected and the number of virus removed with the log file passed in parameter
    '''
    nbVirusDetect = 0
    nbVirusDel = 0

    # @Alex : f.close() cant be forgotten (https://docs.python.org/3/tutorial/errors.html - 8.7)
    with open(files, 'r', encoding='utf-8') as f:
        for line in f:
            # print(line)
            if "Nb virus found" in line:
                nbVirusDetect = extractNumber(line)
                # print(str(files)+' nbVirusDetect:'+str(nbVirusDetect))
            if "Nb virus removed" in line:
                nbVirusDel = extractNumber(line)
                # print(str(files)+' nbVirusDel:'+str(nbVirusDel))
    return nbVirusDetect, nbVirusDel

def cleanLog(logDir):
    '''Clean the log directory'''
    for root, dirnames, filenames in os.walk(logDir + 'LOGS/'):
        # print ("files :"+str(filenames))
        #Deleted not finalized logs or empty logs
        for files in filenames:
            theDir = str(dirnames).replace("[]", "/")
            filePath = os.path.abspath(str(root)+str(theDir)+str(files))
            # print(os.path.getsize(filePath)) #test ok
            if ("FINAL" in files or "STAT" in files) and (os.path.getsize(filePath) != 0):
                # print("ok")
                pass
            else:
                # print(files," supress")
                try:
                    os.remove(os.path.abspath(filePath))
                except Exception:
                    pass

        #Removed empty directories
        for theDir in dirnames:
            subdirpath = os.path.abspath(str(root)+"/"+str(theDir))
            # print(subdirpath)
            if os.listdir(subdirpath) == []:
                # print("vide",subdirpath) #ok
                try:
                    os.rmdir(subdirpath)
                except Exception:
                    pass

if __name__ == '__main__':
    nbScan, virusdetected, virusremoved = stat('/home/decontamine/')
