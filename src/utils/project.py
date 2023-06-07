import datetime
import os
import tkinter as  tk


class project:

    def __init__(self, rootWindow):
        timeNow = str(datetime.datetime.now()).replace(":","-").split(".", 1)[0]

        setPath = os.path.abspath(os.curdir)
        setPath = str(str(setPath)+"/sessions/"+timeNow)
        if not os.path.exists(setPath):
            os.makedirs(setPath)
        
        uid, gid = self.getSudoUser()
        os.chown(setPath, uid, gid)

        neededFiles = ["/scan.txt"]
        for file in neededFiles:
            f = open(setPath+file, "a")
            f.close
            os.chown(setPath+file, uid, gid)

        log = "["+timeNow+"]: created new session: "+setPath+"\n"

        self.path = tk.StringVar(rootWindow, value=setPath)
        self.card = tk.StringVar(rootWindow, value="Not selected yet")
        self.originalInterface = tk.StringVar(rootWindow, value="")
        self.selectedInterface = tk.StringVar(rootWindow, value="")
        self.target = tk.StringVar(rootWindow, value="")
        self.wlanTarget = tk.StringVar(rootWindow, value="192.168.10.1")
        self.drone = tk.StringVar(rootWindow, value="Not selected yet")
        self.logs = tk.StringVar(rootWindow, value=log)
        self.isSpoofing = tk.StringVar(rootWindow, value="OFF")

    def saveLogs(self):
        logsPath = str(self.path.get()) + "/logs.txt"
        with open(logsPath, "a") as logFile:
            logFile.write(str(self.logs.get()))
            logFile.close()
        uid, gid = self.getSudoUser()
        os.chown(logsPath, uid, gid)

    def addLog(self, information):
        timeNow = str(datetime.datetime.now()).replace(":","-").split(".", 1)[0]
        log = "["+timeNow+"]: "+information+"\n"
        print(log)
        self.logs.set(self.logs.get()+log)

    def addToFile(self, file, information):
        with open(self.path.get()+file, "a") as f:
            lines = information.splitlines()
            for line in lines:
                f.write(line)
            f.close()

    def getSession(self):
        return self.path.get()
    
    def udateSession(self):
        timeNow = str(datetime.datetime.now()).replace(":","-").split(".", 1)[0]
        setPath = os.path.abspath(os.curdir)
        setPath = str(str(setPath)+"\sessions\\"+timeNow)
        if not os.path.exists(setPath):
            os.makedirs(setPath) 
        
        self.path.set(setPath)
        self.card.set("Not selected yet")
        self.target.set("Not selected yet")
        self.drone.set("Not selected yet")
    
    def saveInfo(self):
        with open(self.path.get()+"\info.txt", "a") as f:
            f.write("Time: "+self.time.get()+"\n")
            f.write("Selected network adapter: "+self.card.get()+"\n")
            f.write("Selected target: "+self.target.get()+"\n")
            f.close()

    def getSudoUser(self):
        uid = int(os.environ.get("SUDO_UID"))
        gid = int(os.environ.get("SUDO_GID"))
        return uid, gid
