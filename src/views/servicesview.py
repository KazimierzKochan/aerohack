from threading import Thread
import tkinter as tk
from utils import ftputils, telnetutils
from tkinter import filedialog
from graphics import style

def prepareView(tab, session):
	# ------------------------------ Configuration ------------------------------ #
	tab.grid_propagate(False)
	viewFrame = tk.Frame(tab, bg=style.LIGHTMEDIUMGRAY, bd=0)
	viewFrame.pack(expand=True, fill="both")

	viewFrame.columnconfigure(0, weight=1)
	viewFrame.columnconfigure(1, weight=1)
	viewFrame.columnconfigure(2, weight=1)

	viewFrame.rowconfigure(5, weight=2)

	# ------------------------------ Titles ------------------------------ #
	lblFtpTitle = tk.Label(
		viewFrame,
		text="File Transfer Protocol",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblFtpTitle.grid(row = 0, column = 0, columnspan=4, sticky="nws")

	lblTelnetTitle = tk.Label(
		viewFrame,
		text="Telnet",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblTelnetTitle.grid(row = 7, column = 0, columnspan=4, sticky="nws")


	# ------------------------------ FTP Connection configuration ------------------------------ #
	lblUsername = tk.Label(
		viewFrame,
		text = "Username",
	)
	lblUsername.grid(row = 1, column=0)

	username = tk.StringVar(viewFrame, value="")
	
	entrUsername = tk.Entry(
		viewFrame,
		textvariable=username
	)
	entrUsername.grid(row = 1, column = 1, sticky="nw")

	lblPasssword = tk.Label(
		viewFrame,
		text = "Password",
	)
	lblPasssword.grid(row = 2, column=0)

	password = tk.StringVar(viewFrame, value="")

	entrPassword = tk.Entry(
		viewFrame,
		textvariable=password,
		show="*"
	)
	entrPassword.grid(row = 2, column = 1, sticky="nw")

	lblPort = tk.Label(
		viewFrame,
		text="Port"
	)
	lblPort.grid(row = 3, column = 0)

	port = tk.IntVar(viewFrame, value=21)
	
	entrPort = tk.Entry(
		viewFrame,
		textvariable=port
	)
	entrPort.grid(row = 3, column=1, sticky="nw")

	svHost = tk.StringVar(viewFrame, value="192.168.1.1") #default parrot ip
	lblHost = tk.Label(
		viewFrame,
		text="Host"
	)
	lblHost.grid(row = 4, column = 0)

	entrHost = tk.Entry(
		viewFrame,
		textvariable=svHost
	)
	entrHost.grid(row = 4, column=1, sticky="nw")

	def updateFilesTree():
		ftpResults = ftputils.lsFtp()
		lstFtpDir.delete(0,tk.END)
		for line in ftpResults:
			lstFtpDir.insert(tk.END, line)

	def btnConnectClicked():
		session.addLog("Connecting to FTP service: "+svHost.get()+":"+str(port.get())+" with "+username.get()+":"+password.get())
		ftputils.connectToFtp(svHost.get(), username.get(), password.get(), port.get())
		ftpResult = ftputils.getFtpServerVersion()
		lblConnectionInfo.configure(text=ftpResult)
		updateFilesTree()

	btnConnect = tk.Button(
		viewFrame,
		text = "Connect",
		command=btnConnectClicked
	)
	btnConnect.grid(row = 1, column=2, rowspan=3, sticky="news")

	lblConnectionInfo = tk.Label(
		viewFrame,
		text="Not connected yet"
	)
	lblConnectionInfo.grid(row = 4, column=0, columnspan=1, sticky="wn")


	# ------------------------------ FTP  ------------------------------ #
	scrlFtpDirY = tk.Scrollbar(
		viewFrame
	)
	scrlFtpDirY.grid(row=5,column=3,sticky="nws")

	lstFtpDir = tk.Listbox(
		viewFrame,
		yscrollcommand = scrlFtpDirY.set
	)
	lstFtpDir.grid(row=5,column=0,sticky="nwes", columnspan=3)

	scrlFtpDirY.config(command = lstFtpDir.yview)

	def btnOpenFolderClicked():
		selectedFileIndex = lstFtpDir.curselection()
		if not selectedFileIndex:
			svLogs.set(svLogs.get()+"Select folder to open..\n")
		else:
			selectedFile = lstFtpDir.get(selectedFileIndex)
			selectedFile.split(None, 8)
			name = selectedFile.split(None, 8)[-1]
			if(selectedFile[0][0] == "d"):
				newText = "Trying to open: " + name
				ftputils.cwd(name)
				updateFilesTree()
			else:
				newText = "Select a folder to open"
			svLogs.set(svLogs.get()+newText+"\n")
			session.addLog(newText)

	btnOpenFolder = tk.Button(
		viewFrame,
		text="Open folder",
		command=btnOpenFolderClicked
	)
	btnOpenFolder.grid(row = 6, column=0, sticky="nwes")

	def btnStepBackClicked():
		ftputils.cwd("..")
		updateFilesTree()
		session.addLog("FTP: went one step back")
		svLogs.set(svLogs.get()+"Went one step back\n")

	btnStepBack = tk.Button(
		viewFrame,
		text="Step back",
		command=btnStepBackClicked
	)
	btnStepBack.grid(row = 6, column=1, sticky="nwes")

	def btnDownloadFileClicked():
		selectedFileIndex = lstFtpDir.curselection()
		if not selectedFileIndex:
			svLogs.set(svLogs.get()+"Select file to download")
		else:
			selectedFile = lstFtpDir.get(selectedFileIndex)
			svLogs.set(svLogs.get()+"Trying to download: "+selectedFile+"\n")
			session.addLog("Trying to download: "+selectedFile)
			result = ftputils.downloadTextFile(selectedFile.split()[-1], session.path.get()+"/")
			svLogs.set(svLogs.get()+result+"\n")

	btnDownloadFile = tk.Button(
		viewFrame,
		text="Download File",
		command=btnDownloadFileClicked
	)
	btnDownloadFile.grid(row = 6, column=2, sticky="nwes")


	# ------------------------------ Telnet ------------------------------ #

	ivTelnetPort = tk.IntVar(viewFrame, value=23)

	lblPort = tk.Label(
		viewFrame,
		text="Port"
	)
	lblPort.grid(row=8, column=0)

	entrTelnetPort = tk.Entry(
		viewFrame,
		textvariable=ivTelnetPort
	)
	entrTelnetPort.grid(row = 8, column=1, sticky="nw")

	def OpenTelnetThread():
		#TODO session wlan target
		where = session.wlanTarget.get()
		svLogs.set(svLogs.get()+"Connection info: "+where+" at "+str(ivTelnetPort.get())+"\n")
		session.addLog("Connection info: "+where+" at "+str(ivTelnetPort.get()))
		path = telnetutils.connectTelnet(session, where, ivTelnetPort.get())
		svLogs.set(svLogs.get()+"Creted executable file with connection information:\n"+path+"\n")

	def btnOpenTelnetClicked():
		t1 = Thread(target=OpenTelnetThread)
		t1.start()

	btnOpenTelnet = tk.Button(
		viewFrame,
		text="Start telnet",
		command=btnOpenTelnetClicked
	)
	btnOpenTelnet.grid(row=8, column=2, sticky="nwes")


	# ------------------------------ Logs ------------------------------ #
	lblLogs = tk.Label(
		viewFrame,
		text="Last actions",
		bg=style.LIGHTMEDIUMGRAY
	)
	lblLogs.grid(row=9, column=0, sticky="nws")

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
	scrlActionResultY.grid(row=10,column=3,sticky="nws")

	lstActionResult = tk.Listbox(
		viewFrame,
		yscrollcommand = scrlActionResultY.set
	)
	lstActionResult.grid(row=10,column=0,sticky="nwes", columnspan=3)

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
	lblSession.grid(column=0, row=11, sticky="wes", columnspan=5)
