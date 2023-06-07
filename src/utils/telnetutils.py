import os
import stat

from utils import project
def connectTelnet(session, target, port=23):
    uid, gid = session.getSudoUser()

    fileContent = "#!/bin/bash\ntelnet "+target+" "+str(port)
    file = session.path.get()+"/telnet"
    f = open(file, "w")
    f.write(fileContent)
    f.close
    os.chown(file, uid, gid)
    st = os.stat(file)
    os.chmod(file, st.st_mode | stat.S_IEXEC)

    return file
