#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - config.py
#@Alexandre Buissé - 2018

#Standard imports
import os
import sys
import configparser
from datetime import datetime
import subprocess
import getch
from termcolor import colored

#Project modules imports
from commontools import import_from

cfgFile = "/home/decontamine/decontamine.cfg"

avcompatibleDict = {'ClamAV':'clamdscan',
                    'Sophos':'savscan',
                    'F-Secure':'fsav'}
# modulescompatibleDict = {}

def init():
    '''
    Verify
        if av or scanning modules are present on the system
            if the conf file exist (decontamine.cfg) it return the dict of av and modules activated,
            else it creates it with all activated by default
        else exit the program
    '''
    presentAv = finder(avcompatibleDict, 1)
    # presentModules = finder(modulescompatibleDict, 2)
    presentTools = presentAv
    # print(presentTools)
    # sys.exit()
    if presentTools != []:
        if os.path.isfile(cfgFile):
            scanners, disabledScanners = getConfInfos()
        else:
            print('Conf file will be created')
            scanners = setConfInfos(presentTools)
        if scanners != {}:
            return scanners
        else:
            #no av or scanning modules activated on the system
            print("\x1b[2J\x1b[H",end="") # clear
            line1 = colored('No antivirus or scanning modules activated on the system, please ', 'red', attrs=['bold'])
            line2 = colored('activate', 'red', attrs=['bold', 'reverse'])
            line3 = colored(' one !', 'red', attrs=['bold'])
            print(line1 + line2 + line3)
            rep = configurator(avcompatibleDict)
            return rep
    else:
        #no av or scanning modules present on the system
        line1 = colored('No antivirus or scanning modules installed on the system, please ', 'red', attrs=['bold'])
        line2 = colored('install', 'red', attrs=['bold', 'reverse'])
        line3 = colored(' one !', 'red', attrs=['bold'])
        print(line1 + line2 + line3)
        sys.exit(-1)

def finder(dictElem, option):
    '''
    Search antivirus and scanning modules on the system and return the find one
    '''
    elemFind = []
    if option == 1:
        for k, v in dictElem.items():
            if subprocess.call(['/bin/which', v], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                elemFind.append(k)
    return elemFind

def getVersion(elem):
    '''
    Return cleaning tool version passed in parameter
    '''
    tool = elem.lower()
    toolPath = 'tools_scripts'
    tocall = import_from(toolPath, tool)
    itemVersion = tocall.version()
    return itemVersion

def confUpdate():
    '''
    Determine if the conf file must be update
    '''
    lastFileUpdate = os.path.getmtime(cfgFile)
    fileTime = datetime.fromtimestamp(lastFileUpdate)
    timeNow = datetime.now()
    diff = timeNow - fileTime
    diffHours = diff.total_seconds()/3600
    # print(diff)
    # print(diff.total_seconds())
    # print(diffHours)
    if diffHours > 5:#update version information each 5 hours
        return 1
    else:
        return 0

def updateConfFile(tool, param, newvalue):
    '''
    Update value in a conf file
    '''
    # Read file
    config = configparser.ConfigParser()
    config.read(cfgFile)

    # Set the new value in line
    config.set(tool, param, newvalue)
    
    # Write to file
    with open(cfgFile, 'w') as configfile:
        config.write(configfile)

def getConfInfos():
    '''
    Get activated tools and return them
    Return also the disabled tools
    '''
    toolsDict = {}
    toolLSTDisabled = []
    toupdate = confUpdate()

    config = configparser.ConfigParser()
    config.read(cfgFile)

    for section in config.sections():
        name = config.get(section, 'name')
        actif = config.get(section, 'active')
        version = config.get(section, 'version')

        if int(actif[-1:]) == 1:
            if toupdate == 1: # Get tool version and update file
                version = str(getVersion(name))
                updateConfFile(name, 'version', version)
            toolsDict[name] = str(version)
        
        if int(actif[-1:]) == 0:
            toolLSTDisabled.append(name)

    return toolsDict, toolLSTDisabled

def setConfInfos(presentTools):
    '''
    Create the conf file and activated all av and scanning modules present on the system
    Return all of them
    '''
    config = configparser.ConfigParser()
    toolsDict = {}
    
    for tool in presentTools:
        version = getVersion(tool)
        config.add_section(tool)
        config.set(tool, 'name', tool)
        config.set(tool, 'active', '1')
        config.set(tool, 'version', version)
        toolsDict[tool] = str(version)
    
    with open(cfgFile, mode='w') as settings:
        config.write(settings)
    
    return toolsDict

def configurator(avcompatibleDict):
    '''
    Configure the cleaning station
    '''
    # filepath2 = folder+"lstMODdecontamine.cfg"
    # print("\x1b[2J\x1b[H",end="") # clear
    limit = '_'*35
    # screen = terminal.get_terminal(conEmu=False)

    if os.path.isfile(cfgFile):
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
            activeTools, disabledTools = getConfInfos()
            rep = str(getch.getch())
            if rep == '1':
                #Compatible AV
                print(colored('\nCompatible antivirus \n', 'blue', 'on_white'))
                for key, av in avcompatibleDict.items():
                    print(key)
            elif rep == '2':
                activationQuestion(disabledTools, 'activated', 'activate', '\nActivate antivirus \n', 'antivirus')
            elif rep == '3':
                activationQuestion(activeTools, 'disabled', 'disable', '\nDisable antivirus \n', 'antivirus')
            elif rep == '4':
                os.remove(cfgFile)
                return -1
            # if os.path.isfile(filepath2):
                # activeToolsMod, disabledToolsMod = configReader(filepath2, 'module_name = ', 3)
                # if '5' in str(rep):
                    #Liste des modules développés
                    # screen.cprint(7, 0, '\nModules développés \n')
                    # for key, mod in dictMOD.items():
                        # screen.cprint(8, 0, key+'\n')
                # elif '6' in str(rep):
                    # desactiverMod = activationQuestion(disabledToolsMod, 'activés', 'activer', '\nActiver des modules \n', 'modules')
                    # res = activationExec(desactiverMod, 1, 'activé', filepath2, 'module_name = ')
                # elif '7' in str(rep):
                    # activerMod = activationQuestion(activeToolsMod, 'désactivés', 'désactiver', '\nDésactiver des modules \n', 'modules')
                    # res = activationExec(activerMod, 0, 'désactivé', filepath2, 'module_name = ')
                # elif '8' in str(rep):
                    # os.remove(filepath2)
                    # return False
            if rep in ["e", "E"]:
                return False
            print(limit)
    else:
        return False

def activationQuestion(disabledToolsLST, etat, actif, affichage, elem):
    '''
    Configuration mode - enable/disable av and modules
    Take av and modules list and things to be printed.
    Ask question for each tools in the list.
    Sed the file to mod tool state if user wants to.
    '''
    if len(disabledToolsLST) > 0:
        print(colored(affichage, 'blue', 'on_white'))
        for tool in disabledToolsLST:
            print(actif)
            print("Do you want to {} ".format(actif) + colored(str(tool), 'grey', 'on_yellow') + " ? (y = yes, n = no)")
            while True:
                rep3 = str(getch.getch())
                if rep3 in ['y', 'Y']:
                    toMod = 0 #disable
                    if actif == 'activate':
                        #Get tool version
                        print('Getting {} version information'.format(tool))
                        version = str(getVersion(tool))
                        #update version
                        # sed -i '/ClamAV/{n;n;s/.*/version = 0.8/}' /home/decontamine/decontamine.cfg
                        updateConfFile(tool, 'version', version)
                        toMod = 1
                    # sed -i '/ClamAV/{n;s/.*/active = 0/}' /home/decontamine/decontamine.cfg
                    updateConfFile(tool, 'active', str(toMod))
                    print(tool + ' is now ' + actif)
                    break
                elif rep3 in ['n', 'N']:
                    # print(" unsave")
                    break
    else:
        print("All the " + elem + " are " + etat)

if __name__ == '__main__':
    res = init()
    print('scanners :', res)
    # rep = configurator(avcompatibleDict)
    # if rep == -1:
        # res = init()
        # print(res)
    # print(confUpdate())
