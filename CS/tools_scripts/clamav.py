#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - clamav.py
#@Alexandre Buissé - 2018/2020

#Standard imports
import subprocess
import re

#Project modules imports
from commontools import start_proc

def get_virus(log_file):
    '''
    Get virus dict
    '''
    virus_temp_dict = {}
    virus_name = ''
    virus_type = ''
    with open(log_file, mode='r', encoding='utf-8') as log:
        for line in log:
            if 'FOUND' in line:
                virus_name = re.findall('(.*):', str(line))
                virus_type = re.findall(':(.*)FOUND', str(line))
                virus_temp_dict[virus_name[0]] = virus_type[0]
    return virus_temp_dict

def scan(mount_pts, log_file):
    '''
    Scan the mounting point in parameters.
    Return the proc_id
    '''
    cmdline = ['/usr/bin/clamdscan', '-v', '-m', '--fdpass', '-l', log_file, mount_pts]
    proc_id = start_proc(cmdline, 2)
    return proc_id

def version():
    '''
    Return version number of ClamAV
    '''
    ver = str(subprocess.check_output(['/usr/bin/clamdscan', '-V']), 'utf-8')
    return ver.replace('ClamAV ', '').replace('\n', '')

if __name__ == '__main__':
    print(version())
