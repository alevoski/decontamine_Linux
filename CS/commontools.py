#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - commontools.py
#@Alexandre Buissé - 2018/2020

#Standard imports
import subprocess

#Third party imports
import getch

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

def prompter(question, choice_list):
    '''
    Prompt user, return the answer
    '''
    while True:
        print(question)
        rep = str(getch.getch())
        if rep in choice_list:
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
            code = -15
            break
    return code

def stop_all(proc_dict):
    '''
    Stop all processes in proc_dict
    '''
    for proc_id, _ in proc_dict.items():
        proc_status = status_proc(proc_id)
        if proc_status is None:
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
