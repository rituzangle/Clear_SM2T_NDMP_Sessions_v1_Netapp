# -*- coding: utf-8 -*-
"""
Created on Wed Nov 26 10:21:24 2014

@author: rsangha

On filers - sometimes there are leftover ndmp sessions, called 
'orphanded snapmirror sessions', that are a tad tedious to remove.
This script will take the output of "snapmirror status|grep NDMP |grep Idle"
-throw it into-> filername+_smstatus.txt
then save the fields required by the snapmirror release command into another
 file -smReport
 It counts the idle sessions; if they are 0, it smiles for you.

"""
from __future__ import print_function #needed for python 2.7, which is default on most servers

import datetime 
import os
import sys 
import subprocess


today= str(datetime.date.today())
#print (os.system("pwd"))  #find pwd so I know where the output is.
def get_filer_name():
    
    #filername =  "fqdn_f_Filer.yahoo.com"
    filername = sys.argv[1]
    if not filername:
        filername= input("Usage: python idle_ndmp_session_releaser.py filername.prop.colo \n\nSo, give me a filer dude?: ")
    
        verifyinput=input( "my filer is "+ filername + " Correct!! ")
        #ssh fails if filer name is incorrect, which will be self-explainatory 
        #so leaving out those checks to keep things simple
        if verifyinput.upper() == 'Y':
            print("Cool dude - I'll work on", filername)
    else:
        print("My filer is !!!!", filername)      
        
    return(filername)

def get_sm_status(filername,sm_ndmp_report):
    #cmd is: ssh filername.prop.colo snapmirror status |grep NDMP|grep Idle")
    count_ndmp_cmd= "ssh "+filername + " snapmirror status|grep Idle|grep -c NDMP"
    proc = subprocess.Popen([count_ndmp_cmd], stdout=subprocess.PIPE, shell=True)
    (ndmp_count, err) = proc.communicate()

    if (int(ndmp_count) <1):
        print ("No Idle Sessions. Nothing to do :)")
    else:
        the_cmd = "ssh "+filername+ " snapmirror status |grep NDMP|grep Idle > "+sm_ndmp_report  #/homes/rsangha/pyspace/"+filername+"_smstatus.txt"
        os.system(the_cmd)
    
    return (filername+"_smstatus.txt")
    #returns filename ("/homes/rsangha/pyspace/filername-fqdn_smstatus.txt")    
    
def sm_releaser(smReportFile,filername):
    count_ndmp_cmd= "ssh "+filername + " snapmirror status|grep Idle|grep -c NDMP"
    proc = subprocess.Popen([count_ndmp_cmd], stdout=subprocess.PIPE, shell=True)
    (ndmp_count, err) = proc.communicate()

    if (int(ndmp_count) >0): 
        print ("Number of Stale/Idle NDMP Session(s) :", ndmp_count)
        for line in smReportFile:
            os.system(("ssh " + filername + " snapmirror release " + line))  
        print ("\nAll done.")

def main():
    the_dir = "/homes/rsangha/pyspace/"
    os.chdir(the_dir)
    filername = get_filer_name()
    sm_ndmp_report = os.path.join(the_dir,filername+"_smstatus.txt")
    smstatus = open(get_sm_status(filername, sm_ndmp_report),'rt')
    #new file  to save only the part needed by snapmirror release command
    smReport = open(os.path.join(the_dir,filername+"svOut.txt"),"wt")
     
    for line in smstatus: 

        fields = line.split(" ")
        f1=fields[0].split(":")         
        
        smfields=f1[1] + " " + fields[2] + "\n"
        smReport.write(smfields)

    smstatus.close()
    smReport.close()
    
    smReport = open(os.path.join(the_dir,filername+"svOut.txt"),"rt")
    sm_releaser(smReport,filername)
## end  main()  
    
if __name__ == "__main__":
    main()
    
