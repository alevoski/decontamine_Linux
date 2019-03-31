#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - config.py
#@Alexandre Buissé - 2018

#Standard imports
import os
import sys
from datetime import datetime
import subprocess
import getch
from termcolor import colored

#Project modules imports
from logManagement import extractSTR
from commontools import import_from


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
        cfgFile = "/home/decontamine/decontamine.cfg"
        if os.path.isfile(cfgFile):
            scanners, disabledScanners = getConfInfos(cfgFile)
        else:
            print('Conf file will be created')
            scanners = setConfInfos(cfgFile, presentTools)
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

def confUpdate(filename):
    '''
    Determine if the conf file must be update
    '''
    lastFileUpdate = os.path.getmtime(filename)
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

def getConfInfos(cfgFile):
    '''
    Get av and scanning modules activated and return them
    '''
    # @Alex : f.close() cant be forgotten (https://docs.python.org/3/tutorial/errors.html - 8.7)
    #tempFile = []
    with open(cfgFile, 'r') as f:
        tempFile = f.readlines()

    toolsDict = {}
    toolLSTDisabled = []
    toupdate = confUpdate(cfgFile)

    for i, line in enumerate(tempFile):
        # print(line)
        if 'active = 1' in line:
            tool = extractSTR(tempFile[i-1], 'name = ')
            if toupdate == 1:#get tool version and update file
                version = str(getVersion(tool))
                #update version
                # sed -i '/ClamAV/{n;n;s/.*/version = 0.8/}' /home/decontamine/decontamine.cfg
                os.system("sed -i '/" + tool + "/{n;n;s/.*/version = " + str(version).replace('/', '\/') + "/}' " + cfgFile)
            else:
                version = extractSTR(tempFile[i+1], 'version = ')
            toolsDict[tool] = str(version)
        if 'active = 0' in line:
            tool = extractSTR(tempFile[i-1], 'name = ')
            tool.replace('\n', '')
            toolLSTDisabled.append(tool.replace('\n', ''))

    return toolsDict, toolLSTDisabled

def setConfInfos(cfgFile, presentTools):
    '''
    Create the conf file and activated all av and scanning modules present on the system
    Return all of them
    '''
    toolsDict = {}

    # @Alex : f.close() cant be forgotten (https://docs.python.org/3/tutorial/errors.html - 8.7)
    with open(cfgFile, "w", encoding="utf-8", errors='ignore') as f:
        for tool in presentTools:
            name = 'name = {}'.format(tool)
            actif = 'active = 1'
            versionTemp = getVersion(tool)
            version = 'version = {}'.format(versionTemp)
            f.write("##\n" + name + "\n" + actif + "\n" + version + "\n")
            toolsDict[tool] = str(versionTemp)

    return toolsDict

def configurator(avcompatibleDict):
    '''
    Configure the cleaning station
    '''
    folder = "/home/decontamine/"
    filepath = folder+"decontamine.cfg"
    # filepath2 = folder+"lstMODdecontamine.cfg"
    # print("\x1b[2J\x1b[H",end="") # clear
    limit = '_'*35
    # screen = terminal.get_terminal(conEmu=False)

    if os.path.isfile(filepath):

        # f = open(filepath,'w')
        # f.close()
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
            activeTools, disabledTools = getConfInfos(filepath)
            rep = str(getch.getch())
            if rep == '1':
                #Compatible AV
                print(colored('\nCompatible antivirus \n', 'blue', 'on_white'))
                for key, av in avcompatibleDict.items():
                    print(key)
            elif rep == '2':
                activationQuestion(disabledTools, 'activated', 'activate', '\nActivate antivirus \n', 'antivirus', filepath)
            elif rep == '3':
                activationQuestion(activeTools, 'disabled', 'disable', '\nDisable antivirus \n', 'antivirus', filepath)
            elif rep == '4':
                os.remove(filepath)
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

def activationQuestion(disabledToolsLST, etat, actif, affichage, elem, filepath):
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
                        os.system("sed -i '/" + tool + "/{n;n;s/.*/version = " + str(version).replace('/', '\/') + "/}' " + filepath)
                        toMod = 1
                    # sed -i '/ClamAV/{n;s/.*/active = 0/}' /home/decontamine/decontamine.cfg
                    os.system("sed -i '/" + tool + "/{n;s/.*/active = " + str(toMod) + "/}' " + filepath)
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
    # print(confUpdate("/home/decontamine/decontamine.cfg"))
