#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - clamav.py
#@Alexandre Buissé - 2018/2020

#Standard imports
import subprocess
import re

#Project modules imports
from commontools import prompter, start_proc, status_proc, wait_and_check, compare_virus
from logmanagement import writelog


def init(mount_pts, read_only, log_file_path):
    '''
    Init scan with ClamAV
    '''
    log_file = log_file_path + 'tempClamAV'
    writelog(log_file, '\n*****Scan with ClamAV - begin*****\n', 'utf-8')
    status_code = scan(mount_pts, read_only, log_file)
    ending_sentence = '*****Scan with ClamAV - finish*****\n'
    if status_code == -15:
        ending_sentence = '*****Scan with ClamAV has been stopped*****\n'
    writelog(log_file, ending_sentence, 'utf-8')
    if status_code in (1, -15):
        virus_dict = get_virus(log_file)
        # print(virus_dict)
        return status_code, virus_dict, log_file
    return status_code, 0, log_file

def get_virus(log_file):
    '''
    Get virus dict
    '''
    virus_temp_dict = {}
    virus_name = ''
    virus_type = ''
    removed_list = []
    with open(log_file, mode='r', encoding='utf-8') as log:
        for line in log:
            if 'FOUND' in line:
                virus_name = re.findall('(.*):', str(line))
                virus_type = re.findall(':(.*)FOUND', str(line))
                virus_temp_dict[virus_name[0]] = virus_type[0]
            if 'Removed' in line:
                # print('rm : ', line)
                removed_virus = re.findall('(.*):', str(line))
                # print(removed_virus)
                removed_list.append(removed_virus[0])

    # Compare removed_list with virus_temp_dict:
    virus_dict = compare_virus(removed_list, virus_temp_dict)
    return virus_dict

def scan(mount_pts, read_only, log_file):
    '''
    Scan the mounting point in parameters.
    Return
        a code
            0 : No virus
            1 : Virus found
            2 : Error
            -15 : Scan stopped by user
    '''
    cmdline = ['/usr/bin/clamdscan', '-v', '-m', '--fdpass', '-l', log_file, mount_pts]
    if not read_only:
        #Ask user if he wants av to autoclean the device
        rep = prompter('Do you want to automaticly clean the device ? (y/n)')
        if 'y' in str(rep):
            cmdline = ['/usr/bin/clamdscan', '-v', '-m', '--remove', '--fdpass', '-l', log_file, mount_pts]
        elif 'n' in str(rep):
            pass
    print('Scan begin')
    try:
        print("Press 's' to stop the scan")
        proc_id = start_proc(cmdline, 1)
        proc_status = status_proc(proc_id)
        # print('status', proc_status)
        wait_and_check(proc_status, proc_id)
        proc_status = status_proc(proc_id)
        # print('status', proc_status)
        return proc_status
    except subprocess.CalledProcessError as exception: # Error
        proc_status = re.findall(r'exit status.*?(\d+)', str(exception))
    return int(proc_status[0])

def version():
    '''
    Return version number of ClamAV
    '''
    ver = str(subprocess.check_output(['/usr/bin/clamdscan', '-V']), 'utf-8')
    return ver.replace('ClamAV ', '').replace('\n', '')

if __name__ == '__main__':
    print(version())
