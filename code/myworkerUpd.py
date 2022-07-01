#!/usr/bin/python3
import os
os.system('apt-get update&& apt-get install -y python3-pip python3-setuptools python3-pandas python3-yaml python3-requests&& apt-get install -y git curl psmisc p7zip-full wget')
import sys
import shutil
import time
from datetime import datetime
import threading
import signal
import csv

import json
import pandas as pd
import hashlib
import requests

import  mylib




def threadExit():
    os._exit(0)

timer1 = threading.Timer(18000.0, threadExit)
timer1.start()

pathToQuery = sys.argv[1]
pathToListHash = sys.argv[2]
languageForWork = sys.argv[3]
loginName = sys.argv[5].split('/')[0]
passName = sys.argv[4]
repoName = sys.argv[5].split('/')[1]
archivePass = sys.argv[6]
archiveUrl = sys.argv[7]

folderNameListHash = "/tmp/workshash/"
if os.path.exists(folderNameListHash):
    shutil.rmtree(folderNameListHash)
os.system('mkdir '+folderNameListHash)
os.system('cd '+folderNameListHash+' && wget '+archiveUrl+' -O 1.7z > /dev/null 2>&1')
os.system('cd '+folderNameListHash+' && 7z x 1.7z -p'+archivePass)
commonTable = pd.read_csv(folderNameListHash+'commonTable.csv')

folderName = "/tmp/works"
folderTMP = "/tmp/TMP"
folderPRJ = "/tmp/dbprj"
folderGitClone = "/tmp/GitClone"
file_csv_bad = folderName+"/noBuild.csv"
fieldnames = ['hash', 'createDB', 'sizeResult', 'buildTime']

mylib.installCodeql()



def threadCommit():
    mylib.save_repo_branch_commit(loginName,passName,repoName,folderName,branchName,"threadCommit add")
    timer = threading.Timer(1800.0, threadCommit)
    timer.start()

branchName = pathToQuery.splitlines()[0].split('/')[-1].split('.ql')[0]+'_'+pathToListHash.splitlines()[0].split('/')[-1]
commitText = "treading commit"
mylib.down_git_branch(loginName,passName,repoName,folderName,branchName)
threadCommit()


if not os.path.exists(file_csv_bad):
    with open(file_csv_bad, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)    
        writer.writeheader()
fileResultERR = open(file_csv_bad,"a+")
fileResultERR.seek(0, 0)
readFileResultERR = fileResultERR.readlines()
fileResultERR.close() 

with open(pathToListHash) as fileTmp:
    readFile = fileTmp.readlines()
    for i in readFile:
#        print(i)
        if i.splitlines()[0] in str(readFileResultERR):
            continue
        with open(file_csv_bad, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'hash': i.splitlines()[0],
                'createDB': 'NAN',
                'sizeResult': 'NAN',
                'buildTime': 'NAN'})                  
            csvfile.flush()
            os.fsync(csvfile.fileno())

        if len(commonTable.loc[commonTable['HASH'] == i.splitlines()[0]]['URL']) > 0:
            for urlForWork in commonTable.loc[commonTable['HASH'] == i.splitlines()[0]]['URL']:
                if  not urlForWork.startswith('https:'):
                    continue
                if os.path.exists(folderGitClone):
                    shutil.rmtree(folderGitClone)
                os.system("git clone "+urlForWork+" "+folderGitClone)
                if not os.path.exists(folderGitClone):
                    print('not clone project')
                    continue
                if os.path.exists(folderPRJ):
                    shutil.rmtree(folderPRJ)
                os.system("rm -rf "+folderGitClone+"/_lgtm*")
                os.system("echo 321 > /tmp/echoExitCode")
                dbFlagCreate = 0
                bqrsFlagCreate = 0            
                findTime = 0

                os.system("timeout 40m /opt/codeqlmy/codeql/codeql database create --language="+languageForWork+" --source-root="+folderGitClone+"  -- "+folderPRJ+" &&sudo echo $? > /tmp/echoExitCode")
                echoCode = open("/tmp/echoExitCode", 'r').read()

                if echoCode.startswith("0"):
                    dbFlagCreate = 1

                    file_csv = folderName+"/"+pathToQuery.splitlines()[0].split("/")[-1].split(".ql")[0]+".csv"   
                    if not os.path.exists(file_csv):
                        with open(file_csv, 'w', newline='') as csvfile:
                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)    
                            writer.writeheader()

                    fileResultOK = open(file_csv,"a+")
                    fileResultOK.seek(0, 0)
                    readFileResultOK = fileResultOK.readlines()
                    fileResultOK.close()    
                        
                    if i.splitlines()[0] in str(readFileResultOK):
                        continue
                        
                    if os.path.exists("bqrsprj.bqrs"):
                        os.remove("bqrsprj.bqrs")
                    if os.path.exists("/opt/codeqlmy/codeql-repo/"+languageForWork+"/ql/src/experimental/Security/CWE/CWE-XXX/"):
                        shutil.rmtree("/opt/codeqlmy/codeql-repo/"+languageForWork+"/ql/src/experimental/Security/CWE/CWE-XXX/")
                    if not os.path.exists("/opt/codeqlmy/codeql-repo/"+languageForWork+"/ql/src/experimental/Security/CWE/CWE-XXX/"):
                        os.system("mkdir -p /opt/codeqlmy/codeql-repo/"+languageForWork+"/ql/src/experimental/Security/CWE/CWE-XXX/")
                    os.system("cp "+pathToQuery.splitlines()[0]+" /opt/codeqlmy/codeql-repo/"+languageForWork+"/ql/src/experimental/Security/CWE/CWE-XXX/1.ql")
                    start_time = datetime.now()

                    os.system("timeout 40m /opt/codeqlmy/codeql/codeql query run --database="+folderPRJ+" --output=bqrsprj.bqrs -- /opt/codeqlmy/codeql-repo/"+languageForWork+"/ql/src/experimental/Security/CWE/CWE-XXX/1.ql")

                    end_time = datetime.now()
                    findTime = end_time - start_time
                    bqrsFlagCreate = 0
                    tmpTime = 0

                    if os.path.exists("bqrsprj.bqrs"):
                        bqrsFlagCreate = os.stat("bqrsprj.bqrs").st_size

                    
                        if os.path.isfile('/tmp/bqrsOutTmp'):
                            os.system('rm -rf /tmp/bqrsOutTmp')
                        os.system('/opt/codeqlmy/codeql/codeql bqrs info -- bqrsprj.bqrs >> /tmp/bqrsOutTmp')
                        if os.path.isfile('/tmp/bqrsOutTmp'):
                            with open('/tmp/bqrsOutTmp','r') as fileBQRStmp:
                                splitTmpOutBQRS = fileBQRStmp.read()
                                if not splitTmpOutBQRS.split('#select has ')[1].split(' rows and ')[0] == '0':
                                    tmpTime = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                                            
                                    if not os.path.exists(folderName+"/"+pathToQuery.splitlines()[0].split("/")[-1].split(".ql")[0]):
                                        os.system("mkdir "+folderName+"/"+pathToQuery.splitlines()[0].split("/")[-1].split(".ql")[0])
                                
                                    os.system("timeout 40m /opt/codeqlmy/codeql/codeql bqrs decode --output="+folderName+"/"+pathToQuery.splitlines()[0].split("/")[-1].split(".ql")[0]+"/"+str(tmpTime)+".csv --format=csv --entities=all -- bqrsprj.bqrs") 

                    with open(file_csv, 'a', newline='') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writerow({'hash': i.splitlines()[0],
                            'createDB': str(dbFlagCreate),
                            'sizeResult':str(bqrsFlagCreate),
                            'buildTime':str(findTime)+"_"+str(tmpTime)})                  
                        csvfile.flush()
                        os.fsync(csvfile.fileno())
        
                else:
                    with open(file_csv_bad, 'a', newline='') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writerow({'hash': i.splitlines()[0],
                            'createDB': str(dbFlagCreate),
                            'sizeResult':str(bqrsFlagCreate),
                            'buildTime':str(findTime)})                  
                        csvfile.flush()
                        os.fsync(csvfile.fileno())


mylib.save_repo_branch_commit(loginName,passName,repoName,folderName,branchName,"commit in end")
os._exit(0)
