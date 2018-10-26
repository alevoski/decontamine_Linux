#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Decontamine Linux - config.py
#@Alexandre Buissé - 2018

import logManagement
import commontools
import os
import sys
import subprocess
from termcolor import colored
import getch

avcompatibleDict = {'ClamAV':'clamdscan',
'Sophos':'sophos'}
modulescompatibleDict = {}

def init():
    '''
    Verify 
        if av or scanning modules are present on the system
            if the conf file exist (decontamine.cfg) it return the list of av and modules activated, 
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
            scanners = setConfInfos(cfgFile, presentTools)
        if scanners != []:
            # Get av versions
            toolsDict = {}
            for elem in scanners:
                tool = elem.lower()
                # try:
                tocall = commontools.import_from(tool, 'version')
                itemVersion = tocall()
                # print(itemVersion)
                toolsDict[elem] = itemVersion
                # except Exception:
                    # pass
            return toolsDict
        else:
            #no av or scanning modules activated on the system
            os.system('clear')
            line1 = colored('No antivirus or scanning modules activated on the system, please ', 'red', attrs=['bold'])
            line2 = colored('activate', 'red', attrs=['bold', 'reverse'])
            line3 = colored(' one !', 'red', attrs=['bold'])
            print(line1 + line2 + line3)
            rep = configurator(avcompatibleDict)  
            return rep
            # init()
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
            try:
                cmdline = 'command -v ' + v
                p = subprocess.check_output(cmdline, shell = True)
                # print(p)
                # rep = 1
                elemFind.append(k)
            except Exception:
                # rep = 0
                pass
            # print(k + ' : ' + str(rep)) 
    return elemFind
        
def getConfInfos(cfgFile):
    '''
    Get av and scanning modules activated and return them
    '''
    f = open(cfgFile,'r')
    tempFile = []
    tempFile = f.readlines()
    f.close()
    toolLST = []
    toolLSTDisabled = []

    for i, line in enumerate(tempFile):
        # print(line)
        if 'active = 1' in line:
            name = tempFile[i-1]
            # print(name)
            temp = logManagement.extractSTR(tempFile[i-1], 'name = ')
            # print(temp)
            # temp = re.split('name = ', name)[-1]
            # print(temp.replace('\n',''))
            toolLST.append(temp.replace('\n',''))
        if 'active = 0' in line:
            name = tempFile[i-1]
            # temp = re.split('name = ', name)[-1]
            temp = logManagement.extractSTR(tempFile[i-1], 'name = ')
            temp.replace('\n','')
            toolLSTDisabled.append(temp.replace('\n',''))
        
    return toolLST, toolLSTDisabled
    
def setConfInfos(cfgFile, presentTools):
    '''
    Create the conf file and activated all av and scanning modules present on the system
    Return all of them
    '''
    f = open(cfgFile,'w')
    f.close()
    
    toolLST = []

    for tool in presentTools:
        name = 'name = '+str(tool)
        actif =  'active = 1'
        f = open(cfgFile, "a", encoding="utf-8", errors='ignore')
        f.write('##\n'+name+"\n"+actif+"\n")    
        f.close()
        toolLST.append(name)
        
    return toolLST
    
def configurator(avcompatibleDict):
    '''
    Configure the cleaning station
    '''
    folder = "/home/decontamine/" 
    filepath = folder+"decontamine.cfg"
    filepath2 = folder+"lstMODdecontamine.cfg"
    # os.system('clear')
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
            # screen.cprint(8,0,"\n************Modules************")
            # screen.cprint(8,0,"\n5 - Liste des modules développés")
            # screen.cprint(8,0,"\n6 - Activer des modules")
            # screen.cprint(8,0,"\n7 - Désactiver des modules")
            # screen.cprint(8,0,"\n8 - Reset de la configuration des modules")
        print(colored("\n\ne - Exit\n", 'yellow', 'on_white'))

        while True:
            activeTools, disabledTools = getConfInfos(filepath)
            rep = getch.getch()
            if '1' in str(rep):
                #Compatible AV
                print(colored('\nCompatible antivirus \n', 'blue', 'on_white'))
                for key, av in avcompatibleDict.items():      
                    print(key)
            elif '2' in str(rep):
                desactiverAv = activationQuestion(disabledTools, 'activated', 'activate', '\nActivate antivirus \n', 'antivirus')            
                res = activationExec(desactiverAv, 1, 'activé', filepath, 'name = ')
            elif '3' in str(rep):
                activerAv = activationQuestion(activeTools, 'disabled', 'disable', '\nDisable antivirus \n', 'antivirus')
                res = activationExec(activerAv, 0, 'disabled', filepath, 'name = ')
            elif '4' in str(rep):
                os.remove(filepath)
                return -1
            if os.path.isfile(filepath2):
                activeToolsMod, disabledToolsMod = configReader(filepath2, 'module_name = ', 3)
                if '5' in str(rep):
                    #Liste des modules développés
                    screen.cprint(7,0, '\nModules développés \n')
                    for key, mod in dictMOD.items():      
                        screen.cprint(8,0, key+'\n')  
                elif '6' in str(rep):
                    desactiverMod = activationQuestion(disabledToolsMod, 'activés', 'activer', '\nActiver des modules \n', 'modules')            
                    res = activationExec(desactiverMod, 1, 'activé', filepath2, 'module_name = ')
                elif '7' in str(rep):
                    activerMod = activationQuestion(activeToolsMod, 'désactivés', 'désactiver', '\nDésactiver des modules \n', 'modules')
                    res = activationExec(activerMod, 0, 'désactivé', filepath2, 'module_name = ')
                elif '8' in str(rep):
                    os.remove(filepath2)
                    return False
            if 'e' in str(rep):
                return False
            print(limit)
    else:
        return False
    
def activationQuestion(disabledToolsLST, etat, actif, affichage, elem):
    '''
    Configuration mode - enable/disable av and modules
    Take av and modules list and things to be printed.
    Ask question for each tools in the list.
    Return av and modules list to be modified.
    ''' 
    avEtatAMod = []
    if len(disabledToolsLST) > 0:
        print(colored(affichage, 'blue', 'on_white'))
        for tool in disabledToolsLST:
            print("Do you want to " + actif + ' ' + colored(str(tool), 'grey', 'on_yellow')+" ? (y = yes, n = no)")
            while True:
                rep3 = getch.getch()
                if 'y' in str(rep3):
                    # print(" save ")
                    avEtatAMod.append(tool)
                    break
                elif 'n' in str(rep3):
                    # print(" unsave")
                    break
    else:
        print("All the " + elem + " are " + etat)
    return avEtatAMod
    
def activationExec(lstAv, toMod, newStat, filepath, theName):
    '''
    Rewrite .ini file (enable/disable) to take the changes into account
    Take av list and modules to enable/disable, 
    the value to write in the .ini file, it's printed value,
    and the path of the .ini file
    '''
    if len(lstAv) > 0:#Si des av sont à activer ou à désactiver
        # print(lstAv)
        #On copie le fichier ini dans une liste et on remplace les lignes "actives" le cas échéant
        f = open(filepath,'r')
        tempFile = f.readlines()
        newList = []
        f.close()
        # print(tempFile)
        # tempFile.remove('##\n')
        # tempFile.remove('\n')
        
        for item in tempFile:
            if '##' not in item:
                newList.append(item.replace('\n',''))
                # print(item)
        # print(newList)
        #Suppression et écriture du fichier .ini avec les nouveaux params
        os.remove(filepath)
        for i, line in enumerate(newList):
            if theName in line:
                if logManagement.extractSTR(newList[i], theName) in lstAv:
                    # print("hello")
                    name = theName + logManagement.extractSTR(newList[i], theName) 
                    actif = 'active = '+str(toMod)
                    print(logManagement.extractSTR(newList[i], theName) + ' is now ' + newStat)
                else:#on garde la conf d'origine
                    # print("non")
                    avname = newList[i]
                    if 'name = ' == theName:
                        actif = newList[i+1]
                    # else:
                        # present = newList[i+1]
                        # path = newList[i+2]
                        # actif = newList[i+3]
                   # print(line)
                f = open(filepath, 'a', encoding='utf-8', errors='ignore')
                if 'name = ' == theName:
                    f.write('##\n' + name + '\n' + actif + '\n')    
                # else:
                    # f.write('##\n'+avname+"\n"+present+"\n"+path+"\n"+actif+"\n")    
    return False    
    
if __name__ == '__main__':
    init()
        
    