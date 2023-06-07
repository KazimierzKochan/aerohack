from threading import Thread
import tkinter as tk
from attacks import spoofing
from utils import spoofingutils
from graphics import style

def prepareView(tab, session):
	# ------------------------------ Setup ------------------------------ #
	tab.grid_propagate(False)
	viewFrame = tk.Frame(tab, bg=style.LIGHTMEDIUMGRAY, bd=0)
	viewFrame.pack(expand=True, fill="both")

	viewFrame.columnconfigure(0, weight=1)
	viewFrame.columnconfigure(1, weight=1)
	viewFrame.columnconfigure(2, weight=1)

	viewFrame.rowconfigure(8, weight=1)

	
	# ------------------------------ Title ------------------------------ #
	lblSpoogfingTitle = tk.Label(
		viewFrame,
		text="Spoofing",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblSpoogfingTitle.grid(row=0, column=0, sticky="nw")


	# ------------------------------ Spoofing settings ------------------------------ #
	lblDrone = tk.Label(
		viewFrame,
		text="Drone"
	)
	lblDrone.grid(row = 1, column=0, sticky="nwes")

	lblControler = tk.Label(
		viewFrame,
		text="Controler"
	)
	lblControler.grid(row = 2, column=0, sticky="nwes")

	#defaul tello ip pair
	drone = tk.StringVar(viewFrame, value="192.168.10.1")
	controler = tk.StringVar(viewFrame, value="192.168.10.2")

	entrDrone = tk.Entry(
		viewFrame,
		textvariable=drone
	)
	entrDrone.grid(row = 1, column=1, sticky="nwes")

	entrControler = tk.Entry(
		viewFrame,
		textvariable=controler
	)
	entrControler.grid(row = 2, column=1, sticky="nwes")


	# ------------------------------ Packet forwarding ------------------------------ #
	lblForwardingTitle = tk.Label(
		viewFrame,
		text="Packet forwarding",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblForwardingTitle.grid(row=3, column=0, sticky="nsw", columnspan=2)

	global svForwarding
	svForwarding = tk.StringVar(viewFrame, value="Packet forwarding OFF")

	lblForwardingStatus = tk.Label(
		viewFrame,
		textvariable=svForwarding,
		width=1
	)
	lblForwardingStatus.grid(row=4, column=0, sticky="nwes")

	def enableForwardingThread():
		if svForwarding.get() == "Packet forwarding OFF":
			session.addLog("Enabling packet forwarding")
			svLogs.set(svLogs.get()+"Enabling packet forwarding\n")
			spoofing.enableForwarding()
			svForwarding.set("Packet forwarding ON")
		else:
			session.addLog("Packet forwarding is already enabled")
			svLogs.set(svLogs.get()+"Packet forwarding is already enabled\n")
	
	def disableForwardingThread():
		if svForwarding.get() == "Packet forwarding ON":
			session.addLog("Disabling packet forwarding")
			svLogs.set(svLogs.get()+"Disabling packet forwarding\n")
			spoofing.disableForwarding()
			svForwarding.set("Packet forwarding OFF")
		else:
			session.addLog("Packet forwarding is already disabled")
			svLogs.set(svLogs.get()+"Packet forwarding is already disabled\n")


	def btnForwardingClicked():
		if btnForwarding["text"] == "Enable packet forwarding":
			t1 = Thread(target=enableForwardingThread)
			btnForwarding["text"] = "Disable packet forwarding"

		elif btnForwarding["text"] == "Disable packet forwarding":
			t1 = Thread(target=disableForwardingThread)
			btnForwarding["text"] = "Enable packet forwarding"

		t1.start()

	btnForwarding = tk.Button(
		viewFrame,
		text="Enable packet forwarding",
		command=btnForwardingClicked
	)
	btnForwarding.grid(row=4, column=1, sticky="nwes")


	frwd = spoofing.checkForwarding()
	if("0" in frwd):
		svForwarding.set("Packet forwarding OFF")
		btnForwarding["text"] = "Enable packet forwarding"
	elif("1" in frwd):
		btnForwarding["text"] = "Disable packet forwarding"
		svForwarding.set("Packet forwarding ON")


	# ------------------------------ Spoofing status ------------------------------ #
	lblSpoofingStatusTitle = tk.Label(
		viewFrame,
		text="ARP Spoofing status",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblSpoofingStatusTitle.grid(row=5, column=0, sticky="nw")

	svSpoofingStatus = tk.StringVar(viewFrame, value="ARP Spoofing is OFF")

	def sessionSpoofingCallback(isSpoofing):
		svSpoofingStatus.set("ARP Spoofing is "+isSpoofing.get())
	session.isSpoofing.trace("w", lambda name, index, mode, isSpoofing=session.isSpoofing: sessionSpoofingCallback(isSpoofing))

	lblSpoofingStatus = tk.Label(
		viewFrame,
		textvariable=svSpoofingStatus
	)
	lblSpoofingStatus.grid(row=6, column=0, sticky="nswe")


	# ------------------------------ Run ARP cache poisoning ------------------------------ #
	global svSpoofingButton
	svSpoofingButton = tk.StringVar(viewFrame, value="Run ARP cache poisoning")

	def arpSpoofingThread():
		if session.isSpoofing.get() == "OFF":
			svSpoofingButton.set("Stop ARP cache poisoning")
			spoofing.startSpoofing(drone.get(), controler.get(), session)
			svLogs.set(svLogs.get()+"Enabling ARP cache poisoning between "+drone.get()+" and "+controler.get()+"\n")
			session.addLog("Enabling ARP cache poisoning between "+drone.get()+" and "+controler.get())
			session.isSpoofing.set("ON")
		else:
			svSpoofingButton.set("Run ARP cache poisoning")
			spoofing.stopSpoofing()
			svLogs.set(svLogs.get()+"Disabling ARP cache poisoning\n")
			session.addLog("Disabling ARP cache poisoning")
			session.isSpoofing.set("OFF")

	def btnArpSpoofingClicked():
		t1 = Thread(target=arpSpoofingThread)
		t1.start()

	btnEnableForwarding = tk.Button(
		viewFrame,
		textvariable=svSpoofingButton,
		command=btnArpSpoofingClicked
	)
	btnEnableForwarding.grid(row=6, column=1, sticky="nwes")


	# ------------------------------ Get ARP table ------------------------------ #
	def arpTableThread():
		result = spoofingutils.checkArpTable()
		svLogs.set(svLogs.get()+result)
		session.addLog("Arp table: "+result)

	def btnArpTableClicked():
		svLogs.set(svLogs.get()+"Getting ARP table:\n")
		session.addLog("Getting ARP table")
		t1 = Thread(target=arpTableThread)
		t1.start()	

	btnArpTable = tk.Button(
		viewFrame,
		text="Get current ARP table",
		command=btnArpTableClicked
	)
	btnArpTable.grid(row = 6, column=2, sticky="nwes")


	# ------------------------------ Last actions ------------------------------ #
	lblLogsTitle = tk.Label(
		viewFrame,
		text="Logs and results",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblLogsTitle.grid(row=7, column=0, sticky="nwes")

	scrlLogsY = tk.Scrollbar(
		viewFrame
	)
	scrlLogsY.grid(row=8,column=3,sticky="nws", rowspan=2)

	def svLogsCallback(svLogs):
		lines = svLogs.get().splitlines()
		lstLogs.delete(0,tk.END)
		for line in lines:
			lstLogs.insert(tk.END, line)

	svLogs = tk.StringVar(viewFrame)
	svLogs.trace("w", lambda name, index, mode, svLogs=svLogs: svLogsCallback(svLogs))

	lstLogs = tk.Listbox(
		viewFrame,
		yscrollcommand = scrlLogsY.set
	)
	lstLogs.grid(row=8,column=0,sticky="nwes", columnspan=3, rowspan=2)

	scrlLogsY.config(command = lstLogs.yview)


	# ------------------------------ Session information ------------------------------ #
	lblSession = tk.Label(
		viewFrame,
		textvariable = session.path,
		bg = style.MEDIUMGRAY
	)
	lblSession.grid(column=0, row=10, sticky="wes", columnspan=4)