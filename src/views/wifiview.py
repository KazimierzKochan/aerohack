import asyncio
from threading import Thread
import tkinter as tk
from tkinter import filedialog
from utils import project
from utils import wifiutils
from graphics import style
import socket
import netifaces as ni

def prepareView(tab, session):
	# ------------------------------ Configuration ------------------------------ #

	viewFrame = tk.Frame(tab, bg=style.LIGHTMEDIUMGRAY, bd=0)
	viewFrame.pack(expand=True, fill="both")

	viewFrame.columnconfigure(0, weight=1)
	viewFrame.columnconfigure(1, weight=1)
	viewFrame.columnconfigure(3, weight=1)
	viewFrame.columnconfigure(4, weight=1)
	
	viewFrame.rowconfigure(1, weight=1)
	

	# ------------------------------ Titles ------------------------------ #
	lblTargetTitle = tk.Label(
		viewFrame,
		text="Target WiFi",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblTargetTitle.grid(row=0, column=0, columnspan=2, sticky="nws")

	lblDevicesTitle = tk.Label(
		viewFrame,
		text="Conncted Devices",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblDevicesTitle.grid(row=0, column=3, columnspan=3, sticky="nws")

	lblHandshakesTitle = tk.Label(
		viewFrame,
		text="WPA2 4-way-hadshake",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblHandshakesTitle.grid(row=3, column=0, columnspan=2, sticky="nws")

	lblConnectTitle = tk.Label(
		viewFrame,
		text="Connection",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblConnectTitle.grid(row=3, column=3, columnspan=2, sticky="nws")

	lblLogsTitle = tk.Label(
		viewFrame,
		text="Last actions",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblLogsTitle.grid(row=6, column=0, columnspan=6, sticky="nws")


	# ------------------------------ Target network ------------------------------ #
	scrlNetworkY = tk.Scrollbar(
		viewFrame
	)
	scrlNetworkY.grid(row=1,column=2,sticky="nws")

	lstNetwork = tk.Listbox(
		viewFrame,
		yscrollcommand = scrlNetworkY.set
	)
	lstNetwork.grid(row=1,column=0,sticky="nwes", rowspan=1, columnspan=2)

	scrlNetworkY.config(command = lstNetwork.yview)

	lstTargets = ["No target selected yet"]
	for line in lstTargets:
		lstNetwork.insert(tk.END, line)

	# ------------------------------ Connected devices ------------------------------ #

	scrlDevicesY = tk.Scrollbar(
		viewFrame
	)
	scrlDevicesY.grid(row=1,column=5,sticky="nws")

	lstDevices = tk.Listbox(
		viewFrame,
		yscrollcommand = scrlDevicesY.set
	)
	lstDevices.grid(row=1,column=3,sticky="nwes", columnspan=2)

	scrlDevicesY.config(command = lstDevices.yview)

	lstClients = ["No target selected yet"]
	for line in lstClients:
		lstDevices.insert(tk.END, line)	


	# ------------------------------ Manage scan ------------------------------ #

	def StartTargetScan():
		if session.selectedInterface.get().split():
			bssid = session.target.get()
			if bssid:
				bssid = bssid.split()[0].replace(",","")
				session.addLog("Got bssid from setup "+bssid)
				svLogs.set(svLogs.get()+"Got bssid from setup"+bssid+"\n")
				pRet = asyncio.run(wifiutils.scanTargets(session.selectedInterface.get().split()[0], bssid, session))

	def btnStartTargetScanClicked():
		if not "monitor" in session.selectedInterface.get():
			session.addLog("Enable monitor mode to connect scan AP")
			svLogs.set(svLogs.get()+"Enable monitor mode to connect scan AP"+"\n")
			return 0
		session.addLog("Start scanning selected access point")
		svLogs.set(svLogs.get()+"Start scanning selected access point"+"\n")
		t1 = Thread(target=StartTargetScan)
		t1.start()
	
	btnStartTargetsScan = tk.Button(
		viewFrame,
		text = "Start scan",
		command=btnStartTargetScanClicked
	)
	btnStartTargetsScan.grid(row = 2, column=0, sticky="nwes")


	def btnStopTargetScanClicked():
		session.addLog("Trying to stop AP scan")
		svLogs.set(svLogs.get()+"Trying to stop AP scan"+"\n")
		stopped = wifiutils.checkKillScan(session.path.get())
		if stopped == -1:
			session.addLog("AP scan was not running")
			svLogs.set(svLogs.get()+"AP scan was not running"+"\n")
		else:
			session.addLog("AP scan was stopped")
			svLogs.set(svLogs.get()+"AP scan was stopped"+"\n")

	btnStopTargetScan = tk.Button(
		viewFrame,
		text="Stop scan",
		command=btnStopTargetScanClicked
	)
	btnStopTargetScan.grid(row = 2, column=1, sticky="nwes")

	def btnRefreshDevicesClicked():
		session.addLog("Refreshing target's information")
		svLogs.set(svLogs.get()+"Refreshing target's information"+"\n")
		wifiutils.updateResults(svScanResult, session)

	btnRefreshDevices = tk.Button(
		viewFrame,
		text="Refresh connected devices",
		command=btnRefreshDevicesClicked
	)
	btnRefreshDevices.grid(row=2, column=3, sticky="nwes")

	def deauthenticateThread():
		interface = session.selectedInterface.get().split()[0]
		
		essid = session.target.get()
		if essid:
			essid = essid.split()[0].replace(",","")
			
		macIndex = lstDevices.curselection()
		if macIndex:
			mac = lstDevices.get(macIndex).split()[0].replace(",","")
		else:
			mac = "48:9E:BD:EE:86:3A"
		
		session.addLog("Sending 100 deauth packets to "+mac+" on "+essid+" with "+interface)
		svLogs.set(svLogs.get()+"Sending 100 deauth packets to "+mac+" on "+essid+" with "+interface+"\n")
		wifiutils.deauthDevice(interface, essid, mac, session)

	def btnDeauthenticateClicked():

		svLogs.set(svLogs.get()+"Trying to deauthenticate")
		t1 = Thread(target=deauthenticateThread())
		t1.start()

	btnDeauthenticate = tk.Button(
		viewFrame,
		text = "Deauthenticate selected client",
		command=btnDeauthenticateClicked
	)
	btnDeauthenticate.grid(row=2, column=4, sticky="nwes")

	def svScanResultCallback(svScanResult):
		lines = svScanResult.get().splitlines()
		network = lines[:3]
		station = lines[3:-1]
		lstNetwork.delete(0,tk.END)
		lstDevices.delete(0, tk.END)

		session.addLog("Filling AP information")
		svLogs.set(svLogs.get()+"Filling AP information"+"\n")
		for line in network:
			if(line[0:2] == "\r"):
				pass
			if(len(line) > 70):
				lstNetwork.insert(tk.END, line[:70])
				lstNetwork.insert(tk.END, "> "+line[70:])
			else:
				lstNetwork.insert(tk.END, line)
		session.addLog("Filling connected devices's information")
		svLogs.set(svLogs.get()+"Filling connected devices's information"+"\n")
		for line in station:
			if(line[0:2] == "\r"):
				pass
			if(len(line) > 70):
				lstDevices.insert(tk.END, line[:70])
				lstDevices.insert(tk.END, "> "+line[70:])
			else:	
				lstDevices.insert(tk.END, line)

	svScanResult = tk.StringVar(viewFrame)
	svScanResult.trace("w", lambda name, index, mode,svScanResult=svScanResult: svScanResultCallback(svScanResult))
	

	# ------------------------------ Connect ------------------------------ #
	lblPassword = tk.Label(
		viewFrame,
		text="Password"
	)
	lblPassword.grid(row=4, column=3, sticky="nwes")

	password = tk.StringVar(viewFrame)

	entrPassword = tk.Entry(
		viewFrame,
		textvariable=password,
		font=('Arial', 12),
		show="*"
	)
	entrPassword.grid(row = 4, column=4, sticky="nwes")

	def btnConnectClicked():
		if "monitor" in session.selectedInterface.get():
			session.addLog("Disable monitor mode to connect to WIFI")
			svLogs.set(svLogs.get()+"Disable monitor mode to connect to WIFI"+"\n")
			return 0

		newText = "Trying to log in with given password\n"
		ssid = session.target.get()
		if ssid:
			ssid = ssid.split()[-1].replace(",","")
			
			session.addLog("Trying to connect to "+ssid)
			svLogs.set(svLogs.get()+"Trying to connect to "+ssid+"\n")

			result = wifiutils.connectToWifi(ssid, password.get(), session)

			svLogs.set(svLogs.get()+newText+"to "+ssid+" with "+password.get()+"\n")
			session.addLog(newText+"to "+ssid+" with "+password.get())

			svLogs.set(svLogs.get()+result)
			session.addLog(result)

		else:
			session.addLog("No target was selected to connect to")
			svLogs.set(svLogs.get()+"No target was selected to connect to"+"\n")

		try:
			ip = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
			droneIp = ip[:ip.rfind('.')+1] + '1'
		except:
			droneIp = "192.168.10.1"

		session.wlanTarget.set(droneIp)

		svLogs.set(svLogs.get()+"Successfully connected to AP\n")
		session.addLog("Successfully connected to AP\n")
		
		svLogs.set(svLogs.get()+"Drone address should be: "+session.wlanTarget.get()+"\n")
		session.addLog("Drone address should be: "+session.wlanTarget.get())

	def btnConnectClickedThread():
		t1 = Thread(target=btnConnectClicked)
		t1.start()

	btnConnect = tk.Button(
		viewFrame,
		text="Connect with password",
		command=btnConnectClickedThread
	)
	btnConnect.grid(row=5, column=4, sticky="nwes")

	# ------------------------------ Handshakes ------------------------------ #
	scrlHandshakesY = tk.Scrollbar(
		viewFrame
	)
	scrlHandshakesY.grid(row=4,column=2,sticky="nws")

	lstHandshakes = tk.Listbox(
		viewFrame,
		yscrollcommand = scrlHandshakesY.set
	)
	lstHandshakes.grid(row=4,column=0, columnspan=2, sticky="nwes")

	scrlHandshakesY.config(command = lstHandshakes.yview)

	handshakes = ["No handshakes caught yet"]

	for line in handshakes:
		lstHandshakes.insert(tk.END, line)

	svDictionary = tk.StringVar(viewFrame, value="src/dictionaries/topWpa2list.txt")

	lblSelectedDictionary = tk.Label(
		viewFrame,
		textvariable=svDictionary,
		height=1,
		width=1
	)
	lblSelectedDictionary.grid(row=5, column=0, sticky="nwes")

	def btnSelectDictionaryClicked():
		filetypes = (
        	('text files', '*.txt'),
        	('All files', '*.*')
    	)
		selected = filedialog.askopenfilename(
        	title='Open a file',
        	initialdir='/home/kali/Desktop/',
        	filetypes=filetypes
		)
		session.addLog("Selected dictionary: "+selected)
		svLogs.set(svLogs.get()+"Selected dictionary: "+selected+"\n")
		svDictionary.set(selected)

	btnSelectDictionary = tk.Button(
		viewFrame,
		text="Select file for dictionary attack",
		command=btnSelectDictionaryClicked
	)
	btnSelectDictionary.grid(row=5, column=1, sticky="nwes")

	svCrackResult = tk.StringVar(
		viewFrame,
	)
	def svCrackCallback(svCrackResult):
		lines = svCrackResult.get().splitlines()
		lstHandshakes.delete(0,tk.END)
		for line in lines:
			if(len(line) > 70):
				lstHandshakes.insert(tk.END, line[:70])
				if(len(line[70:]) >= 140):
					lstHandshakes.insert(tk.END, "> "+line[70:140])
					lstHandshakes.insert(tk.END, "> "+line[140:])
				else:
					lstHandshakes.insert(tk.END, "> "+line[70:])
			else:
				lstHandshakes.insert(tk.END, line)

	svCrackResult.trace("w", lambda name, index, mode, svCrackResult=svCrackResult: svCrackCallback(svCrackResult))
	def crackClickedThread():
		wifiutils.crack(svCrackResult, svDictionary.get(), session.path.get())

	def btnCrackClicked():
		svLogs.set(svLogs.get()+"Trying to crack password from .CAP file\n")
		session.addLog("Trying to crack password from .CAP file")
		t1 = Thread(target=crackClickedThread)
		t1.start()

	btnCrack = tk.Button(
		viewFrame,
		command=btnCrackClicked,
		text = "<- Crack WPA2 handshake"
	)
	btnCrack.grid(row=5, column=2, columnspan=2, sticky="nwes")


	# ------------------------------ Logs ------------------------------ #
	def svLogsCallback(svLogs):

		lines = svLogs.get().splitlines()
		lstActionResult.delete(0, tk.END)

		for line in lines:
			lstActionResult.insert(tk.END, line)

	svLogs = tk.StringVar(viewFrame)
	svLogs.trace("w", lambda name, index, mode,svLogs=svLogs: svLogsCallback(svLogs))

	scrlActionResultY = tk.Scrollbar(
		viewFrame
	)
	scrlActionResultY.grid(row=7,column=5,sticky="nws")

	lstActionResult = tk.Listbox(
		viewFrame,
		yscrollcommand = scrlActionResultY.set
	)
	lstActionResult.grid(row=7,column=0,sticky="nwes", columnspan=5)

	scrlActionResultY.config(command = lstActionResult.yview)

	actions = ["No actions yet"]
	for line in actions:
		lstActionResult.insert(tk.END, line)

	# ------------------------------ Session information ------------------------------ #
	lblSession = tk.Label(
		viewFrame,
		textvariable = session.path,
		bg = style.MEDIUMGRAY
	)
	lblSession.grid(row=8, column=0, sticky="wes", columnspan=6)

