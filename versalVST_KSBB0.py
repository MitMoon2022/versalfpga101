#!/usr/bin/python

########################################################################################################
###### ps_pvtf_bench.python            			 	       										########
###### Main Python Wrapper for Versal PS and ME Systest-based PVTF     	       					########
###### usage - python ps_pvtf_bench.py -p <ParamFile> -t <Temperature> -s <SerialNumber>		########
########################################################################################################


#################################################################################################################
## IMPORTS

import sys
import os
import optparse
import subprocess
import threading
import collections
import random
import re
import tempfile
import datetime
import time
import filecmp
from filecmp import dircmp
from time import gmtime, strftime
import time
import json
import socket
import csv

#################################################################################################################
## CONSTANTS
c_STARTOFLINESTR		= 'SOF'
c_ENDOFLINESTR 			= 'EOF'
c_SCRIPTDIR			= os.path.dirname(os.path.realpath(__file__))+'/'
c_ROOTDIR			= os.path.abspath(os.path.join(c_SCRIPTDIR, os.pardir))+'/'
c_PARAMFILEDIR 			= c_ROOTDIR+"params/"
c_LOGDIR			= c_ROOTDIR+'logs/'
c_TOPLOGDIR			= c_LOGDIR+"top/"
c_JSONFILE			= c_SCRIPTDIR+"master_list.json"
c_VST_ROOTDIRS			= os.path.abspath(os.path.join(c_ROOTDIR, os.pardir))+'/'
c_BUILDIN_DIRS			= c_ROOTDIR+'tool/vn3716/'
c_VST_JSONDIRS			= c_ROOTDIR+'json/'
c_VSTLOGDIR                     = c_LOGDIR+'vstlogs/'
c_DNADIR                        = c_LOGDIR+'dna/'
c_RESULTDIR                     = c_LOGDIR+'result/'
c_HISTORYDIR			= c_LOGDIR+'history/'
c_TRACKDIR			= c_HISTORYDIR+'tracking/'
c_TESTDIR			= c_HISTORYDIR+'test/'
c_BOARDDIR                      = c_HISTORYDIR+'board/'
c_SITEDIR                       = c_HISTORYDIR+'site/'
c_BATCHDIR			= c_LOGDIR+'batch/'
c_SENDRESULT			= '/group/xap_charserv2/engineering/Characterization/charmnt/DATA_COLLECTION_POOL/vst_result_api.py'
#################################################################################################################
## GLOBALS

g_options 		= None
g_arguments		= None
g_temperature		= None
g_serialnum		= None
g_vstProgram		= None
g_vstTimestamp		= None
g_paramFilePath		= None
g_board			= None
g_boardsn		= None
g_hostname		= None
g_topLog		= None
g_dna                   = "NODNA-0_X0_Y0"
g_chipTemperature	= None
g_boardtype		= None
g_silicon_rev		= None
g_device		= None
g_package		= None


#################################################################################################################
## Run a shell command
def callCmd(cmd, *args):
    argsList = list(args)
    argsList = argsList[0].split()
    argsList.insert(0, cmd)
    ccmd = str(argsList)
    p = subprocess.Popen(argsList, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return (out, err, ccmd)


#################################################################################################################
## Run command with timeout
class Command(object):
    def __init__(self, cmd, runDir):
        self.cmd = cmd
        self.runDir = runDir
        self.process = None
        self.out = ""
        self.err = None
        items = cmd.split()
        if 'systest' == items[0].lower():
            self.systest = True
        else:
            self.systest = False

    def run(self, timeout):
        def target():
            print 'Thread started'
            self.process = subprocess.Popen(self.cmd, cwd=r'{0}'.format(self.runDir), shell=True, stdout=subprocess.PIPE, bufsize=1)
            while True:
                output = self.process.stdout.readline()
                if output == '' and self.process.poll() is not None:
                    break
                if output:
                    print output.strip()
                    #lines = output.strip()
                    #for line in lines:
                    #	os.system("echo {0}".format(line))
                    self.out += output


            #self.out, self.err = self.process.communicate()
            print 'Thread finished'


        thread = threading.Thread(target=target)
        thread.start()
        thread.join(int(timeout))

        if thread.is_alive():
            print 'Terminating process'
            os.system('ps -ef | grep systest')
            try:
                os.system("pkill -9 systest")
            except:
                print("Process already been killed")
            print 'Send pkill -9 systest'
            time.sleep(30)
            if not self.systest:
                try:
                    self.process.terminate()
                except:
                    print("Process already been terminated")
                thread.join()

        return self.process.returncode

    def get_out(self):
        return self.out


#################################################################################################################
## Print an error message to stdout and exit python

def printErr(errStr, exit=True):
    print ("> Error: " + errStr)
    if (exit):
        print "Exiting"
        sys.exit()
    return

#################################################################################################################
## print MSG to screen
def printMSGtoScreen(msg, times=1):
    for i in range(times):
        os.system("echo {0}".format(msg))
        #os.system("echo \n")


#################################################################################################################
## Set and print current timestamp (optionally also to stdout)
def formatTimestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

#################################################################################################################
## Print a fixed end message

def printEndMsg():
    print "\n*********************************************************"
    print "                   Integration test flow Done 					    "
    print "*********************************************************\r\n"
    cmd = "Integration test flow Done. Goodbye!"
    printMSGtoScreen(cmd, times=3)


def printAllFailMsg():
    cmd = "ALL TEST FAILED! CHECK SETUP!"
    printMSGtoScreen(cmd, times=3)

def printAllPassMsg():
    cmd = "ALL TEST PASS"
    printMSGtoScreen(cmd, times=3)

def printToplog(line, printStdout=False, createNewLog=False):
    global g_topLog
    writeAppend = 'w' if createNewLog else 'a'
    if (printStdout):
        os.system("echo "+line)
    f = open(g_topLog, writeAppend)
    f.write('{0}\n'.format(line))
    f.close()

def printVSTlog(vstLog, line, printStdout=False, createNewLog=False):
    writeAppend = 'w' if createNewLog else 'a'
    if (printStdout):
        printMSGtoScreen(line)
    f = open(vstLog, writeAppend)
    f.write('{0}\n'.format(line))
    f.close()

def printVIlog(msgType, msgDetail):
    msgType = msgType.replace("\r","").replace("\n","")
    msgDetail = msgDetail.replace("\r","").replace("\n","")
    string = "[VILOG]::{0}::{1}::[EOF]".format(msgType, msgDetail)
    printMSGtoScreen(string)

def saveDNA():
    global g_serialnum
    global g_dna

    f_path = '{0}/sn{1}_dna.txt'.format(c_DNADIR, g_serialnum).replace('//','/')
    f = open(f_path, 'w')
    f.write('{0}'.format(g_dna))
    f.close()


def isValidSN(serialnum):
    if len(serialnum) == 16 and re.match(r'X[0-9A-Z]{15}', serialnum):
        return True
    else:
        return False


def appendTrackingRecord():
    global g_serialnum
    global g_dna
    global g_hostname
    global g_temperature
    global g_boardsn

    f_path = '{0}/sn{1}_site.txt'.format(c_TRACKDIR,g_serialnum).replace('//','/')
    f = open(f_path, 'a')
    f.write('{0} {1} {2} {3} {4}\n'.format(formatTimestamp(time.time()), g_dna, g_hostname, g_boardsn, g_temperature))
    f.close()

def appendTestRecord(vstTestName, result, timestamp, temperature, vstLog):
    global g_serialnum
    global g_dna
    global g_hostname
    global g_temperature
    global g_boardsn

    f_path = '{0}/sn{1}.txt'.format(c_TESTDIR,g_serialnum).replace('//','/')
    f = open(f_path, 'a')
    f.write('{0} {1} {2} {3} {4} {5} {6} {7} {8}\n'.format(timestamp, g_dna, vstTestName, g_temperature, temperature, result, g_hostname, g_boardsn, vstLog))
    f.close()


def appendSiteRecord(vstTestName, result, timestamp):
    global g_serialnum
    global g_dna
    global g_hostname
    global g_temperature
    global g_boardsn

    f_path = '{0}/site_{1}.txt'.format(c_SITEDIR,g_hostname).replace('//','/')
    f = open(f_path, 'a')
    f.write('{0} {1} {2} {3} {4} {5} {6}\n'.format(g_boardsn, g_serialnum, g_dna, vstTestName, g_temperature, result, timestamp))
    f.close()

def appendBoardRecord(vstTestName, result, timestamp):
    global g_serialnum
    global g_dna
    global g_hostname
    global g_temperature
    global g_boardsn


    f_path = '{0}/board_{1}.txt'.format(c_BOARDDIR,g_boardsn).replace('//','/')
    f = open(f_path, 'a')
    f.write('{0} {1} {2} {3} {4} {5} {6}\n'.format(g_hostname, g_serialnum, g_dna, vstTestName, g_temperature, result, timestamp))
    f.close()


def readTestResult(serialnum, temperature):

    f_path = '{0}/sn{1}_{2}_result.txt'.format(c_RESULTDIR,serialnum,temperature).replace('//','/')
    result = {}

    if os.path.isfile(f_path):
        f = open(f_path, 'r')
        content = f.readlines()
        for line in content:
            items = line.split('::')
            if len(items)==2:
                result[items[0].lower()] = items[1].replace('\n','').replace('\r','')
    else:
        print("No previous record")

    return result


def readSiteResult():
    global g_hostname

    f_path = '{0}/site_{1}.txt'.format(c_SITEDIR,g_hostname).replace('//','/')
    result = {}

    if os.path.isfile(f_path):
        f = open(f_path, 'r')
        content = f.readlines()
        for line in content:
            line = line.lower()
            items = line.split()
            if len(items)>=6:
                continuefailCNT = 0
                if items[3] in result:
                    continuefailCNT = result[items[3]]

                if items[5].upper()=='PASS':
                    continuefailCNT = 0
                else:
                    continuefailCNT = continuefailCNT + 1

                result[items[3]] = continuefailCNT

    return result


def writeTestResult(serialnum, temperature, vstResults):
    global g_dna
    global g_hostname
    mytimestamp = int(time.time())
    f_path = '{0}/sn{1}_{2}_result.txt'.format(c_RESULTDIR,serialnum,temperature).replace('//','/')
    f = open(f_path, 'w')
    for key in vstResults:
        result = '{0}::{1}'.format(key.upper(), vstResults[key])
        printMSGtoScreen(result)
        f.write('{0}\n'.format(result))	
    f.close()

def writeTestResultSummary(serialnum, temperature, vstResults):
    global g_dna
    global g_hostname
    mytimestamp = formatTimestamp(time.time())
    f_path = '{0}/summary.log'.format(c_RESULTDIR).replace('//','/')
    f = open(f_path, 'a')
    result = '{0} {1} {2} {3} '.format(serialnum, g_dna, g_hostname, mytimestamp)
    for key in vstResults:
        result += '{0}::{1} '.format(key.upper(), vstResults[key])
    f.write('{0}\n'.format(result))
    f.close()

def summaryResult():
    global g_vstTimestamp
    global g_device
    global g_dna
    global g_chipTemperature
    global g_serialnum

    f_path = '{0}/sn{1}_{2}_result.txt'.format(c_RESULTDIR,g_serialnum,temperature).replace('//','/')
    r_path = '{0}/{1}_VST_SummaryResult.csv'.format(c_LOGDIR,g_device).replace('//','/')
    with open(f_path, 'r') as f:
        lines = f.readlines()
        output = ''.join(lines[:9])
        output = output.replace("::", ",")
    with open(r_path, "a", newline="") as f:
        f.write('{0},{1},{2},{3},{4}'.format(g_serialnum,g_dna,g_chipTemperature,g_hostname,output))


def updateSerialNumberToBatchLookupTable(serialnum, batch):
    if isValidSN(serialnum):
        f_path = '{0}/{1}.txt'.format(c_BATCHDIR, serialnum).replace('//','/')
        with open(f_path, 'w') as f:
            f.write(batch)
            print('{0} {1}'.format(serialnum, batch))



#################################################################################################################
## Parsing JSON file

def parsingVSTList(json_file):
    global g_boardtype
    global g_silicon_rev
    global g_device
    global g_package


    fp = open(json_file)
    items = json.load(fp)

    json_dict = {}

    #print(c_VST_JSONDIRS)
    json_files = [pos_json for pos_json in os.listdir(c_VST_JSONDIRS) if pos_json.endswith('.json')]
    for json_file in json_files:
        item = json_file.replace('.json','')
        fname = '{0}/{1}'.format(c_VST_JSONDIRS,json_file)
        if item in json_dict.keys():
            printMSGtoScreen('Test {0} already exited {1}'.format(item, json_dict[item]))
        #printMSGtoScreen('Add {0} : {1} into VST test case'.format(item, fname))
        json_dict[item]=fname


    #print(c_VST_ROOTDIRS)
    for path in [c_BUILDIN_DIRS, c_VST_ROOTDIRS]:
        filenames = os.listdir(path)
        for filename in filenames: # loop through all the files and folders
            if '_' == filename[0]:
                continue

            if os.path.isdir(os.path.join(path, filename)): # check whether the current object is a folder or not
                fname = "{0}/{1}/TestProgram/setting.json".format(path, filename)
                if os.path.isfile(fname):
                    if filename in json_dict.keys():
                        printMSGtoScreen('Test {0} already exited {1}'.format(filename, json_dict[filename]))
                    #printMSGtoScreen('Add {0} : {1} into VST test case'.format(filename, fname))
                    json_dict[filename]=fname


    for key in items.keys():
        if key in json_dict.keys():
            printMSGtoScreen('Test {0} already exited {1}'.format(key, json_dict[key]))
        json_dict[key] = items[key]

    vst_dict = {}
    for key in json_dict.keys():
        vst_fp = open(json_dict[key])
        vst_info = json.load(vst_fp)
        config = {}
        pwd = os.path.dirname(json_dict[key])

        if 'EXE_SCRIPT' not in vst_info or 'TIMEOUT' not in vst_info or 'VSTname' not in vst_info:
            printMSGtoScreen("JSON {0} not Complete".format(key))
            continue

        if 'CHK_SCRIPT' not in vst_info or 'CHK_STRING' not in vst_info:
            printMSGtoScreen("JSON {0} not Complete".format(key))
            continue

        if 'ACF' not in vst_info or 'DBGLOG' not in vst_info:
            printMSGtoScreen("JSON {0} not Complete".format(key))
            continue

        if 'DEVICE' in vst_info:
            g_device = vst_info['DEVICE']

        if 'PACKAGE' in vst_info:
            g_package = vst_info['PACKAGE']

        if 'SILICONVERSION' in vst_info:
            g_silicon_rev = vst_info['SILICONVERSION']

        if 'BOARDTYPE' in vst_info:
            g_boardtype = vst_info['BOARDTYPE']

        config['VSTname'] = vst_info['VSTname']
        config['CHK_STRING'] = vst_info['CHK_STRING'].replace('[PWD]', pwd)
        config['ACF'] = vst_info['ACF'].replace('[VSTname]',config['VSTname']).replace('[PWD]', pwd)
        config['DBGLOG'] = vst_info['DBGLOG'].replace('[VSTname]',config['VSTname']).replace('[PWD]', pwd)
        config['EXE_SCRIPT'] = vst_info['EXE_SCRIPT'].replace('[DBGLOG]',config['DBGLOG']).replace('[ACF]',config['ACF']).replace('[VSTname]',config['VSTname']).replace('[PWD]', pwd)
        config['TIMEOUT'] = vst_info['TIMEOUT']
        config['CHK_SCRIPT'] = vst_info['CHK_SCRIPT'].replace('[DBGLOG]',config['DBGLOG']).replace('[ACF]',config['ACF']).replace('[VSTname]',config['VSTname']).replace('[PWD]', pwd)
        config['CHK_SCRIPT'] = config['CHK_SCRIPT'].replace('[CHK_STRING]',config['CHK_STRING'])
        config['PWD'] = pwd

        vst_dict[key.lower()] = config

    return vst_dict


#################################################################################################################
## Convert into execute command string
def parsingCommand(rawString, convertTemperature =False):
    global g_dna
    global g_board
    global g_boardsn
    global g_hostname
    global g_temperature
    global g_serialnum
    global g_vstTimestamp
    global g_corner
    global g_voltage


    if not g_boardsn:
        g_boardsn = 'None'
    if not g_board:
        g_board = 'None'


    DNASplit = g_dna.replace('-','_').split('_')

    rawString = rawString.replace('[SN]', g_serialnum.upper())
    rawString = rawString.replace('[sn]', g_serialnum.lower())
    if convertTemperature :
        rawString = rawString.replace('[TEMP]', g_temperature.replace('m','-').replace('n','-'))
    else:
        rawString = rawString.replace('[TEMP]', g_temperature)
    rawString = rawString.replace('[BOARDSN]', g_boardsn)
    rawString = rawString.replace('[BOARD]', g_board)
    rawString = rawString.replace('[HOST]', g_hostname)
    rawString = rawString.replace('[DNA]', g_dna)
    rawString = rawString.replace('[LOT]', DNASplit[0])
    rawString = rawString.replace('[TIMESTAMP]', g_vstTimestamp)
    rawString = rawString.replace('[CN]', g_corner)
    rawString = rawString.replace('[Voltage]', g_voltage)

    return rawString


#################################################################################################################
## Parse Param file
def parseParamFile(paramFile):
    paramFilePath = ("{0}/{1}".format(c_PARAMFILEDIR, paramFile)).replace("//", "/")
    realInfo = False
    readheaderInfo = False
    headerInfo = []
    paramInfoArray = []

    if not os.path.isfile(paramFilePath):
        printErr("Could not find parameter file: {0}".format(paramFilePath))
        return paramInfoArray

    paramInfoArray.append({'Index': '0', 'Test_Suite': 'killsystest', 'Timeout': '300', 'Voltage': ''})
    paramInfoArray.append({'Index': '0', 'Test_Suite': 'read_dna', 'Timeout': '300', 'Voltage': ''})

    with open(paramFilePath,'r') as fp:
        Lines = fp.readlines() 
        for line in Lines: 

            if c_ENDOFLINESTR in line:
                realInfo = False
            elif realInfo:
                items = line.split()
                if readheaderInfo:
                    readheaderInfo = False
                    headerInfo = items
                else:
                    record = {}
                    for i in range(len(headerInfo)):
                        record[headerInfo[i]] = items[i]
                    paramInfoArray.append(record)


            elif c_STARTOFLINESTR in line:
                # Begin real info
                realInfo = True
                readheaderInfo = True

    return paramInfoArray

#################################################################################################################
## Decode Test suit format
def decodeTestSuitFormat(testsuit):
    items = testsuit.upper().split('_')

    if len(items) >= 3 and re.match(r'R[0-9]{3}', items[-1]):
        print('Valid Testprogram format {0}'.format(testsuit))
        TPname = testsuit.upper().replace('_{0}'.format(items[-1]), '').replace('_{0}'.format(items[-2]), '')
        PWR = items[-2]
        Rev = items[-1]
        return [TPname, PWR, Rev]
    else:
        print('Invalid Testprogram format {0}'.format(testsuit))
        return [testsuit.upper(),'MP','R001']




#################################################################################################################
## Decode VST log
def decodeVSTLog(line):
    global g_dna
    global g_boardsn
    global g_chipTemperature
    global g_boardtype
    global g_silicon_rev
    global g_device
    global g_package

    if "[VILOG]::" in line and "::[EOF]" in line:
        # VI LOG message
        items = line.split("::")
        if len(items) == 4:
            # correct format
            msgType = items[1].upper()
            msgData = items[2].upper()

            if msgType == "DNA":
                g_dna = msgData
            elif msgType == "TEMPERATURE":
                g_chipTemperature = msgData
            elif msgType == "BOARDSN":
                g_boardsn = msgData
            elif msgType == "BOARDTYPE":
                g_boardtype = msgData
            elif msgType == "SILICONVERSION":
                g_silicon_rev = msgData
            elif msgType == "DEVICE":
                g_device = msgData
            elif msgType == "PACKAGE":
                g_package = msgData
            else:
                print("{0} {1}".format(msgType, msgData))


## Check VST result
def checkVSTResult(vstlog, scriptOut, passString):
    global g_dna
    global g_boardsn
    global g_chipTemperature

    result = 'FAIL'
    f=open(vstlog, "a")
    scriptOut.seek(0)
    for line in scriptOut:
        f.write(line+'\n')
        print(line)
        if passString in line:
            result = 'PASS'
        elif 'VST_TESTED' in line:
            result = 'TEST'

        decodeVSTLog(line)

    f.close()
    return result



## Check VST output log
def checkVSTOutputLog(vstlog, scriptOut):

    f=open(vstlog, "a")
    outlog = scriptOut.splitlines()
    for line in outlog:
        if len(line.strip()) > 0:
            decodeVSTLog(line)
            #print(line)
            f.write(line+'\n')

    f.close()


#################################################################################################################
## Returns true if any systest process is running, else false

def systestIsRunning():
    systestProcessStrs = ["systest-client", "systest"]
    (out, err, ccmd) = callCmd('ps', '-ef')
    stCount = 0

    try:
        for line in out.split('\n'):
            if ((any(x in line for x in systestProcessStrs)) and ('grep' not in line) and ('echo' not in line)):
                print("> Systest already running: {0}".format(line))
                stCount = stCount + 1
    except Exception as e:
        print "Unexpected exception in systestIsRunning(): {0}".format(e)
    if stCount > 0:
        return True
    return False


#################################################################################################################
## Main function

def main():

    global g_options
    global g_arguments
    global g_temperature
    global g_serialnum
    global g_vstProgram
    global g_paramFilePath
    global g_board
    global g_boardsn
    global g_hostname
    global g_dna
    global g_topLog
    global g_chipTemperature
    global g_vstTimestamp
    global g_boardtype
    global g_silicon_rev
    global g_device
    global g_package
    global g_corner
    global g_voltage




    ####################################################
        ### Check system folders
    for folder in [c_LOGDIR, c_TOPLOGDIR, c_VSTLOGDIR, c_PARAMFILEDIR, c_DNADIR, c_RESULTDIR, c_HISTORYDIR, c_TRACKDIR, c_TESTDIR, c_BOARDDIR, c_SITEDIR, c_BATCHDIR]:
        if (not (os.path.isdir("{0}".format(folder)))):
            subprocess.call(['mkdir', '-p', '%s' %(folder)])
            subprocess.call(['chmod', '777', '%s' %(folder)])
    ####################################################

    timestamp = int(time.time())
    start_Time = formatTimestamp(time.time())

    opts = optparse.OptionParser()

    opts.add_option("-p",	dest = "Params_File", type = "string",     default = None,      help = "Parameters Filename [REQUIRED]")
    opts.add_option("-k",	dest = "VST_KEY",     type = "string",     default = None,      help = "VST test case name if no param file [REQUIRED]")
    opts.add_option("-t",	dest = "TEMP",	      type = "string",     default = None,      help = "Temperature Setting [REQUIRED]")
    opts.add_option("-s",	dest = "serialNum",   type = "string",	   default = None,      help = "Serial Number [REQUIRED]")
    opts.add_option("-b",	dest = "board",       type = "string",     default = "vn3716", help = "Board [default: ksb vn3716]")
    opts.add_option("-c",	dest = "hostName",    type = "string",     default = None,      help = "Test Hostname [default: unknown]")
    opts.add_option("-f",   dest = "force",       action="store_true", default = False,     help = "Force to run")
    opts.add_option("-d",  	dest = "dummyRun",    action="store_true", default = False,     help = "Dummy run (no side effects) [default: False]")
    opts.add_option("-x",   dest = "batch",       type="string", default = None,     help = "Random 2D barcode Batch number")
    opts.add_option("-z",   dest = "corner",       type="string", default = None,     help = "Process corner")

    (g_options, g_arguments) = opts.parse_args()

    resultsMatrix 	= []
    domainName 		= []
    paramLines 		= []
    LNum 			= []

    printMSGtoScreen( "=========================================================")
    printMSGtoScreen( "         Welcome to VST integrated test flow             ")
    printMSGtoScreen( "=========================================================")

    print "Params: {0}".format(g_options.Params_File)
    print "VST key: {0}".format(g_options.VST_KEY)
    print "Temperature: {0}".format(g_options.TEMP)
    print "SN: {0}".format(g_options.serialNum)
    if None in [g_options.TEMP, g_options.serialNum]:
        printMSGtoScreen("Please define as a minimum the Temperature and Serial Number")
        return

    if not any([g_options.Params_File, g_options.VST_KEY]):
        printMSGtoScreen("Please define as a minimum the Parameter file, or VST key")
        return

    g_temperature   = g_options.TEMP.lower()
    g_serialnum     = g_options.serialNum.upper()
    g_corner = g_options.corner.lower()
    if (g_options.board is not None):
        g_board = g_options.board.lower()

    if (g_options.hostName is not None):
        g_hostname = g_options.hostName.lower()
    else:
        g_hostname = socket.gethostname()


    if g_options.batch is not None:
        print('{0} {1}'.format(g_serialnum, g_options.batch))
        updateSerialNumberToBatchLookupTable(g_serialnum, g_options.batch)

    if g_options.Params_File is None:
        g_vstProgram = g_options.VST_KEY
        g_topLog        = "{0}/sn{1}_{2}_{3}_{4}.log".format(c_TOPLOGDIR, g_serialnum, g_vstProgram, g_temperature, timestamp)
        paramInfoArray = []
        paramInfoArray.append({'Index': '0', 'Test_Suite': 'killsystest', 'Timeout': '300'})
        paramInfoArray.append({'Index': '1', 'Test_Suite': 'read_dna', 'Timeout': '300'})
        paramInfoArray.append({'Index': '2', 'Test_Suite': g_options.VST_KEY, 'Timeout': '3600'})
    else:
        g_vstProgram = g_options.Params_File
        g_topLog        = "{0}/sn{1}_{2}_{3}_{4}.log".format(c_TOPLOGDIR, g_serialnum, g_vstProgram, g_temperature, timestamp)
        paramInfoArray = parseParamFile(g_options.Params_File)


    test_pass = 0


    printToplog("SN: {0}".format(g_serialnum), printStdout=True, createNewLog=True)
    printToplog("Test site: {0}".format(g_hostname), printStdout=True)
    printToplog("Temperature: {0}".format(g_temperature.replace("m","-")), printStdout=True)

    vstlist = parsingVSTList(c_JSONFILE)

    allTestPass = True
    vstFullTestResult = readTestResult(g_serialnum, g_temperature)
    vstSiteResult = readSiteResult()

    for paramInfo in paramInfoArray:
        index = paramInfo['Index']
        testSuite = paramInfo['Test_Suite'].lower()
        testTimeout = paramInfo['Timeout']
        g_voltage = paramInfo['Voltage']
        testLoop = 1
        testForce = 0
        testOut = 0

        if 'Loop' in paramInfo:
            testLoop = int(paramInfo['Loop'])
        if 'Force' in paramInfo:
            testForce = int(paramInfo['Force'])
        if 'Out' in paramInfo:
            testOut = int(paramInfo['Out'])

        if testSuite in ["read_dna", "killsystest", "contact_check"]:
            # special test program
            testForce = 1

        if testSuite in ["read_dna"]:
            testOut = 1

        # if no systest is running, just skip this round
        if testSuite == "killsystest":
            if not systestIsRunning():
                print("No systest is running, skip kill systest")
                continue

        for i in range(testLoop):

            printMSGtoScreen("===========================================")
            printMSGtoScreen("Start test suite {0}".format(testSuite))
            printMSGtoScreen("Test flow start time {0}".format(start_Time))

            testSuit_start_time =  formatTimestamp(time.time())
            g_vstTimestamp = testSuit_start_time.replace(' ','').replace('-','').replace(':','')

            ret = -1

            vstResult = "FAIL"
            if testSuite in vstlist:

                if testSuite in vstFullTestResult:
                    vstResult = vstFullTestResult[testSuite]
                    print('Previous vst test result is {0}'.format(vstResult))

                if g_options.force==False and testForce!=1 and re.match('PASS',vstResult) and isValidSN(g_serialnum):
                    print('Unit already pass this {0} test, continue next test'.format(testSuite))
                    ret = 0
                    test_pass = 1
                    continue

                vstLog = "{0}/sn{1}_{2}_{3}.log".format(c_VSTLOGDIR, g_serialnum, testSuite, g_vstTimestamp).replace("//", "/")
                items = vstlist[testSuite]
                vstName = items['VSTname']
                acfLog = parsingCommand(items['ACF'], convertTemperature=True)
                dbgLog = parsingCommand(items['DBGLOG'], convertTemperature=True)
                cmdExe = parsingCommand(items['EXE_SCRIPT'])
                timeout = items['TIMEOUT']
                cmdChk = parsingCommand(items['CHK_SCRIPT'], convertTemperature=True)
                chkStr = parsingCommand(items['CHK_STRING'])

                printVSTlog(vstLog, "VST Test programe: {0}".format(vstName), printStdout=True, createNewLog=True)
                printVSTlog(vstLog, "Serial Number: {0}".format(g_serialnum), printStdout=True)
                printVSTlog(vstLog, "DNA: {0}".format(g_dna), printStdout=True)
                printVSTlog(vstLog, "Host: {0}".format(g_hostname), printStdout=True)
                printVSTlog(vstLog, "Board SN: {0}".format(g_boardsn))
                printVSTlog(vstLog, "Temperature: {0}".format(g_temperature.replace("m","-")))
                printVSTlog(vstLog, "Chip temperature: {0}".format(g_chipTemperature), printStdout=True)
                printVSTlog(vstLog, "Execute command: {0}".format(cmdExe), printStdout=True)
                printVSTlog(vstLog, "Timeout: {0}".format(timeout), printStdout=True)
                printVSTlog(vstLog, "Running directory: {0}".format(items['PWD']), printStdout=True)
                printVSTlog(vstLog, "Check result command: {0}".format(cmdChk), printStdout=True)
                printVSTlog(vstLog, "Check string: {0}".format(chkStr), printStdout=True)
                printVSTlog(vstLog, "ACF file: {0}".format(acfLog), printStdout=True)
                printVSTlog(vstLog, "DBG log: {0}".format(dbgLog), printStdout=True)
                printVSTlog(vstLog, "Test start time: {0}".format(testSuit_start_time))

                command = Command(cmdExe, items['PWD'])
                ret = command.run(timeout=timeout)
                out_log = command.get_out()
                checkVSTOutputLog(vstLog, out_log)
                end_time = formatTimestamp(time.time())
                printVSTlog(vstLog, "Test end time: {0}".format(end_time), printStdout=True)

                if ret == 0:
                    #p = subprocess.Popen(cmdChk.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    #out, err = p.communicate()
                    #out = os.popen(cmdChk, cwd=items['PWD']).read()
                    with tempfile.TemporaryFile() as tempf:
                        subprocess.call(cmdChk.split(), stdout=tempf, cwd='{0}'.format(items['PWD']))
                        vstResult = checkVSTResult(vstLog, tempf, chkStr)

                printVSTlog(vstLog, "Test result: {0}".format(vstResult), printStdout=True)

                printVIlog("TPname",vstName)
                printVIlog("DBG","BoardSN {0}".format(g_boardsn))
                printVIlog("DBG","Temperature {0}".format(g_temperature.replace("m","-")))
                printVIlog("DBG","Test start time {0}".format(testSuit_start_time))
                printVIlog("DBG","Test end time {0}".format(end_time))
                printVIlog("RESULT", vstResult)


                if testSuite == "read_dna":
                    # special process for read_dna
                    appendTrackingRecord()
                    if g_dna=="InvalidDNA":
                        printToplog("> Invalid DNA - could not read ID registers")
                        printVIlog("DNA","")
                        printVIlog("FATAL","Invalid DNA - could not read ID register")
                        time.sleep(10)
                        printAllFailMsg()
                    saveDNA()

                    printToplog("DNA: {0}".format(g_dna), printStdout=True)
                    printToplog('Board SN: {0}'.format(g_boardsn), printStdout=True)
                    printToplog("Chip Temperature: {0}".format(g_chipTemperature), printStdout=True)
                    printVIlog("DNA","{0}".format(g_dna))


                vstFullTestResult[testSuite.lower()] = vstResult
                appendSiteRecord(testSuite.upper(), vstResult, g_vstTimestamp)
                appendBoardRecord(testSuite.upper(), vstResult, g_vstTimestamp)
                appendTestRecord(testSuite.upper(), vstResult, g_vstTimestamp, g_chipTemperature, vstLog)
                writeTestResult(g_serialnum, g_temperature, vstFullTestResult)


                #[TPname, PWR, Rev] = decodeTestSuitFormat(testSuite)
                # python c_SENDRESULT -d VC1902 -x es2 -p A2197 -i API_TEST -r r001 -n {0} -s X999312341500032 -a T8P425-5_X12_Y5 -t m40 -v LHP -o PASS -z xapvst01 -b bsn -l xxx.log'.format(timestamp)
                #cmd = 'python {0} -d {1} -x {2} -p {3} -i {4} -r {5} -n {6} -s {7} -a {8} -t {9} -v {10} -o {11} -z {12} -b {13} -l {14}'.format(c_SENDRESULT, g_device, g_silicon_rev, g_package, TPname, Rev, g_vstTimestamp, g_serialnum, g_dna, g_chipTemperature, PWR, vstResult, g_hostname, g_boardsn, vstLog)
                #print(cmd)
                #os.system(cmd)


                if vstResult!="PASS":
                    allTestPass = False

                    if testSuite in vstSiteResult:
                        continueFailCount = vstSiteResult[testSuite] + 1

                        if continueFailCount >= 5:
                            printMSGtoScreen("{0} WARNING Continuously test failing detected at {1} for {2} times".format(testSuite, g_hostname, continueFailCount))


                    if 1 == testOut:
                        # Test Failed, exit test loop
                        printVSTlog(vstLog, "Test {0} Failed, exited current test suit".format(testSuite), printStdout=True)
                        writeTestResultSummary(g_serialnum, g_temperature, vstFullTestResult)
                        return

            else:
                printVIlog("DBG", "UNKNOW TEST suite {0}".format(testSuite))
                time.sleep(10)

            if ret == 0:
                test_pass = 1


            testSuit_end_time = formatTimestamp(time.time())
            cmd = "echo Test suite " + testSuite + " finished! and result is " + str(ret)
            printMSGtoScreen(cmd)
            printToplog("TEST {0}::START {1}::End {2}::Result {3}".format(testSuite, testSuit_start_time, testSuit_end_time, vstResult), printStdout=True)
            printMSGtoScreen("===========================================")

    #summaryResult()
    printMSGtoScreen("===========================================")
    end_Time = formatTimestamp(time.time())
    printToplog("TEST {0}::START {1}::End {2}::Result {3}".format(g_vstProgram, start_Time, end_Time, test_pass), printStdout=True)


    printMSGtoScreen("Start Time {0}".format(start_Time))
    printMSGtoScreen("End Time {0}".format(formatTimestamp(time.time())))
    time.sleep(10)

    writeTestResult(g_serialnum, g_temperature, vstFullTestResult)

    writeTestResultSummary(g_serialnum, g_temperature, vstFullTestResult)

    if allTestPass:
        printAllPassMsg()

    if test_pass == 1:
        printEndMsg()
    else:
        printAllFailMsg()


#################################################################################################################
## Run main

if __name__ == "__main__":
    main()
