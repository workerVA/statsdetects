
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
loginName = sys.argv[4].split('/')[0]
passName = sys.argv[3]
repoName = sys.argv[4].split('/')[1]
archivePass = sys.argv[5]
archiveUrl = sys.argv[6]

folderNameListHash = "/tmp/workshash/"
if os.path.exists(folderNameListHash):
    shutil.rmtree(folderNameListHash)
os.system('mkdir '+folderNameListHash)
os.system('cd '+folderNameListHash+' && wget '+archiveUrl+' -O 1.7z > /dev/null 2>&1')
os.system('cd '+folderNameListHash+' && 7z x 1.7z -p'+archivePass)
commonTable = pd.read_csv(folderNameListHash+'commonTable.csv')

folderName = "/tmp/works"
folderGitClone = "/tmp/GitClone"
file_csv_bad = folderName+"/noBuild.csv"
fieldnames = ['hash', 'line', 'regex', 'end_url']

def threadCommit():
    mylib.save_repo_branch_commit(loginName,passName,repoName,folderName,branchName,"threadCommit add")
    timer = threading.Timer(1800.0, threadCommit)
    timer.start()

branchName = pathToQuery.splitlines()[0].split('/')[-1].split('.rgxp')[0]+'_'+pathToListHash.splitlines()[0].split('/')[-1]
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
        print(i)
        if i.splitlines()[0] in str(readFileResultERR):
            print('skeep work')
            continue
        with open(file_csv_bad, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'hash': i.splitlines()[0],
                'line': 'NAN',
                'regex': 'NAN',
                'end_url': 'NAN'})                  
            csvfile.flush()
            os.fsync(csvfile.fileno())

        if len(commonTable.loc[commonTable['HASH'] == i.splitlines()[0]]['URL']) > 0:
            for urlForWork in commonTable.loc[commonTable['HASH'] == i.splitlines()[0]]['URL']:
                if  not urlForWork.startswith('https:'):
                    continue
                if os.path.exists(folderGitClone):
                    shutil.rmtree(folderGitClone)

                os.system("timeout 20m git clone "+urlForWork+" "+folderGitClone)
                if not os.path.exists(folderGitClone):
                    continue



                file_csv = folderName+"/"+pathToQuery.splitlines()[0].split("/")[-1].split(".rgxp")[0]+".csv"   
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
                with open(pathToQuery) as file_in:
                    for findStr in file_in:
                        mylib.gogo_fidt(findStr,i.splitlines()[0],file_csv,folderGitClone)


mylib.save_repo_branch_commit(loginName,passName,repoName,folderName,branchName,"commit in end")
os._exit(0)
