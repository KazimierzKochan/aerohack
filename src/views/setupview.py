import asyncio
from threading import Thread
import tkinter as tk
from tkinter import Entry, Button
from tkinter import ttk
from views import startview
from utils import setuputils
from graphics import style


def prepareView(tab, session):
	# ------------------------------ Configuration ------------------------------ #
	tab.grid_propagate(False)

	viewFrame = tk.Frame(tab, bg=style.LIGHTMEDIUMGRAY, bd=0)
	viewFrame.pack(expand=True, fill="both")

	viewFrame.columnconfigure(0, weight=2)
	viewFrame.columnconfigure(1, weight=2)
	viewFrame.columnconfigure(2, weight=2)
	viewFrame.rowconfigure(8, weight=1)


	# ------------------------------ Title ------------------------------ #
	lblSetpuTitle = tk.Label(
		viewFrame,
		text = "Setup interface, select target",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblSetpuTitle.grid(column=0, row=0, columnspan=2, sticky="nw")


	# ------------------------------ Wireless interface selection ------------------------------ #
	lblNetworkCardSelectionTitle = tk.Label(
		viewFrame,
		text = "Select wireless interface to use",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblNetworkCardSelectionTitle.grid(column=0, row=1, columnspan=2, sticky="nw")

	global lstNetworkInterfaces
	lstNetworkInterfaces = list()
	interfaces = setuputils.listWirelessInterfaces()
	session.addLog("Searching for available wireless interfaces")
	
	if not (interfaces):
		lstNetworkInterfaces.append("No available wireless interfaces")
		session.addLog("No available wireless interfaces")
	else:
		for i in interfaces:
			lstNetworkInterfaces.append(i)
		session.addLog("Selected default wireless interface: "+interfaces[0])
		session.selectedInterface.set(interfaces[0])

	optNetworkCardSelection = ttk.Combobox(
		viewFrame,
		values=lstNetworkInterfaces,
		state="readonly",
		width=1
    )
	optNetworkCardSelection.set("Choose a wireless interface")
	optNetworkCardSelection.current(0)
	optNetworkCardSelection.grid(column=0, row=2, columnspan=2, sticky="nwes")



	def btnRefreshInterfacesClicked():
		session.addLog("Refreshing wireless interfaces' list")
		interfaces = setuputils.listWirelessInterfaces()
		lstNetworkInterfaces.clear()

		if not (interfaces):
			lstNetworkInterfaces.append("No available wireless interfaces")
			session.addLog("No available wireless interfaces")
		else:
			for i in interfaces:
				lstNetworkInterfaces.append(i)
			session.addLog("Wireless interfaces list refreshed")

		optNetworkCardSelection['values'] = lstNetworkInterfaces

	btnRefreshInterfaces = tk.Button(
		viewFrame,
		text = "Refresh interfaces list",
		command = btnRefreshInterfacesClicked
	)
	btnRefreshInterfaces.grid(column=2, row=2, sticky="nwes")

	def setFromComboBox(event):
		selectedInterface = event.widget.get()
		session.addLog("Selected wireless interface: "+selectedInterface)
		session.selectedInterface.set(selectedInterface)
	
	optNetworkCardSelection.bind("<<ComboboxSelected>>", setFromComboBox)

	# ------ check if card can be set into monitro mode ------
	lblNetworkCardCheckTitle = tk.Label(
		viewFrame,
		text = "Check if chosen network adapter can be set into monitor mode",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblNetworkCardCheckTitle.grid(column=0, row=3, columnspan=2, sticky="nw")

	lblNetworkCardCheckResult = tk.Label(
		viewFrame,
		text = "Not tested yet",
		width=1,
		bg=style.LIGHTGRAY
	)
	lblNetworkCardCheckResult.grid(column=1, row=4, sticky="nwes", columnspan=1, rowspan=1)

	def btnNetworkCardCheckedClicked():
		session.addLog("Checking if wireless interface "+session.selectedInterface.get()+" can be set into monitor mode")

		if "monitor" in session.selectedInterface.get():
			newText = "Interface "+session.selectedInterface.get().split()[0]+" is already in monitor mode"
		else:
			if session.selectedInterface.get().split():
				newText = setuputils.checkMonitorMode(session.selectedInterface.get().split()[0])
			else:
				newText = "No interface selected"
		session.addLog("Result: "+newText)

		lblNetworkCardCheckResult.configure(text=newText)

	btnNetworkCardChecked = Button(
		viewFrame,
		text="Check network adapter",
		command= btnNetworkCardCheckedClicked)
	btnNetworkCardChecked.grid(column=0, row=4, sticky="nwes")


	lblAdapterMode = tk.Label(
		viewFrame,
		text = "Monitor mode not set",
		bg = style.LIGHTGRAY
	)
	lblAdapterMode.grid(column=0, row=6, sticky="nes", columnspan=2)


	def btnSetMonitorModeThread():
		if "monitor" in session.selectedInterface.get():
			newText = "Selected interface already is in monitor mode"
		else:
			if session.selectedInterface.get().split():
				r = setuputils.setIntoMonitorMode(session.selectedInterface.get().split()[0])
				session.originalInterface.set(session.selectedInterface.get())

				btnRefreshInterfacesClicked()
				newInterface = session.selectedInterface.get().split()[0]
				newText = "Selected newly created interface with monitor mode set: "+newInterface
				session.selectedInterface.set(newInterface)
			else:
				newText = "No interface selected"
		lblAdapterMode.configure(text=newText)
		session.addLog(newText)
		
	def btnSetMonitorModeClicked():
		t1 = Thread(target=btnSetMonitorModeThread)
		t1.start()

	btnSetMonitorMode = tk.Button(
		viewFrame,
		text = "Set monitor mode on selected adapter",
		command=btnSetMonitorModeClicked,
		width=1
	)
	btnSetMonitorMode.grid(column=0, row=5, sticky="nwes", columnspan=1, rowspan=1)

	def btnResetModeThread():
		session.addLog("Reseting monitor mode on "+session.selectedInterface.get().split()[0])
		if session.selectedInterface.get().split():
			if(session.selectedInterface.get().split()[0].endswith("mon")):
				r = setuputils.resetMode(session.selectedInterface.get().split()[0])
				newText = "Reverted back to managed wlan0"
			else:
				newText = "Interface was not in monitor mode"
		else:
			newText = "No interface"
		session.addLog(newText)
		lblAdapterMode.configure(text=newText)

	def btnResetModeClicked():
		t1 = Thread(target=btnResetModeThread)
		t1.start()

	btnResetMode = tk.Button(
		viewFrame,
		text="Reset mode on selected adapter",
		command=btnResetModeClicked,
		width=1
	)
	btnResetMode.grid(column=1, row=5, sticky="nwes")

	lblSetTarget = tk.Label(
		viewFrame,
		text = "Select target",
		width=2
	)
	lblSetTarget.grid(column=0, row=7, columnspan=1, sticky="nwes")

	def StartTargetsScan():
		if session.selectedInterface.get().split():
			pRet = asyncio.run(setuputils.scanForTargets(session.selectedInterface.get().split()[0], session.path.get()))

	def btnStartTargetsScanClicked():
		if not "monitor" in session.selectedInterface.get():
			session.addLog("You need an interface in monitor mode to perform such action")
		else:
			session.addLog("Start scanning for targets")
			t1 = Thread(target=StartTargetsScan)
			t1.start()
	
	btnStartTargetsScan = tk.Button(
		viewFrame,
		text = "Start scanning for targets",
		command=btnStartTargetsScanClicked
	)
	btnStartTargetsScan.grid(row = 7, column=0, sticky="nwes")


	def btnStopTargetScanClicked():
		session.addLog("Trying to stop scan for targets")
		stopped = setuputils.checkKillScan(session.path.get())
		if stopped == -1:
			session.addLog("Scan for targets was not running")
		else:
			session.addLog("Scan for targets was stopped")

	btnStopTargetScan = tk.Button(
		viewFrame,
		text="Stop scanning for targets",
		command=btnStopTargetScanClicked
	)
	btnStopTargetScan.grid(row = 7, column=1, sticky="nwes")


	def btnRefreshTargetsClicked():
		session.addLog("Refreshing targets")
		setuputils.updateResults(svScanResult, session)
		pass

	btnRefreshTargets = tk.Button(
		viewFrame,
		text="Refresh targets list",
		command=btnRefreshTargetsClicked,
		bg = style.DARKMEDIUMGRAY
	)
	btnRefreshTargets.grid(row = 7, column=2, sticky="nwes")


	scrlScanResultY = tk.Scrollbar(
		viewFrame
	)
	scrlScanResultY.grid(row=8,column=3,sticky="nws")

	def svScanResultCallback(svScanResult):
		lines = svScanResult.get().splitlines()
		lstScanResult.delete(0,tk.END)
		for line in lines:
			lstScanResult.insert(tk.END, line)

	svScanResult = tk.StringVar(viewFrame)
	svScanResult.trace("w", lambda name, index, mode,svScanResult=svScanResult: svScanResultCallback(svScanResult))

	lstScanResult = tk.Listbox(
		viewFrame,
		yscrollcommand = scrlScanResultY.set
	)
	lstScanResult.grid(row=8,column=0,sticky="nwes", columnspan=3)

	scrlScanResultY.config(command = lstScanResult.yview)

	lblSelectedTarget = tk.Label(
		viewFrame,
		text = "No target yet selected",
		wraplength=650,
		height=1,
		width=1
	)
	lblSelectedTarget.grid(row = 9, column=1, columnspan=2, rowspan=2, sticky="nwes")

	def btnSelectTargetClicked():
		selectedTarget = lstScanResult.curselection()
		if not selectedTarget:
			lblSelectedTarget.configure(text="Select target")
		else:
			selected = lstScanResult.get(selectedTarget)
			session.target.set(selected)
			selected.replace("\t", " ")
			session.addLog("Selected target: "+selected)
			lblSelectedTarget.configure(text="Target: "+selected)

	btnSelectTarget = tk.Button(
		viewFrame,
		text = "Select target",
		command=btnSelectTargetClicked
	)
	btnSelectTarget.grid(row=9, column=0, sticky="nwes")


	# ------------------------------ Session information ------------------------------ #
	lblSession = tk.Label(
		viewFrame,
		textvariable = session.path,
		bg = style.MEDIUMGRAY
	)
	lblSession.grid(column=0, row=11, sticky="wes", columnspan=3)





