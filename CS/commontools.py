#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - commontools.py
#@Alexandre Buissé - 2018/2020

#Standard imports
import re
import subprocess
import getch
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
    kbinput = kbhitClass.KBHit()

    # print('Hit any key, or ESC to exit')

    test = 1
    while test < 15000:
        # print(test)
        if kbinput.kbhit():
            char = kbinput.getch()
            # print(char)
            return char
        test += 1

def create_table(the_dict, column1, column2):
    '''
    Create a table
    '''
    max1 = 0
    max2 = 0

    for item, value in the_dict.items():
        # max len()
        if len(item) > max1:
            max1 = len(item)
        if len(value) > max2:
            max2 = len(value)

    # Table headers
    diff_max1 = max1-len(column1)
    max1_header = column1 + " " * diff_max1 + "| "

    diff_max2 = max2-len(column2)
    max2_header = column2 + " " * diff_max2 + "|"

    header = max1_header + max2_header
    lim_header = "-" * max1 + "-" * max2
    print(colored(header, attrs=['bold']))
    print(lim_header)

    # Table values
    for item, value in the_dict.items():
        # print(item)
        diff_max1 = max1-len(item)
        the_item = item +" "*diff_max1

        diff_max2 = max2-len(value)
        the_value = value +" "*diff_max2

        print(colored(the_item, 'green') + "|" + colored(the_value, 'magenta'))

def extract_number(line):
    '''
    Extract number in string
    '''
    try:
        num = re.search('[0-9]+', line)
        # print(repr(line), repr(num.group(0)))
        return int(num.group(0))
    except Exception:
        return 0

def prompter(question):
    '''
    Prompt user, return the answer
    '''
    while True:
        print(question)
        rep = str(getch.getch())
        if rep in ['y', 'n']:
            break
    return rep

def start_proc(procname, mode, fwrite=subprocess.DEVNULL):
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

def status_proc(proc):
    '''
    Return process status code
    '''
    return proc.poll()

def stop_proc(proc):
    '''
    Kill a process and wait until it terminate
    '''
    # proc.kill()
    proc.terminate()
    proc.wait()

def wait_and_checkOLD(proc_status, proc_id):
    '''
    Wait for process to terminate itself
    Meanwhile, check if user wants to stop process
    '''
    while proc_status is None:
        proc_status = status_proc(proc_id)
        if proc_status is not None:
            break
        if mykbhit() in ['s', 'S']:
            stop_proc(proc_id)
            
            
def wait_and_check(proc_status, proc_id):
    '''
    Wait for process to terminate itself
    Meanwhile, check if user wants to stop process
    '''
    code = 0
    while proc_status is None:
        proc_status = status_proc(proc_id)
        if proc_status is not None:
            break
        if mykbhit() in ['s', 'S']:
            print('Stop requested')
            # stop_proc(proc_id)
            code = -15
            break
    return code
    
def stop_all(proc_dict):
    # import psutil
    for proc_id, _ in proc_dict.items():
        # process = psutil.Process(proc_id.pid)
        proc_status = status_proc(proc_id)
        # print(process.name, proc_status)
        if proc_status is None:
            # print(str(process.name) + ' will be terminated')
            stop_proc(proc_id)
    
def compare_virus(removed_list, virus_temp_dict):
    '''
    Compare removed_list with virus_temp_dict
    '''
    virus_dict = {}
    for virus_name, virus_type in virus_temp_dict.items():
        # print(virus_name)
        removed = 0
        if virus_name in removed_list:
            removed = 1
            # print('rm ok')
        virus_dict[virus_name] = {'type':str(virus_type), 'removed':removed}
    return virus_dict

#https://repolinux.wordpress.com/2012/10/09/non-blocking-read-from-stdin-in-python/
