#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - commontools.py
#@Alexandre Buissé - 2018

#Standard imports
import re
import getch
import subprocess
from termcolor import colored

#Project modules imports
import kbhitClass

def import_from(module, name):
    '''
    Do a dynamic import bases on variables
    '''
    module = __import__(module, fromlist=[name])
    return getattr(module, name)

def mykbhit():
    '''
    Detect a key press by user
    '''
    kb = kbhitClass.KBHit()

    # print('Hit any key, or ESC to exit')

    test = 1
    while test < 15000:
        # print(test)
        if kb.kbhit():
            c = kb.getch()
            # print(c)
            return c
        test += 1

def createTable(theDict, column1, column2):
    '''
    Create a table
    '''

    max1 = 0
    max2 = 0

    for item, value in theDict.items():
        # max len()
        if len(item) > max1:
            max1 = len(item)
        if len(value) > max2:
            max2 = len(value)

    #Table headers
    diffMax1 = max1-len(column1)
    max1Header = column1+" "*diffMax1+"| "

    diffMax2 = max2-len(column2)
    max2Header = column2+" "*diffMax2+"|"

    header = max1Header + max2Header
    limHeader = "-"*max1 + "-"*max2
    print(colored(header, attrs=['bold']))
    print(limHeader)

    #Table values
    for item, value in theDict.items():
        # print(item)
        diffMax1 = max1-len(item)
        theItem = item +" "*diffMax1

        diffMax2 = max2-len(value)
        theValue = value +" "*diffMax2

        print(colored(theItem, 'green') + "|" + colored(theValue, 'magenta'))

def extractNumber(line):
    '''Extract number dans rapport'''
    try:
        p = re.search('[0-9]+', line)
        # print(repr(line), repr(p.group(0)))
        return int(p.group(0))
    except Exception:
        return 0

def prompter(toAsk):
    '''
    Prompt user, return the answer
    '''
    while True:
        print(toAsk)
        rep = str(getch.getch())
        if rep in ['y', 'n']:
            break
    return rep

def startPROC(procname, mode, fwrite=''):
    '''
    Start a process and return its process id
    '''
    if mode == 1: # non blocking mode
        proc = subprocess.Popen(procname, shell=False)
    elif mode == 2: # non blocking mode + redirect stdout
        proc = subprocess.Popen(procname, stdout=fwrite, shell=False)
    else:
        proc = subprocess.check_output([procname]) # Blocking call
    return proc

def statusPROC(proc):
    '''
    Return process status code
    '''
    return proc.poll()

def stopPROC(proc):
    '''
    Kill a process and wait until it terminate
    '''
    # proc.kill()
    proc.terminate()
    proc.wait()

def waitandcheck(procStatus, procID):
    '''
    Wait for process to terminate itself
    Meanwhile, check if user wants to stop process
    '''
    while procStatus == None:
        procStatus = statusPROC(procID)
        if procStatus != None:
            break
        if mykbhit() in ['s', 'S']:
            stopPROC(procID)

#https://repolinux.wordpress.com/2012/10/09/non-blocking-read-from-stdin-in-python/
