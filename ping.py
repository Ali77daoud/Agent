from ping3 import ping
import time

def myping(host):
    resp = ping(host)

    if resp == False:
        return False
    else:
        return True

print(myping("192.168.1.1"))