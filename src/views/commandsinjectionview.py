import tkinter as tk
from tkinter import ttk
from graphics import style
from attacks import commandsinjection
import asyncio
from threading import Thread

def prepareView(tab, session):
	# ------------------------------ Configuration ------------------------------ #
	tab.grid_propagate(False)
	viewFrame = tk.Frame(tab, bg=style.LIGHTMEDIUMGRAY, bd=0)
	viewFrame.pack(expand=True, fill="both")

	viewFrame.rowconfigure(6, weight=2)

	viewFrame.columnconfigure(0, weight=1)
	viewFrame.columnconfigure(1, weight=1)
	viewFrame.columnconfigure(2, weight=1)

	# ------------------------------ Title ------------------------------ #
	lblCommandsInjecionTitle = tk.Label(
		viewFrame,
		text="Commands injection",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblCommandsInjecionTitle.grid(row=0, column=0, sticky="nws")


	# ------------------------------ Setup ------------------------------ #
	lblCommand = tk.Label(
		viewFrame,
		text="Enter your command"
	)
	lblCommand.grid(row = 1, column=0, sticky="nwes")

	svCommand = tk.StringVar(viewFrame, value="Type command")
	entrCommand = tk.Entry(
		viewFrame,
		textvariable=svCommand,
	)
	entrCommand.grid(row = 1, column = 1, columnspan=2, sticky="nwes")


	lblProtocolPort = tk.Label(
		viewFrame,
		text="Protocol;Port"
	)
	lblProtocolPort.grid(row=2, column=0, sticky="nwes")

	lstProtocols = ["UDP"]
	svProtocol = tk.StringVar(viewFrame, value="UDP")
	cmbProtocol = ttk.Combobox(
		viewFrame,
		values=lstProtocols,
		state="readonly",
		width=1,
		textvariable=svProtocol
    )
	cmbProtocol.set("Choose a protocol")
	cmbProtocol.current(0)
	cmbProtocol.grid(column=1, row=2, sticky="nwes")

	svPort = tk.IntVar(
		viewFrame,
		value=8889
	)
	entrPort = tk.Entry(
		viewFrame,
		textvariable=svPort
	)
	entrPort.grid(row=2, column=2, sticky="nwes")


	lblSpoof = tk.Label(
		viewFrame,
		text="Send as: "
	)
	lblSpoof.grid(row=3, column=0, sticky="nwes")

	svSpoof = tk.StringVar(viewFrame, value="192.168.10.2")
	entrSpoof = tk.Entry(
		viewFrame,
		textvariable=svSpoof
	)
	entrSpoof.grid(row=3, column=1, sticky="nwes")


	svSrcPort = tk.IntVar(
		viewFrame,
		value=7152
	)
	entrSrcPort = tk.Entry(
		viewFrame,
		textvariable=svSrcPort
	)
	entrSrcPort.grid(row=3, column=2, sticky="nwes")

	def btnSendCommandThread():
		commandsinjection.sendUdpCommand(svSpoof.get(), svSrcPort.get(), session.wlanTarget.get(), svPort.get(), svCommand.get())
		log = "Sending command: "+svCommand.get()+" to "+session.wlanTarget.get()+":"+str(svPort.get())+" as "+svSpoof.get()+":"+str(svSrcPort.get())
		session.addLog(log)
		svLogs.set(svLogs.get()+log+"\n")

	def btnSendCommandClicked():
		t1 = Thread(target=btnSendCommandThread)
		t1.start()

	btnSendCommand = tk.Button(
		viewFrame,
		text="Send command",
		command=btnSendCommandClicked,
		bg=style.DARKMEDIUMGRAY
	)
	btnSendCommand.grid(row=4, column=0, columnspan=3, sticky="nwes")

	# ------------------------------ Last actions ------------------------------ #
	lblLogsTitle = tk.Label(
		viewFrame,
		text="Logs and results",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblLogsTitle.grid(row=5, column=0, sticky="nws")

	scrlLogsY = tk.Scrollbar(
		viewFrame
	)
	scrlLogsY.grid(row=6,column=3,sticky="nws", rowspan=2)

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
	lstLogs.grid(row=6,column=0,sticky="nwes", columnspan=3, rowspan=1)

	scrlLogsY.config(command = lstLogs.yview)

	# ------------------------------ Session information ------------------------------ #
	lblSession = tk.Label(
		viewFrame,
		textvariable = session.path,
		bg = style.MEDIUMGRAY
	)
	lblSession.grid(column=0, row=7, sticky="wes", columnspan=4)