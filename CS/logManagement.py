#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - logManagement.py
#@Alexandre Buissé - 2018

import commontools
import re
import os
import shutil
import getch
import subprocess

def extractSTR(line, mystrRGX):
    '''Extract str'''
    # p = re.search(')
    # mystrRGX = 'av_name = '#"([^"]+)"'
    temp = re.split(mystrRGX, line)[-1]
    # print(temp)
    return temp.replace('\n','')
    
def writeLog(logFile, element, codec):
    '''Write log on the station'''
    # print(repr(element))
    #Create a directory where all the logs will be stored
    dirToCreate = os.path.dirname(os.path.abspath(logFile))
    # print (dirToCreate)
    if not os.path.exists(dirToCreate):
        os.makedirs(dirToCreate)
    try:
        f = open(logFile, 'a', encoding=codec, errors='ignore')
        # print(element)
        f.write(element)
        f.close()
    except Exception:
        print("Can't write the file ",logFile, " with this element : " + str(element))
        pass
        
def writeFinalLog(concatenateBasesFiles, fileLst):
    '''
    Concatenate log files in one final log file
    Take the path to write the final log and the list of log files
    '''
    finalFile = open(concatenateBasesFiles, 'w', errors='ignore', encoding='utf-8')
    # print ("fichier final test : "+str(concatenateBasesFiles)) #ok

    for i in fileLst:
        while os.path.isfile(i):
            # print ("testFile : "+str(i)) #ok
            shutil.copyfileobj(open(i, 'r', errors='ignore', encoding='utf-8'), finalFile)
            try:
                # i.close() #surtout pas, engendre une erreur qui génère de très gros fichiers !!
                os.remove(i) #suppression des fichiers concaténés
            except Exception:#OSError:
                continue
    finalFile.close()
    
def concat(theFile, theList):
    '''
    Append a file to a list
    '''
    if type(theFile) is list:
        for logs in theFile:
            theList.append(logs)
    else:
        theList.append(theFile)
    return theList
    
def readLog(finalLog):
    '''
    Prompt the user to read the final log
    '''
    rep = commontools.prompter('Do you want to read the detail of the scan ? (y/n)')
    if 'y' in str(rep):
        subprocess.call(('xdg-open', str(finalLog)))
    elif 'n' in str(rep):
        pass 

def getLog(finalLog, mountPTS):
    '''
    Prompt the user to get a copy of the final log
    '''
    rep = commontools.prompter('Do you want a copy of the detail of the scan ? (y/n)')
    if 'y' in str(rep):
        shutil.copy(finalLog, mountPTS)
        copiedFile = mountPTS + '/' + os.path.basename(finalLog)
        # print(copiedFile)
        if os.path.isfile(copiedFile):
            print('The result of the scan have been copied on the device ' + mountPTS)
    elif 'n' in str(rep):
        pass 
    
    