#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - analyze.py
#@Alexandre Buissé - 2018/2020

#Standard imports
import os
from termcolor import colored
from tabulate import tabulate

#Project modules imports
from commontools import import_from, status_proc, wait_and_check, stop_all, prompter
from logmanagement import writelog, write_first_line
from concurrent.futures import ThreadPoolExecutor as pooler

TOOL_PATH = 'tools_scripts'

def init(tools_dict, mount_pts, log_file_path):
    '''
    Take the av list and the mounting point to be scan in params,
    Init the scan
    '''
    tocall_dict = {}
    av_names = ''
    print('\n' + colored('Init of the scan with :', attrs=['bold']))
    for av_name, _ in tools_dict.items():
        av_names += '   - ' + av_name + '\n'
        tool = av_name.lower()
        log_file = log_file_path + 'temp' + tool
        tocall_dict[import_from(TOOL_PATH, tool)] = {'log_file':log_file, 'tool':tool}
    print(colored(av_names, 'green'))
    # Multithread tool call
    resul_list = []
    proc_dict = {}
    with pooler() as executor:
        for tocall, values in tocall_dict.items():
            log_file = values['log_file']
            resul_list.append(executor.submit(tocall.scan, mount_pts, log_file))
    for elem in resul_list:
        proc_id = elem.result()
        proc_status = status_proc(proc_id)
        proc_dict[proc_id] = proc_status

    # Waiting for processes to finish or for user input
    resul_list = []
    sentence = 'Scan finished !'
    print("Press 's' to stop the scan")
    with pooler() as executor:
        for proc_id, proc_status in proc_dict.items():
            resul_list.append(executor.submit(wait_and_check, proc_status, proc_id))
            for elem in resul_list:
                code = elem.result()
                # print(code)
            if code == -15:
                stop_all(proc_dict)
                sentence = 'Scan has been interrupted'
    print(sentence)

    # Get virus dicts, parse them from log files and return results
    detection_dict = {}
    log_av_list = []
    for tocall, values in tocall_dict.items():
        log_file = values['log_file']
        tool = values['tool']
        write_first_line(log_file, '\n*****Scan with ' + tool + ' - begin*****\n')
        writelog(log_file, '\n*****Scan with ' + tool + ' - finish*****\n', 'utf-8')
        virus_dict = tocall.get_virus(log_file)
        log_av_list.append(log_file)
        if isinstance(virus_dict, dict) and len(virus_dict) > 0:
            detection_dict = virus_found_tools(detection_dict, virus_dict, tool)

    return detection_dict, log_av_list

def show_result(detection_dict, tools_dict):
    '''
    Show result of the scan
    Return 0 : no virus found
    Return 1 : virus found
    '''
    nb_virus = len(detection_dict)
    sentence_res = str(nb_virus) + ' virus detected !'
    print(sentence_res)
    code = 0
    if nb_virus > 0:
        code = 1
        # Headers
        table = []
        virus_num = 1
        for virus_name, values in detection_dict.items():
            virus_type = values['virus_type']
            tools_list = values['tool']
            tool = []
            # tool = ''
            for thetools in list(sorted(tools_dict.keys())):
                # print(thetools)
                # for tools in tools_list:
                if thetools.lower() in tools_list:
                    tool.append('X')
                    # tool += 'X'
                else:
                    # print('no')
                    # tool += '_'
                    tool.append('_')
            table.append([virus_num, virus_name, virus_type, tool])
            virus_num += 1
        print(tabulate(table, headers=['virus_num', 'virus_name', 'virus_type', list(sorted(tools_dict.keys()))]))
    return code

def final_result(detection_dict, tools_dict, rm_list, log_final_temp):
    '''
    Write final result
    '''
    final_summary = '\n' + '-' * 5 + ' *****FINAL RESULT***** ' + 5 * '-' + '\n'
    writelog(log_final_temp, final_summary, 'utf-8')
    nb_virus = len(detection_dict)
    
    all_virus = len(detection_dict)

    if all_virus > 0:
        if len(rm_list) == all_virus:
            res2show = 'The {} found virus(es) was/were removed.'.format(all_virus)
        else:
            res2show = '\n {} virus(es) detected, {} removed.'.format(all_virus, len(rm_list))

        # Write table
        table = []
        virus_num = 1
        for virus_name, values in detection_dict.items():
            virus_type = values['virus_type']
            tools_list = values['tool']
            tool = []
            removed = ''
            if virus_name in rm_list:
                removed = 'X'
            for thetools in list(sorted(tools_dict.keys())):
                # print(thetools)
                # for tools in tools_list:
                if thetools.lower() in tools_list:
                    tool.append('X')
                    # tool += 'X'
                else:
                    # print('no')
                    # tool += '_'
                    tool.append('_')
            table.append([virus_num, virus_name, virus_type, tool, removed])
            virus_num += 1
        # print(tabulate(table, headers=['virus_num', 'virus_name', 'virus_type', list(sorted(tools_dict.keys())), 'removed']))
        writelog(log_final_temp, '\n' +
                 tabulate(table, headers=['virus_num', 'virus_name', 'virus_type', list(sorted(tools_dict.keys())), 'removed'])
                 + '\n', 'utf-8')
    else:
        res2show = 'No virus found on your device.'
    all_virus_write = '\nNb virus found : {}'.format(all_virus)
    rm_virus_write = 'Nb virus removed : {}'.format(len(rm_list))
    not_remove = all_virus - len(rm_list)
    not_rm_virus_write = 'Nb virus not removed : {}'.format(not_remove)
    writelog(log_final_temp, all_virus_write + '\n' + rm_virus_write + '\n' + not_rm_virus_write, 'utf-8')
    writelog(log_final_temp, '\n' + res2show, 'utf-8')
    print(colored(res2show, attrs=['bold']))

def rm_virus(detection_dict):
    '''
    Prompt the user to remove viruses
    '''
    rm_list = []
    for virus_name, _ in detection_dict.items():
        rep = prompter('Do you want to remove ' + str(virus_name)+ ' ? (y/n)')
        if rep in ['y', 'Y']:
            if os.path.isfile:
                os.remove(virus_name)
                rm_list.append(virus_name)
            else:
                print('Error - file not found !')
        elif rep in ['n', 'N']:
            pass
    return rm_list

def virus_found_tools(detection_dict, virus_dict, tool):
    '''
    Take a virus dictionary and two lists of previously not removed virus and removed virus
    Return lists of virus detected and virus removed
    '''
    # print('virus_dict : ', str(virus_dict))
    tool_list = []
    for virus_name, virus_type in virus_dict.items():
        if virus_name in detection_dict:
            # virus already found, we add the tool
            for virus, values in detection_dict.items():
                if virus == virus_name:
                    tool_list = values['tool']
                    tool_list.append(tool)
                    # print(tool_list)
                    # print(type(tool_list))
                    break
        else:
            tool_list = []
            tool_list.append(tool)
        detection_dict[virus_name] = {'virus_type':virus_type,
                                      'tool':tool_list}
    # print(detection_dict)
    return detection_dict
