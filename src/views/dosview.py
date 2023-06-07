import asyncio
from threading import Thread
import tkinter as tk
from graphics import style
from utils import scanutils
from attacks import dos

def prepareView(tab, session):
	# ------------------------------ Configuration ------------------------------ #
	tab.grid_propagate(False)
	viewFrame = tk.Frame(tab, bg=style.LIGHTMEDIUMGRAY, bd=0)
	viewFrame.pack(expand=True, fill="both")

	viewFrame.columnconfigure(0, weight=1)
	viewFrame.columnconfigure(1, weight=1)
	viewFrame.columnconfigure(2, weight=1)

	viewFrame.rowconfigure(8, weight=1)

	svLogs = tk.StringVar(viewFrame)
	

	# ------------------------------ Title ------------------------------ #
	lblDosTitle = tk.Label(
		viewFrame,
		text="Denial of Service",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblDosTitle.grid(row=0, column=0, sticky="nws")


	# ------------------------------ SYN Flood ------------------------------ #
	lblSynFlood = tk.Label(
		viewFrame,
		text="SYN Flood Attack",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblSynFlood.grid(row = 1, column=0, sticky="nws")

	lblSynFloodTarget = tk.Label(
		viewFrame,
		text="Target: "
	)
	lblSynFloodTarget.grid(row=2, column=0, sticky="nwes")

	#set tello ip as default
	target = tk.StringVar(viewFrame, value="192.168.10.1")

	entrSynFloodTarget = tk.Entry(
		viewFrame,
		textvariable=target
	)
	entrSynFloodTarget.grid(row=2, column=1, sticky="nwes")

	lblPacketsNumber = tk.Label(
		viewFrame,
		text="Port"
	)
	lblPacketsNumber.grid(row=3, column=0, sticky="nwes")

	svSynPort= tk.IntVar(viewFrame, value=9999)

	entrsvSynPort = tk.Entry(
		viewFrame,
		textvariable=svSynPort
	)
	entrsvSynPort.grid(row=3, column=1, sticky="nwes")

	def startDosThread():
		session.addLog("Starting SYN Flood attack on "+target.get()+":"+str(svSynPort.get()))
		svLogs.set(svLogs.get()+"Starting SYN Flood attack on "+target.get()+":"+str(svSynPort.get())+"\n")
		dos.synFlood(target.get(), svSynPort.get(), 1500, svLogs)
		
	def btnSynFloodClicked():
		t1 = Thread(target=startDosThread)
		t1.start()

	btnSynFlood = tk.Button(
		viewFrame,
		text="Run TCP Syn Flood attack",
		command=btnSynFloodClicked
	)
	btnSynFlood.grid(row=2, column=2, sticky="wens")


	def stopDosThread():
		session.addLog("Trying to stop SYN Flood attack")
		svLogs.set(svLogs.get()+"Trying to stop SYN Flood attack\n")
		r = dos.checkKillSynFlood()
		if r == 0:
			session.addLog("Stopped SYN Flood attack")
			svLogs.set(svLogs.get()+"Stopped SYN Flood attack\n")
		elif r == -1:
			session.addLog("SYN Flood attack was not on")
			svLogs.set(svLogs.get()+"SYN Flood attack was not on\n")

	def btnStopSynFloodClicked():
		t1 = Thread(target=stopDosThread)
		t1.start()

	btnStopSynFlood = tk.Button(
		viewFrame,
		text="Stop TCP Syn Flood attack",
		command=btnStopSynFloodClicked
	)
	btnStopSynFlood.grid(row=3, column=2, sticky="wens")


	# ------------------------------ DOS Overheating ------------------------------ #
	lblOverheatingDos = tk.Label(
		viewFrame,
		text="DoS by overheating procedure",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblOverheatingDos.grid(row = 4, column=0, sticky="nws")

	lblOverheatingTarget = tk.Label(
		viewFrame,
		text="Target: "
	)
	lblOverheatingTarget.grid(row=5, column=0, sticky="nwes")

	#set tello ip as default
	target2 = tk.StringVar(viewFrame, value="192.168.10.1")

	entrTarget2 = tk.Entry(
		viewFrame,
		textvariable=target2
	)
	entrTarget2.grid(row=5, column=1, sticky="nwes")
	#do

	lblPortsNumber = tk.Label(
		viewFrame,
		text="Number of ports to scan"
	)
	lblPortsNumber.grid(row=6, column=0, sticky="nwes")

	portsNumber = tk.IntVar(viewFrame, value=1000)

	entrPortsNumber= tk.Entry(
		viewFrame,
		textvariable=portsNumber
	)
	entrPortsNumber.grid(row=6, column=1, sticky="nwes")



	def startScanThread():
		scan = "nmap -p 1-"+str(portsNumber.get())+" "+target2.get()
		session.addLog("Starting scan: "+scan)
		svLogs.set(svLogs.get()+"Starting scan: "+scan+"\n")
		 
		returnCode = asyncio.run(scanutils.executeScan(scan, svLogs, session))

		session.addLog("DOS Scan return code: "+str(returnCode))
		svLogs.set(svLogs.get()+"DOS Scan return code: "+str(returnCode)+"\n")

	def btnStartScanClicked():
		svLogs.set(svLogs.get()+"Startig overheating DOS\n")
		session.addLog("Startig overheating DOS")

		t1 = Thread(target=startScanThread)
		t1.start()

	btnOverheatingDos = tk.Button(
		viewFrame,
		text="Run Overheating DoS",
		command=btnStartScanClicked
	)
	btnOverheatingDos.grid(row=5, column=2, sticky="wens")

	def stopScanThread():
		r = scanutils.checkKillSynFlood()
		if r == 0:
			session.addLog("Stopped overheating dos scan")
			svLogs.set(svLogs.get()+"Stopped overheating dos scan\n")
		elif r == -1:
			session.addLog("Overheating dos scan was not on")
			svLogs.set(svLogs.get()+"Overheating dos scan was not on\n")

	def btnStopScanClicked():
		t1 = Thread(target=stopScanThread)
		t1.start()

	btnStopScan = tk.Button(
		viewFrame,
		text="Stop overheating DOS attack",
		command=btnStopScanClicked
	)
	btnStopScan.grid(row=6, column=2, sticky="wens")


	# ------------------------------ Logs ------------------------------ #
	lblActions = tk.Label(
		viewFrame,
		text="Last actions: ",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblActions.grid(row = 7, column=0, sticky="nws")

	def svLogsCallback(svLogs):
		lines = svLogs.get().splitlines()
		lstActionResult.delete(0,tk.END)
		for line in lines:
			lstActionResult.insert(tk.END, line)


	svLogs.trace("w", lambda name, index, mode,svLogs=svLogs: svLogsCallback(svLogs))

	scrlActionResultY = tk.Scrollbar(
		viewFrame
	)
	scrlActionResultY.grid(row=8,column=3,sticky="nws")

	lstActionResult = tk.Listbox(
		viewFrame,
		yscrollcommand = scrlActionResultY.set
	)
	lstActionResult.grid(row=8,column=0,sticky="nwes", columnspan=3)

	actions = ["No actions yet"]
	for line in actions:
		lstActionResult.insert(tk.END, line)
	scrlActionResultY.config(command = lstActionResult.yview)



	# ------------------------------ Session information ------------------------------ #
	lblSession = tk.Label(
		viewFrame,
		textvariable = session.path,
		bg = style.MEDIUMGRAY
	)
	lblSession.grid(column=0, row=9, sticky="wes", columnspan=4)