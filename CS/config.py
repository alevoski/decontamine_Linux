#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - config.py
#@Alexandre Buissé - 2018/2020

#Standard imports
import os
import sys
from configparser import ConfigParser
from datetime import datetime
import subprocess
import getch
from termcolor import colored

#Project modules imports
from commontools import import_from

CFG_FILE = "/home/decontamine/decontamine.cfg"

AV_COMPATIBLE_DICT = {'ClamAV':'clamdscan',
                      'Sophos':'savscan',
                      'F-Secure':'fsav'}

TOOL_PATH = 'tools_scripts'
# modulescompatibleDict = {}

def init():
    '''
    Verify
        if av or scanning modules are present on the system
            if the conf file exist (decontamine.cfg) it return the dict of av and modules activated,
            else it creates it with all activated by default
        else exit the program
    '''
    present_av = finder(AV_COMPATIBLE_DICT, 1)
    # presentModules = finder(modulescompatibleDict, 2)
    present_tools = present_av
    # print(present_tools)
    # sys.exit()
    if present_tools != []:
        if os.path.isfile(CFG_FILE):
            active_tools, _ = get_conf_infos()
        else:
            print('Conf file will be created')
            active_tools = set_conf_infos(present_tools)
        if active_tools != {}:
            return active_tools
        else:
            # No scanning tools activated on the system
            print("\x1b[2J\x1b[H",end="") # clear
            line1 = colored('No antivirus or scanning modules activated on the system, please ', 'red', attrs=['bold'])
            line2 = colored('activate', 'red', attrs=['bold', 'reverse'])
            line3 = colored(' one !', 'red', attrs=['bold'])
            print(line1 + line2 + line3)
            rep = configurator()
            return rep
    else:
        # No scanning tools present on the system
        line1 = colored('No antivirus or scanning modules installed on the system, please ', 'red', attrs=['bold'])
        line2 = colored('install', 'red', attrs=['bold', 'reverse'])
        line3 = colored(' one !', 'red', attrs=['bold'])
        print(line1 + line2 + line3)
        sys.exit(-1)

def finder(elem_dict, option):
    '''
    Search antivirus and scanning modules on the system and return the find one
    '''
    elem_find_list = []
    if option == 1:
        for key, value in elem_dict.items():
            if subprocess.call(['/bin/which', value], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                elem_find_list.append(key)
    return elem_find_list

def get_version(elem):
    '''
    Return cleaning tool version passed in parameter
    '''
    tool = elem.lower()
    tocall = import_from(TOOL_PATH, tool)
    item_version = tocall.version()
    return item_version

def conf_update():
    '''
    Determine if the conf file must be update
    '''
    last_file_update = os.path.getmtime(CFG_FILE)
    file_time = datetime.fromtimestamp(last_file_update)
    time_now = datetime.now()
    diff = time_now - file_time
    diff_hours = diff.total_seconds()/3600
    # print(diff)
    # print(diff.total_seconds())
    # print(diff_hours)
    if diff_hours > 5:# Update version information each 5 hours
        return 1
    return 0

def update_confile(tool, param, newvalue):
    '''
    Update value in a conf file
    '''
    # Read file
    config = ConfigParser()
    config.read(CFG_FILE)

    # Set the new value in line
    config.set(tool, param, newvalue)

    # Write to file
    with open(CFG_FILE, 'w') as configfile:
        config.write(configfile)

def get_conf_infos():
    '''
    Get activated tools and return them
    Return also the disabled tools
    '''
    tools_dict = {}
    disabled_tools = []
    toupdate = conf_update()

    config = ConfigParser()
    config.read(CFG_FILE)

    for section in config.sections():
        name = config.get(section, 'name')
        actif = config.get(section, 'active')
        version = config.get(section, 'version')

        if int(actif[-1:]) == 1:
            if toupdate == 1: # Get tool version and update file
                version = str(get_version(name))
                update_confile(name, 'version', version)
            tools_dict[name] = str(version)

        if int(actif[-1:]) == 0:
            disabled_tools.append(name)

    return tools_dict, disabled_tools

def set_conf_infos(present_tools):
    '''
    Create the conf file and activated all av and scanning modules present on the system
    Return all of them
    '''
    config = ConfigParser()
    tools_dict = {}

    for tool in present_tools:
        version = get_version(tool)
        config.add_section(tool)
        config.set(tool, 'name', tool)
        config.set(tool, 'active', '1')
        config.set(tool, 'version', version)
        tools_dict[tool] = str(version)

    with open(CFG_FILE, mode='w') as settings:
        config.write(settings)

    return tools_dict

def configurator():
    '''
    Configure the cleaning station
    '''
    # filepath2 = folder+"lstMODdecontamine.cfg"
    # print("\x1b[2J\x1b[H",end="") # clear
    limit = '_'*35
    # screen = terminal.get_terminal(conEmu=False)

    if os.path.isfile(CFG_FILE):
        # print(lstAvTrouve)
        # print(avCompatible)
        print(colored("Station configuration\n", attrs=['bold']))
        print(colored("Chose an option", 'white', attrs=['bold', 'underline']))
        print(colored("\n1 - Compatible antivirus", 'blue', 'on_white'))
        print(colored("\n2 - Activate antivirus", 'blue', 'on_white'))
        print(colored("\n3 - Disable antivirus", 'blue', 'on_white'))
        print(colored("\n4 - Reset antivirus configuration", 'red', 'on_white'))
        # if os.path.isfile(filepath2):
            # screen.cprint(8, 0, "\n************Modules************")
            # screen.cprint(8, 0, "\n5 - Liste des modules développés")
            # screen.cprint(8, 0, "\n6 - Activer des modules")
            # screen.cprint(8, 0, "\n7 - Désactiver des modules")
            # screen.cprint(8, 0, "\n8 - Reset de la configuration des modules")
        print(colored("\n\ne - Exit\n", 'yellow', 'on_white'))

        while True:
            active_tools, disabled_tools = get_conf_infos()
            rep = str(getch.getch())
            if rep == '1':
                # Compatible AV
                print(colored('\nCompatible antivirus \n', 'blue', 'on_white'))
                for av_name, _ in AV_COMPATIBLE_DICT.items():
                    print(av_name)
            elif rep == '2':
                activation_question(disabled_tools, 'activated', 'activate', '\nActivate antivirus \n', 'antivirus')
            elif rep == '3':
                activation_question(active_tools, 'disabled', 'disable', '\nDisable antivirus \n', 'antivirus')
            elif rep == '4':
                os.remove(CFG_FILE)
                return -1
            # if os.path.isfile(filepath2):
                # activeToolsMod, disabledToolsMod = configReader(filepath2, 'module_name = ', 3)
                # if '5' in str(rep):
                    #Liste des modules développés
                    # screen.cprint(7, 0, '\nModules développés \n')
                    # for key, mod in dictMOD.items():
                        # screen.cprint(8, 0, key+'\n')
                # elif '6' in str(rep):
                    # desactiverMod = activation_question(disabledToolsMod, 'activés', 'activer', '\nActiver des modules \n', 'modules')
                    # res = activationExec(desactiverMod, 1, 'activé', filepath2, 'module_name = ')
                # elif '7' in str(rep):
                    # activerMod = activation_question(activeToolsMod, 'désactivés', 'désactiver', '\nDésactiver des modules \n', 'modules')
                    # res = activationExec(activerMod, 0, 'désactivé', filepath2, 'module_name = ')
                # elif '8' in str(rep):
                    # os.remove(filepath2)
                    # return False
            if rep in ["e", "E"]:
                return False
            print(limit)
    else:
        return False

def activation_question(tools_list, etat, actif, affichage, elem):
    '''
    Configuration mode - enable/disable av and modules
    Take av and modules list and things to be printed.
    Ask question for each tools in the list.
    Sed the file to mod tool state if user wants to.
    '''
    if len(tools_list) > 0:
        print(colored(affichage, 'blue', 'on_white'))
        for tool in tools_list:
            print(actif)
            print("Do you want to {} ".format(actif) + colored(str(tool), 'grey', 'on_yellow') + " ? (y = yes, n = no)")
            while True:
                rep3 = str(getch.getch())
                if rep3 in ['y', 'Y']:
                    to_mod = 0 # Disable
                    if actif == 'activate':
                        # Get tool version
                        print('Getting {} version information'.format(tool))
                        version = str(get_version(tool))
                        # Update version
                        # sed -i '/ClamAV/{n;n;s/.*/version = 0.8/}' /home/decontamine/decontamine.cfg
                        update_confile(tool, 'version', version)
                        to_mod = 1
                    # sed -i '/ClamAV/{n;s/.*/active = 0/}' /home/decontamine/decontamine.cfg
                    update_confile(tool, 'active', str(to_mod))
                    print(tool + ' is now ' + actif)
                    break
                if rep3 in ['n', 'N']:
                    # print(" unsave")
                    break
    else:
        print("All the " + elem + " are " + etat)

if __name__ == '__main__':
    init()
