import os
import signal
import sys
import subprocess
from threading import Timer
import pkg_resources
import subprocess
import pyric.pyw as pyw
import psutil
import tkinter as tk
import time


global pid
global isOn
isOn = False

def listWirelessInterfaces():
    p = subprocess.Popen(["iw", "dev"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, r = p.communicate(None)
    output = output.decode().replace("\n"," ").replace("\t","")
    output = output.split("Interface ")
    output.pop(0)
    return output



def checkMonitorMode(dev):
    global cardOk
    cardOk = False
    ifaces = pyw.interfaces()
    wifaces = pyw.winterfaces()
    if dev not in ifaces:
        return "Device "+dev+" is not valid"
    elif dev not in wifaces:
        return "Device "+dev+" is not wireless"    
    dinfo = pyw.devinfo(dev)
    card = dinfo['card']
    pinfo = pyw.phyinfo(card)


    if pinfo['modes'].count("monitor"):
        cardOk = True
        return "Device "+dev+" can be set into monitor mode"
    else:
        return "Device "+dev+" can NOT be set into monitor mode"

def setIntoMonitorMode(dev):
    dev="wlan0"
    command = ["sudo", "airmong-ng", "check", "kill"]
    p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, r = p.communicate(None)

    command = ["sudo", "airmon-ng", "start", dev]
    p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, r = p.communicate(None)
    return output

def resetMode(dev):
    dev="wlan0mon"
    command = ["sudo", "airmong-ng", "check", "kill"]
    p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, r = p.communicate(None)

    command = ["sudo", "airmon-ng", "stop", dev]
    p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, r = p.communicate(None)
    return output

async def scanForTargets(interface, path):
    global isOn
    isOn = True
    filePath = path+"/targets"
    command = ["airodump-ng", "-w", filePath, "--output-format", "csv", interface]
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
        filePath = path+"/targets-01.csv"
        #if doesnt exist say to start scan or pritn no data found
        with open(filePath, mode="r") as f:
            svScanResult.set("")
            lines = f.readlines()
            session.addLog("Read "+str(len(lines))+" lines of targets' scan")
        svScanResult.set("".join(lines))
        return 0
    else:
        session.addLog("Targets' scan is not ON, will not read file")
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
            os.rename(path+"/targets-01.csv", path+"/targets-"+str(time.time())+".csv")
            isOn = False
            return 0
    return -1