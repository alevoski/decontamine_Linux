#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - clamav.py
#@Alexandre Buissé - 2018/2020

'''
Scanning module : ClamAV antivirus
'''

#Standard imports
import subprocess

#Project modules imports
from commontools import start_proc

def scan(mount_pts, log_file):
    '''
    Scan the mounting point in parameters.
    Return the proc_id
    '''
    cmdline = ['/usr/bin/clamdscan', '-v', '-m', '--fdpass', '-l', log_file, mount_pts]
    proc_id = start_proc('ClamAV', cmdline, 2)
    return proc_id

def version():
    '''
    Return version number of ClamAV
    '''
    ver = str(subprocess.check_output(['/usr/bin/clamdscan', '-V']), 'utf-8')
    return ver.replace('ClamAV ', '').replace('\n', '')

if __name__ == '__main__':
    print(version())
