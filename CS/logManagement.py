#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - logManagement.py
#@Alexandre Buissé - 2018

#Standard imports
import re
import os
import shutil
import subprocess
import fileinput

#Project modules imports
from commontools import prompter

def extractSTR(line, mystrRGX):
    '''Extract str'''
    # p = re.search(')
    # mystrRGX = 'av_name = '#"([^"]+)"'
    temp = re.split(mystrRGX, line)[-1]
    # print(temp)
    return temp.replace('\n', '')

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
    except Exception:
        print("Can't write the file {} with this element : {}".format(logFile, element))
    finally:
        f.close()


def writeFinalLog(concatenateBasesFiles, fileLst):
    '''
    Concatenate log files in one final log file
    Take the path to write the final log and the list of log files
    '''
#    finalFile = open(concatenateBasesFiles, 'w', errors='ignore', encoding='utf-8')
    with open(concatenateBasesFiles, 'w', errors='ignore', encoding='utf-8') as finalFile:
        # print ("fichier final test : "+str(concatenateBasesFiles)) #ok

        for i in fileLst:
            while os.path.isfile(i):
                # print ("testFile : "+str(i)) #ok
                shutil.copyfileobj(open(i, 'r', errors='ignore', encoding='utf-8'), finalFile)
                try:
                    # i.close() #NEVER decomment : could create a very big file in an infinite loop
                    os.remove(i) #remove concatenated file
                except Exception:#OSError:
                    continue
#    finalFile.close()

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
    rep = prompter('Do you want to read the detail of the scan ? (y/n)')
    if rep == 'y':
        subprocess.call(('xdg-open', str(finalLog)))
    elif rep == 'n':
        pass

def getLog(finalLog, mountPTS):
    '''
    Prompt the user to get a copy of the final log
    '''
    rep = prompter('Do you want a copy of the detail of the scan ? (y/n)')
    if rep == 'y':
        copiedFile = mountPTS + '/' + os.path.basename(finalLog)
        # print(finalLog)
        shutil.copy2(finalLog, copiedFile)
        # print(copiedFile)
        if os.path.isfile(copiedFile):
            print('The result of the scan have been copied on the device ' + mountPTS)
    elif rep == 'n':
        pass

def replacer(logfile, elemOri, elem):
    '''Replace elemOri with elem in logfile'''
    with open(logfile, 'r') as f:
        filedata = f.read()

    newdata = filedata.replace(elemOri, elem)

    with open(logfile, 'w') as f:
        f.write(newdata)

def deleter(logfile, elem):
    '''Delete line containing elem in logfile'''
    for line in fileinput.input(logfile, inplace=True):
        if not re.search(elem, line):
            print(line, end='')
