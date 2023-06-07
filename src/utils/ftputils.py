from ftplib import FTP

global ftpConnection

def connectToFtp(host, user, password, port = 21):
    global ftpConnection
    ftpConnection = FTP()
    ftpConnection.connect(host, port)
    ftpConnection.login(user, password)


def getFtpServerVersion():
    return ftpConnection.getwelcome()
    
def pwdFtp():
    return ftpConnection.pwd()

def lsFtp():
    files = []
    ftpConnection.dir(files.append)
    return files

def cwd(path):
    ftpConnection.cwd(path)

def downloadTextFile(fileName, whereSave):
    pathToSave = whereSave+fileName
    with open(pathToSave, 'w') as local_file:
        response = ftpConnection.retrlines('RETR '+fileName, local_file.write)

        if response.startswith("226"):  # Transfer complete
            return "Transfer complete"
        else:
            return "Error transferring. Local file may be incomplete or corrupt."


def downloadBinaryFile(fileName, whereSave):
    pathToSave = whereSave+fileName
    with open(pathToSave, 'wb') as local_file:
        ftpConnection.retrbinary('RETR '+fileName, local_file.write)

def bruteForceFtp():
    pass

