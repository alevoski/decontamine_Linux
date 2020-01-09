#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - analyze.py
#@Alexandre Buissé - 2018/2020

#Standard imports
from termcolor import colored

#Project modules imports
from commontools import import_from
from logmanagement import writelog

TOOL_PATH = 'tools_scripts'

def init(tools_dict, mount_pts, read_only, log_file_path):
    '''
    Take the av list and the mounting point to be scan in params,
    Init the scan
    '''
    detected = []
    rm_list = []
    log_av_list = []
    for av_name, _ in tools_dict.items():
        print('\n' + colored('Init of the scan with ' + colored(av_name, 'green'), attrs=['bold']))
        tool = av_name.lower()
        tocall = import_from(TOOL_PATH, tool)
        status_code, virus_dict, log_file = tocall.init(mount_pts, read_only, log_file_path)
        if status_code == -15:
            print(colored('Scan has been stopped !', 'red'))
        log_av_list.append(log_file)
        if isinstance(virus_dict, dict) and len(virus_dict) > 0:
            print('\n' + colored(av_name, 'green') + ' found something !')
            detected, rm_list = result(virus_dict, detected, rm_list)
        else:
            print('\nNo virus found with ' + colored(av_name, 'green'))
        print(colored('Scan finished with ' + colored(av_name, 'green'), attrs=['bold']))
    return detected, rm_list, log_av_list

def final(detected, rm_list, log_file_path):
    '''
    Print the final scan results
    '''
    # print('notRM : ' + str(len(detected)) + str(detected))
    # print('RM : ' + str(len(rm_list)) + str(rm_list))
    log_file = log_file_path + 'tempRes'
    final_summary = '\n' + '-' * 5 + ' *****FINAL RESULT***** ' + 5 * '-' + '\n'
    writelog(log_file, final_summary, 'utf-8')

    all_virus = len(detected)

    if all_virus > 0:
        if len(rm_list) == len(detected):
            res2show = 'The {} found virus(es) was/were removed.'.format(all_virus)
            for elem in rm_list:
                writelog(log_file, elem + '\n', 'utf-8')
        else:
            res2show = '\n {} virus(es) detected, {} removed.'.format(all_virus, len(rm_list))
            for elem in detected:
                writelog(log_file, elem + '\n', 'utf-8')
            writelog(log_file, '---REMOVED---\n', 'utf-8')
            for elem in rm_list:
                writelog(log_file, elem + '\n', 'utf-8')
    else:
        res2show = 'No virus found on your device.'

    all_virus_write = 'Nb virus found : {}'.format(all_virus)
    rm_virus_write = 'Nb virus removed : {}'.format(len(rm_list))
    not_remove = len(detected) - len(rm_list)
    not_rm_virus_write = 'Nb virus not removed : {}'.format(not_remove)
    writelog(log_file, all_virus_write + '\n' + rm_virus_write + '\n' + not_rm_virus_write, 'utf-8')
    writelog(log_file, '\n' + res2show, 'utf-8')
    print(colored(res2show, attrs=['bold']))

    return log_file

def result(virus_dict, detected, rm_list):
    '''
    Take a virus dictionary and two lists of previously not removed virus and removed virus
    Return lists of virus detected and virus removed
    '''
    # print('virus_dict : ', str(virus_dict))
    for virus, values in virus_dict.items():
        # Patched to avoid double counts when multiple av tools scan a device
        # print(virus)
        removed = values['removed']
        if removed == 1:
            if virus not in rm_list:
                # print(virus, 'removed')
                rm_list.append(virus)
        if virus not in detected:
            # print(virus, 'detected')
            detected.append(virus)

    return detected, rm_list
