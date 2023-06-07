import tkinter as tk
from tkinter import ttk
from utils import scanutils
import asyncio
import json
from threading import *
import datetime
import re
from graphics import style


def prepareView(tab, session):
	# ------------------------------ Configuration ------------------------------ #
	tab.grid_propagate(False)
	viewFrame = tk.Frame(tab, bg=style.LIGHTMEDIUMGRAY, bd=0)
	viewFrame.pack(expand=True, fill="both")

	viewFrame.columnconfigure(1, weight=1)

	viewFrame.rowconfigure(5, weight=1)


	# ------------------------------ Title ------------------------------ #
	lblScanTitle = tk.Label(
		viewFrame,
		text = "Scan target",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblScanTitle.grid(column=0, row=0, columnspan=2, sticky="nws")


	# ------------------------------ Suggested scan ------------------------------ #
	lblScans = tk.Label(
		viewFrame,
		text = "Chose one of suggested scans or use your own",
	)
	lblScans.grid(row=1, column=0, columnspan=2, sticky="nw")



	lstCommonScans = scanutils.getSugestedScans()

	cmbCommonScan = ttk.Combobox(
		viewFrame,
		values=lstCommonScans,
		state="readonly"
    )
	cmbCommonScan.set("Choose a common scan")
	cmbCommonScan.current(0)
	cmbCommonScan.grid(row=3, column=1, sticky="nwes", columnspan=1)



# ------------------------------ Custom scan ------------------------------ #
	entrOwnScan = ttk.Entry(
		viewFrame,
	)
	entrOwnScan.insert(0, "Enter own nmap scan")
	entrOwnScan.grid(row=4, column=1 ,sticky="nwes")



	# ------------------------------ Scan selection ------------------------------ #
	scanOption = tk.StringVar(viewFrame, value="common")
	
	rbtnCommonScan = tk.Radiobutton(
		viewFrame,
		value="common",
		var=scanOption
	)
	rbtnCommonScan.grid(row = 3, column=0, sticky="ne")

	rbtnCustomScan = tk.Radiobutton(
		viewFrame,
		value="custom",
		var=scanOption
	)
	rbtnCustomScan.grid(row = 4, column=0, sticky="ne")

	scanOption.set("l")


	# ------------------------------ Scan execution ------------------------------ #
	def startScanThread():
		selected = scanOption.get()
		#get ip
		ip = session.wlanTarget.get()

		if not bool(re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",ip)):
			#if does not end in ip scan default tello IP
			ip = "192.168.10.1"

		if selected == "common":
			#execute common
			scan = lstCommonScans[cmbCommonScan.current()]
			scan = scan+ip

			session.addLog("Executing common scan: "+scan)

			returnCode = asyncio.run(scanutils.executeScan(scan, svScanResult, session))

		elif selected == "custom":
			#execute custom
			scan = entrOwnScan.get()
			lastArgument = scan.split(" ")[-1]
			session.addLog("Executing custom scan: "+scan)
			returnCode = asyncio.run(scanutils.executeScan(scan, svScanResult, session))
		else:
			session.addLog("No scan selected")
			returnCode = -1

		session.addLog("Scan return code: "+str(returnCode))

	def btnStartScanClicked():
		t1 = Thread(target=startScanThread)
		t1.start()


	btnStartScan = tk.Button(
		viewFrame,
		text="Start scan!",
		command=btnStartScanClicked,
		bg=style.DARKMEDIUMGRAY
	)
	btnStartScan.grid(row=1, column=2, columnspan=1, rowspan=4, sticky="nwes")



	# ------------------------------ Scan result ------------------------------ #

	scrlScanResultY = tk.Scrollbar(
		viewFrame
	)
	scrlScanResultY.grid(row=5,column=3,sticky="nws")

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
	lstScanResult.grid(row=5,column=0,sticky="nwes", columnspan=3)

	scrlScanResultY.config(command = lstScanResult.yview)


	# ------------------------------ Scan result options ------------------------------ #
	def btnClearScanResultClicked():
		lstScanResult.delete(0,tk.END)

	btnClearScanResult = tk.Button(
		viewFrame,
		text="Clear results",
		command=btnClearScanResultClicked
	)
	btnClearScanResult.grid(row=6, column=0, sticky="nwes")

	def btnSaveResultClicked():
		session.addToFile("\scan.txt", svScanResult.get())
		session.addLog("Saved latest scan's result to scan.txt")

	btnClearSaveResult = tk.Button(
		viewFrame,
		text="Save results",
		command=btnSaveResultClicked
	)
	btnClearSaveResult.grid(row=6, column=1, sticky="nwes")


	# ------------------------------ Session information ------------------------------ #
	lblSession = tk.Label(
		viewFrame,
		textvariable = session.path,
		bg = style.MEDIUMGRAY
	)
	lblSession.grid(column=0, row=10, sticky="wes", columnspan=3)