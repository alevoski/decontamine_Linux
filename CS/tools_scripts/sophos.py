#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - sophos.py
#@Alexandre Buissé - 2018/2020

#Standard imports
import subprocess
import re

#Project modules imports
from commontools import start_proc, status_proc, wait_and_check, compare_virus
from logmanagement import writelog, deleter, write_first_line

def init(mount_pts, read_only, log_file_path):
    '''
    Init scan with Sophos
    '''
    log_file = log_file_path + 'tempSophosAV'
    status_code = scan(mount_pts, read_only, log_file)
    write_first_line(log_file, '\n*****Scan with Sophos - begin*****\n')
    ending_sentence = '*****Scan with Sophos - finish*****\n'

    # Clean the log of not usefull informations
    deleter(log_file, 'Using IDE file')

    if status_code == 1:
        status_code = -15 # Change with a commonly shared status code
        ending_sentence = '*****Scan with Sophos has been stopped*****\n'
    writelog(log_file, ending_sentence, 'utf-8')

    if status_code in (3, -15):
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
            if '>>> Virus' in line:
                virus_name = re.findall('file (.*)', str(line))
                virus_type = re.findall("'(.*)'", str(line))
                virus_temp_dict[virus_name[0]] = virus_type[0]
            if 'Removal successful' in line:
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
    Return
        a code
            0 : No virus and no errors
            1 : Scan interruption
            2 : Errors encounter
            3 : Virus found
    '''
    cmdline = ['/usr/local/bin/savscan', '-f', '-all', '-rec', '-sc', '--stay-on-filesystem', '--stay-on-machine', '--backtrack-protection', '--preserve-backtrack', '--no-reset-atime', '--no-reset-atime', mount_pts, '-p='+ log_file]
    if not read_only:
        cmdline = ['/usr/local/bin/savscan', '-remove', '-f', '-all', '-rec', '-sc', '--stay-on-filesystem', '--stay-on-machine', '--backtrack-protection', '--preserve-backtrack', '--no-reset-atime', '--no-reset-atime', mount_pts, '-p=' + log_file]
    print('Scan begin')
    try:
        # res = str(subprocess.check_output(cmdline), 'utf-8')
        # print(res)
        # p = re.findall('Infected files:*?(\d+)', str(res))
        # return 0
        print("Press 's' to stop the scan")
        proc_id = start_proc(cmdline, 1)
        proc_status = status_proc(proc_id)
        # print('status', proc_status)
        wait_and_check(proc_status, proc_id)
        proc_status = status_proc(proc_id)
        # print('status sophos', proc_status)
        return proc_status
    except subprocess.CalledProcessError as exception:#Error
        proc_status = re.findall(r'exit status.*?(\d+)', str(exception))
    return int(proc_status[0])

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
