import tkinter as tk
from tkinter import ttk
from views import *
from utils import project as proj
from utils import setuputils, wifiutils
from attacks import dos, spoofing
import os
from PIL import ImageTk, Image  

global session

def main():
	window = tk.Tk()
	window.title("AeroHack")
	window.geometry("1200x700")
	window.resizable(False, False)

	iconPath = os.getcwd()
	iconPath = iconPath+"/src/graphics/aerohack_icon.png"
	imgIcon = Image.open(iconPath)
	pImgIcon = ImageTk.PhotoImage(imgIcon)
	window.iconphoto(False, pImgIcon)

	
	session = proj.project(window)

	session.addLog("AeroHack started")

	def onExit():
		session.addLog("Killing left scans if they are still active")
		setuputils.checkKillScan(session.path.get())
		wifiutils.checkKillScan(session.path.get())
		
		session.addLog("Killing left SYN Flood attack")
		dos.checkKillSynFlood()

		session.addLog("Killing left spoofing processes")
		spoofing.stopSpoofing()

		session.addLog("Closing Aerohack")

		session.addLog("Saving logs")
		session.saveLogs()
		window.destroy()

	window.protocol("WM_DELETE_WINDOW", onExit)


	tabControl = ttk.Notebook(window)

	tab1 = ttk.Frame(tabControl)
	tab2 = ttk.Frame(tabControl)
	tab3 = ttk.Frame(tabControl)
	tab4 = ttk.Frame(tabControl)
	tab5 = ttk.Frame(tabControl)
	tab6 = ttk.Frame(tabControl)
	tab7 = ttk.Frame(tabControl)
	tab8 = ttk.Frame(tabControl)

	tabControl.add(tab1, text="Start")
	tabControl.add(tab2, text="Setup")
	tabControl.add(tab3, text="WiFi")
	tabControl.add(tab4, text="Spoofing")
	tabControl.add(tab5, text="Scan")
	tabControl.add(tab6, text="Denial of Service")
	tabControl.add(tab7, text="Services")
	tabControl.add(tab8, text="Commands Injection")

	startview.prepareView(tab1, tabControl, tab2, session)
	setupview.prepareView(tab2, session)
	wifiview.prepareView(tab3, session)
	spoofingview.prepareView(tab4, session)
	scanview.prepareView(tab5, session)
	dosview.prepareView(tab6, session)
	servicesview.prepareView(tab7, session)
	commandsinjectionview.prepareView(tab8, session)

	tabControl.pack(expand=1, fill="both")
	window.mainloop()

if __name__ == '__main__':
	main()