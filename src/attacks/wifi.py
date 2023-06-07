import pyric
import pyric.pyw as pyw

def getNetworkAdapters():
    try:
        return pyw.winterfaces()
    except pyric.error as e:
        print("Error")
