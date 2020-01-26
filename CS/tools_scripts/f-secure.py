#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - f-secure.py
#@Alexandre Buissé - 2018/2020

'''
Scanning module : F-Secure antivirus
'''

#Standard imports
import subprocess
import re

#Project modules imports
from commontools import start_proc

def scan(mount_pts, log_file):
    '''
    Scan the mounting point in parameters.
    Return the proc_id
    '''
    cmdline = ['/usr/bin/fsav', '--virus-action1=report', '--allfiles', '--archive', '--maxnested=15', '--scantimeout=180', mount_pts]
    with open(log_file, mode='w', encoding='utf-8') as flog:
        proc_id = start_proc(cmdline, 2, flog)
    return proc_id

def version():
    '''
    Return version informations of F-Secure
    '''
    try:
        # cmdline = 'fsav --version | grep -e "Security version" -e "Hydra engine version" -e "Hydra database version"'
        vertemp = str(subprocess.check_output(['/usr/bin/fsav', '--version']), 'utf-8')

        # Get Product version
        pver = 'Prod_ver ' + str(re.findall('F-Secure Linux Security version (.*)', vertemp)[0])

        # Get Engine version
        ever = '/Eng_ver ' + str(re.findall('F-Secure Corporation Hydra engine version (.*)', vertemp)[0])

        # Get last update date
        vdata = '/VirusDAT_ver ' + str(re.findall('F-Secure Corporation Hydra database version (.*)', vertemp)[0])

        finalres = pver + ever + vdata

        # print(finalres)
        return finalres
    except subprocess.CalledProcessError:
        return "Evaluation version"

if __name__ == '__main__':
    version()
