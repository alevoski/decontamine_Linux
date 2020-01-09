#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - f-secure.py
#@Alexandre Buissé - 2018/2020

#Standard imports
import subprocess
import re

#Project modules imports
from commontools import prompter, start_proc, status_proc, wait_and_check, compare_virus
from logmanagement import writelog, write_first_line

def init(mount_pts, read_only, log_file_path):
    '''
    Init scan with F-Secure
    '''
    log_file = log_file_path + 'tempF-SecureAV'
    status_code = scan(mount_pts, read_only, log_file)
    ending_sentence = '*****Scan with F-Secure - finish*****\n'
    write_first_line(log_file, '\n*****Scan with F-Secure - begin*****\n')

    if status_code == 143:
        status_code = -15 # Change with a commonly shared status code
        ending_sentence = '*****Scan with F-Secure has been stopped*****\n'
    writelog(log_file, ending_sentence, 'utf-8')

    if status_code == 3:
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
            if 'Infected:' in line:
                virus_name = re.findall('(.*): Infected', str(line))
                virus_type = re.findall('Infected: (.*)', str(line))
                virus_temp_dict[virus_name[0]] = virus_type[0]
            if '[deleted]' in line:
                # print('rm : ', line)
                # removed_virus = re.findall('file (.*)', str(line))
                # print(removed_virus)
                removed_list.append(virus_name[0])

    # Compare removed_list with virus_temp_dict:
    virus_dict = compare_virus(removed_list, virus_temp_dict)
    return virus_dict

def scan(mount_pts, read_only, log_file):
    '''
    Scan the mounting point in parameters.
    Return a code
        0 : No virus
        3 : Virus found
        143 : Scan stopped by user
    '''
    cmdline = ['/usr/bin/fsav', '--virus-action1=report', '--allfiles', '--archive', '--maxnested=15', '--scantimeout=180', mount_pts]
    if not read_only:
        #Ask user if he wants av to autoclean the device
        rep = prompter('Do you want to automaticly clean the device ? (y/n)')
        if 'y' in str(rep):
            cmdline = ['/usr/bin/fsav', '--virus-action1=clean', '--virus-action2=remove', '--auto', '--allfiles', '--archive', '--maxnested=15', '--scantimeout=180', mount_pts]
    print('Scan begin')
    print("Press 's' to stop the scan")
    proc_status = '?'
    with open(log_file, mode='w', encoding='utf-8') as flog:
        # subprocess.call(cmdline, stdout=flog)
        proc_id = start_proc(cmdline, 2, flog)
        proc_status = status_proc(proc_id)
        # print('status', proc_status)
        wait_and_check(proc_status, proc_id)
        proc_status = status_proc(proc_id)
        # print('status', proc_status)
    return proc_status

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
