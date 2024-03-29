import socket
import ssl
from urllib.parse import urlparse
 
def https_test(url):
    proto = "http"
    host = ""
    port = 80
    up = urlparse(url)
    print(111)
    if (up.scheme != ""):
        proto = up.scheme
        print("proto=%s"%proto)
    dest = up.netloc.split(":")
    if (len(dest) == 2):
        port = int(dest[1])
    else:
        if (proto == "http"):
            port = 80
        elif (proto == "https"):
            port = 443
    host = dest[0]
    if (proto == "http"):
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    elif (proto == "https"):    
        sock = ssl.wrap_socket(socket.socket()) 
 
    sock.settimeout(5)
    try:
        sock.connect((host, port)) 
    except Exception as e:
        print ("error %s"%e)
        return None
    
    sock.send("GET {} HTTP/1.1\r\nHost: {}\r\n".format(up.path, host).encode())
    
    response = sock.recv(1024)
    print(response)   
    sock.close()

https_test("https://www.baidu.com")