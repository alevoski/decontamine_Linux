#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - sophos.py
#@Alexandre Buissé - 2018/2020

'''
Scanning module : Sophos antivirus
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
    # cmdline = ['/usr/local/bin/savscan', '-f', '-all', '-rec', '-sc', '--stay-on-filesystem', '--stay-on-machine', '--backtrack-protection', '--preserve-backtrack', '--no-reset-atime', mount_pts, '-p='+ log_file]
    cmdline = ['/usr/local/bin/savscan', '-q', '-all', '-rec', '-sc', '--stay-on-filesystem', '--stay-on-machine', '--backtrack-protection', '--preserve-backtrack', '--no-reset-atime', mount_pts, '-p='+ log_file]
    proc_id = start_proc('Sophos', cmdline, 2)
    return proc_id

def version():
    '''
    Return version informations of Sophos
    '''
    # cmdline = 'savscan -v | grep -e "Product version" -e "Engine version" -e "Virus data version" -e "Released"'
    # cmdline = 'savscan -v | grep -e "Product version" -e "Engine version" -e "Virus data version" -e "Data file date"'
    vertemp = str(subprocess.check_output(['/usr/local/bin/savscan', '-v']), 'utf-8')

    # Get Product version
    pver = 'Prod_ver ' + str(re.findall('Product version *: (.*)', vertemp)[0])

    # Get Engine version
    ever = '/Eng_ver ' + str(re.findall('Engine version *: (.*)', vertemp)[0])

    # Get Virus data version
    vdata = '/VirusDAT_ver ' + str(re.findall('Virus data version *: (.*)', vertemp)[0])

    # Get Virus data version
    vdate = '/ ' + str(re.findall('Data file date *: (.*)', vertemp)[-1])

    finalres = pver + ever + vdata + vdate

    # print(finalres)
    return finalres

if __name__ == '__main__':
    version()
