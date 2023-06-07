import subprocess
from scapy.all import Ether, ARP, srp, send

def checkArpTable():
    command = ["arp", "-a"]
    p = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8"
    )
    result = ""
    for line in iter(p.stdout.readline,""):
        result = result+line+"\n"
    return result

def get_mac(ip):
    ans, _ = srp(Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(pdst=ip), timeout=3, verbose=0)
    if ans:
        return ans[0][1].src