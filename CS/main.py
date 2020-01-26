#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - main.py
#@Alexandre Buissé - 2018/2020

#Standard imports
from datetime import datetime
import time
import os
import subprocess
from sys import exit

#Third party imports
import getch
from termcolor import colored
from tabulate import tabulate

#Project modules imports
import stats
import config
import testpreanalyse
import analyze
import commontools
import logmanagement

LOG_DIRECTORY = '/home/decontamine/'

def dismount(mount_pts):
    '''
    Prompt the user to dismount and take back his device
    '''
    rep = commontools.prompter('Do you want to eject and get back your device ? (y/n)', ['y', 'Y', 'n', 'N'])
    if rep in ['y', 'Y']:
        if subprocess.call(['/bin/umount', str(mount_pts)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            print('Success to umount your device !')
        else:
            print('Cannot umount your device !')
        print('Press any key to exit.')
        if getch.getch():
            pass
    elif rep in ['n', 'N']:
        pass

def create_table(tools_dict):
    '''
    Create a table
    '''
    table = []
    for name, value in tools_dict.items():
        version = value['version']
        table.append([colored(name, 'green'), colored(version, 'magenta')])
    print(tabulate(table, headers=[colored('Name', attrs=['bold']), colored('Version', attrs=['bold'])]))

def init():
    '''
    Initialization of the cleaning station
    It's the main function
    '''
    # Verify if LOG_DIRECTORY exists
    if os.path.exists(LOG_DIRECTORY):
        # Clean log directory
        stats.cleanlog(LOG_DIRECTORY)
    else:
        print('ERROR !')
        print('You should create "/home/decontamine" directory to store the logs and the conf file !')
        exit(1)

    print("\x1b[2J\x1b[H", end="") # clear
    # colored('install', 'red', attrs=['bold', 'reverse'])
    project_name = 'Decontamine Linux'
    project_description = 'Analyzing and cleaning station:'
    compatibility = '   for optical drives, USB drives, etc.\n'
    config_print = 'Type "' + colored('C', 'red') + '" to enter the configurator'
    exit_print = 'Type "' + colored('E', 'red') + '" to exit program'
    print('*'*len(project_name) + 20*('*'))
    print('*'*10 + colored(project_name, attrs=['bold']) + 10*'*')
    print('*'*len(project_name) + 20*('*'))
    print(project_description)
    print(compatibility)
    print(config_print)
    print(exit_print)
    now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    print("\nBegin: {d}".format(d=now) + '\n')

    # Test if av or scan modules are present on the system and activated
    tools_dict = config.init() # Will exit program if no tools find
    while tools_dict in (-1, False):
        init()
    print(colored('Scanning tools activated : ', attrs=['underline']))
    # Get a clean table of scanners activated
    create_table(tools_dict)

    # Print stats
    nb_scan, virus_detected, virus_removed = stats.stat(LOG_DIRECTORY)
    if nb_scan > 1:
        print("\n" + colored(str(nb_scan), 'yellow') + " devices have been scanned with success.")
    if (nb_scan > 1) and (virus_detected > 1):
        phrase = "And " + colored(str(virus_detected), 'yellow') + " viruses have been detected !"
        if virus_removed > 1:
            phrase = phrase + " ( " + colored(str(virus_removed), 'yellow') + " removed !)\n"
        print(phrase)

    while True:
        # Test if drives to analyze
        chosen = 0
        print('\nPlease insert a drive to analyze')
        while chosen == 0:
            rep = commontools.mykbhit()
            if rep in ['c', 'C']:   # Enter config mode
                print("\x1b[2J\x1b[H", end="") # clear
                rep = config.configurator()
                init()
            if rep in ['e', 'E']:   # Exit
                exit(1)

            chosen, device_dict = testpreanalyse.init() # Will not take any user input during the test
        # print(chosen, device_dict)

        # Get device attributs
        label, mount_pts, read_only = testpreanalyse.depack_device(device_dict)

        if mount_pts != '':
            log_file_path = LOG_DIRECTORY + 'LOGS/{}'.format(datetime.now().strftime('%Y/%m/%d'))
            log_file_path += '/' + datetime.now().strftime("%d%m%y%H%M%S")
            log_file = log_file_path + "Log.txt"

            print('\n' + '_'*30 + '\n')
            print('Device {} detected'.format(label))
            if read_only == 1:
                print('\n {} is read-only, '.format(label) + colored('it will be impossible to remove viruses !', attrs=['bold']))

            element1 = "-------------------------Device scanned : ''"+str(label) + "'' --------------\n"
            element1b = "-------------------------Read-only : " + str(read_only) + " --------------\n"
            element1c = "-------------------------Station : ''" + os.uname()[1] + "'' --------------\n"
            element2 = "-------------------------" + str(datetime.now().strftime("%A %d %B %Y %H:%M:%S")) + "--------------\n"
            element = element1 + element1b + element1c + element2
            logmanagement.writelog(log_file, element, 'utf-8')#write log_file

            # Get files
            test = 1
            while test < 30:
                begin_scan = time.time()
                files_list = testpreanalyse.get_files(mount_pts, [])
                if len(files_list) > 0:
                    # print(files_list)
                    file_print = '{} files to analyze on the device "{}"'.format(len(files_list), label)
                    print(colored(str(len(files_list)), 'yellow') + ' files to analyze on the device "{}"'.format(label))
                    logmanagement.writelog(log_file, file_print + '\n', 'utf-8')
                    for files in files_list:
                        logmanagement.writelog(log_file, files + '\n', 'utf-8')
                    test = 30
                    break
                if test == 29:# No files
                    print('No files to analyze on the device "{}"'.format(label))
                time.sleep(0.5) # Let the time for the system to get the files
                test += 1
            if len(files_list) > 0:
                print('\nBeginning of the analyze, please wait !')
                # 1 - Launch scanning tools
                detection_dict, log_av_list = analyze.init(tools_dict, mount_pts, log_file_path)

                # 2 - Print scan results
                print('\n' + '_'*30 + '\n')
                print(colored('Analyze is finished !', attrs=['bold']))

                end_scan = time.time()
                total_time_scan = end_scan - begin_scan
                total_time = 'Device analyzed in {} seconds.'.format(round(total_time_scan, 5))
                print('Device analyzed in ' + colored(str(round(total_time_scan, 5)), 'yellow') + ' seconds.\n')

                code = analyze.show_result(detection_dict, tools_dict)
                log_final_temp = log_file_path + 'tempRes'
                logmanagement.writelog(log_final_temp, '\n' + total_time + '\n', 'utf-8')

                # 3 - Ask user to remove viruses
                rm_list = []
                if read_only == 0:
                    if code == 1:
                        rm_list = analyze.rm_virus(detection_dict)
                analyze.final_result(detection_dict, tools_dict, rm_list, log_final_temp)

                # 4 - concat all logs in one final log
                all_logs = []
                all_logs = logmanagement.concat(log_file, all_logs)
                all_logs = logmanagement.concat(log_av_list, all_logs)
                all_logs = logmanagement.concat(log_final_temp, all_logs)
                # print(all_logs)
                final_log = os.path.dirname(log_file) + "/" + os.uname()[1] + "_FINAL-" + os.path.basename(log_file)
                # print(final_log)
                logmanagement.write_final_log(final_log, all_logs)
                # Clean the log of not usefull informations
                logmanagement.deleter(final_log, 'Using IDE file')

                # 5 - Prompt the user to read the detail of the final result
                logmanagement.readlog(final_log)

                #6 - Prompt the user to get a copy of the final result
                if read_only == 0:
                    logmanagement.getlog(final_log, mount_pts)

                # 7 - Prompt the user to dismount and take back his device
                dismount(mount_pts)

                # 8 - Reload the process
                init()

if __name__ == '__main__':
    init()
