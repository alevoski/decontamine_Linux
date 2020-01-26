#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - stats.py
#@Alexandre Buissé - 2018/2020

#Standard imports
import os
import re

def stat(log_dir):
    '''
    Count and return the number of files and the number of virus in the directory passed in parameter with global_stat()
    '''
    nb_scan = []
    virus_detected = 0
    virus_removed = 0
    nb_virus_detect = 0
    nb_virus_del = 0
    for root, dirnames, filenames in os.walk(log_dir + 'LOGS/'):
        for files in filenames:
            # print(files)
            the_dir = str(dirnames).replace("[]", "/")
            file_path = os.path.abspath(str(root) + str(the_dir) + str(files))
            if "FINAL" in files:
                nb_scan.append(files)
            # print(nb_scan)
            # print(file_path)
            # Get detected viruses and removed viruses
            try:
                nb_virus_detect, nb_virus_del = global_stat(file_path)
            except UnicodeDecodeError:
                continue
            # print("virus per files  : ", nb_virus_del, file_path)
            virus_detected = virus_detected + nb_virus_detect
            virus_removed = virus_removed + nb_virus_del
    return len(nb_scan), virus_detected, virus_removed

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

def global_stat(files):
    '''
    Get and return the number of virus detected and the number of virus removed with the log file passed in parameter
    '''
    nb_virus_detect = 0
    nb_virus_del = 0

    with open(files, mode='r', encoding='utf-8') as logfile:
        for line in logfile:
            # print(line)
            if "Nb virus found" in line:
                nb_virus_detect = extract_number(line)
                # print(str(files)+' nb_virus_detect:'+str(nb_virus_detect))
            if "Nb virus removed" in line:
                nb_virus_del = extract_number(line)
                # print(str(files)+' nb_virus_del:'+str(nb_virus_del))
    return nb_virus_detect, nb_virus_del

def cleanlog(log_dir):
    '''
    Clean the log directory
    '''
    for root, dirnames, filenames in os.walk(log_dir + 'LOGS/'):
        # print ("files :"+str(filenames))
        #Deleted not finalized logs or empty logs
        for files in filenames:
            the_dir = str(dirnames).replace("[]", "/")
            file_path = os.path.abspath(str(root) + str(the_dir) + str(files))
            # print(os.path.getsize(file_path)) #test ok
            if ("FINAL" in files or "STAT" in files) and (os.path.getsize(file_path) != 0):
                # print("ok")
                pass
            else:
                # print(files," supress")
                try:
                    os.remove(os.path.abspath(file_path))
                except Exception:
                    pass

        # Removed empty directories
        for the_dir in dirnames:
            subdirpath = os.path.abspath(str(root) + "/" + str(the_dir))
            # print(subdirpath)
            if os.listdir(subdirpath) == []:
                # print("vide",subdirpath) #ok
                try:
                    os.rmdir(subdirpath)
                except Exception:
                    pass

if __name__ == '__main__':
    print(stat('/home/decontamine/'))
