#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - logmanagement.py
#@Alexandre Buissé - 2018/2020

#Standard imports
import re
import os
import shutil
import subprocess
import fileinput

#Project modules imports
from commontools import prompter

def write_first_line(log_file, line):
    '''
    Write first line in a file
    '''
    with open(log_file, mode='r+') as file2write:
        content = file2write.read()
        file2write.seek(0, 0)
        file2write.write(line.rstrip('\r\n') + '\n' + content)

def writelog(log_file, element, codec):
    '''Write log on the station'''
    # print(repr(element))
    #Create a directory where all the logs will be stored
    dir_to_create = os.path.dirname(os.path.abspath(log_file))
    # print (dir_to_create)
    if not os.path.exists(dir_to_create):
        os.makedirs(dir_to_create)
    try:
        with open(log_file, mode='a', encoding=codec, errors='ignore') as file2write:
            # print(element)
            file2write.write(element)
    except Exception:
        print("Can't write the file {} with this element : {}".format(log_file, element))

def write_final_log(concatenate_base_files, logs):
    '''
    Concatenate log files in one final log file
    Take the path to write the final log and the list of log files
    '''
    with open(concatenate_base_files, mode='w', encoding='utf-8', errors='ignore') as final_file:
        # print ("fichier final test : "+str(concatenate_base_files)) #ok
        for i in logs:
            while os.path.isfile(i):
                # print ("testFile : "+str(i)) #ok
                with open(i, mode='r', encoding='utf-8', errors='ignore') as file2copy:
                    shutil.copyfileobj(file2copy, final_file)
                    try:
                        # i.close() #NEVER decomment : could create a very big file in an infinite loop
                        os.remove(i) #remove concatenated file
                    except Exception:#OSError:
                        continue

def concat(the_file, the_list):
    '''
    Append a file to a list
    '''
    if isinstance(the_file, list):
        for logs in the_file:
            the_list.append(logs)
    else:
        the_list.append(the_file)
    return the_list

def readlog(final_log):
    '''
    Prompt the user to read the final log
    '''
    rep = prompter('Do you want to read the detail of the scan ? (y/n)', ['y', 'Y', 'n', 'N'])
    if rep == 'y':
        subprocess.call(('xdg-open', str(final_log)))
    elif rep == 'n':
        pass

def getlog(final_log, mount_pts):
    '''
    Prompt the user to get a copy of the final log
    '''
    rep = prompter('Do you want a copy of the detail of the scan ? (y/n)', ['y', 'Y', 'n', 'N'])
    if rep == 'y':
        copied_file = mount_pts + '/' + os.path.basename(final_log)
        # print(final_log)
        shutil.copy2(final_log, copied_file)
        # print(copied_file)
        if os.path.isfile(copied_file):
            print('The result of the scan have been copied on the device ' + mount_pts)
    elif rep == 'n':
        pass

def deleter(log_file, elem):
    '''Delete line containing elem in log_file'''
    for line in fileinput.input(log_file, inplace=True):
        if not re.search(elem, line):
            print(line, end='')
