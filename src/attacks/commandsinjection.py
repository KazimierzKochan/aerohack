from scapy.all import *
from scapy.layers.inet import *

def sendUdpCommand(srcIp, srcPort, dstIp, dstPort, command):
    send(IP(dst=dstIp, src=srcIp)/UDP(dport=int(dstPort), sport=int(srcPort))/Raw(load=command))