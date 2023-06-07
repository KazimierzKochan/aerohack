import subprocess
import psutil
import signal
import os

global pid

def getSugestedScans():
    suggestedScans = [
        "nmap -sV -p 21,22,80,9999 ",
        "nmap -p 1-100 ",
        "nmap "
    ]
    return suggestedScans

def getTestScan():
    with open("scan.txt", "r") as f:
        lstContent = f.readlines()
        f.close()
        return lstContent

async def executeScan(command, svScanResult, session):
    command = command.split(" ")
    #deny executing different commands
    if command[0] != "nmap":
        return 0
    
    host = command[-1]
    response = os.system("ping -c 1 " + host)
    if response == 0:
        svScanResult.set(svScanResult.get()+host+" is up, scan will be executed\n")
        session.addLog(host+" is up, scan will be executed\n")
    else:
        svScanResult.set(svScanResult.get()+host+" is down, not executing scan\n")
        session.addLog(host+" is down, not executing scan")
        return -1

    session.addLog("Executing scan: "+str(command))
    p = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8"
    )
    global pid
    pid = p.pid

    while True:
        realtimeOutput = p.stdout.readline()

        if(realtimeOutput == "" and p.poll() is not None):
            break
        if(realtimeOutput):
            svScanResult.set(svScanResult.get()+realtimeOutput)

    return p.returncode

def checkKillSynFlood():
	global pid
	if not "pid" in globals():
		return -1
	if not pid:
		return -1
	if pid != -1:
		if psutil.pid_exists(pid):
			os.kill(pid, signal.SIGKILL)
			return 0
	return -1


