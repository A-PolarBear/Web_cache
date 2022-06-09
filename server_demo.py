import os
import time 
import socket

from _thread import *
import threading
from http.client import HTTPResponse
from datetime import datetime, timedelta

GMT_FORMAT =  "%a, %d %b %Y %H:%M:%S\n"
HOST = "127.0.0.1"
PORT = 65432
FRESH_WHEN = 20
print_lock = threading.Lock()


def handler(conn):
    while True:
        request = conn.recv(4096).decode()
        print(request == "")
        if not request:
            break
        # print(request)

        # parse the request header from client
        headers = request.split('\n')
        dest = headers[0].split()[1].replace('\n', '').replace('\r', '')
        # print("dest",dest)

        # hostname
        hostn = dest.split('/')[1]
        # print("host",hostn)
        
        #pathname
        filename = dest[dest.find(hostn,1)+len(hostn):]

        if filename == "":
            filename = "/"
        
        print("Requesting for {}".format(hostn+filename))

        content = fetch_file(hostn,filename)

        if content:
            response = "HTTP/1.0 200 OK\n\n".encode()+content
        else:
            response = 'HTTP/1.0 404 NOT FOUND\n\n File Not Found'.encode()
        
        conn.sendall(response)
    print(111) 
    conn.close()      


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST,PORT))
        s.listen(5)
        print("Server is listening...")
        while True:
            conn,addr = s.accept()
            print("Connected by {}".format(addr))

            cthread = threading.Thread(target = handler, args=(conn,))
            cthread.start()
        s.close()
            

def fetch_file(hostn,filename):
    file_from_cache= fetch_from_cache(hostn+filename)
    if file_from_cache:
        last_time = os.path.getmtime("./cache/"+(hostn+filename).replace("/","_").replace("?","_"))
        fileTime = time.localtime(last_time)
        # conditional get 
        print("Time diff: {}".format(time.time() - last_time))
        if time.time() - last_time>FRESH_WHEN:
            flag = 1
            print("File in cache is expired.Fetching from server...")
            file_from_server,modifiedFlag= fetch_from_server(hostn,filename,flag,fileTime)
            if file_from_server:
                print("File is from server.")
                save_in_cache(hostn+filename,file_from_server)
                return file_from_server
            elif not modifiedFlag:
                print("File has not been modified, so file is from cache.")
                return file_from_cache
            else:
                return None
        else:
            print("Fetch from cache successfully!")
            return file_from_cache
    else:
        # the file is not in cache
        print("Not in cache.Fetching from server...")
        file_from_server= fetch_from_server(hostn,filename)
        if file_from_server:
            save_in_cache(hostn+filename,file_from_server)
            return file_from_server
        else:
            return None

def fetch_from_cache(filename):
    try:
        tar = filename.replace(':','_').replace('/','_').replace("?","_")
        file = open('./cache/' + tar,'rb')
        # print(time)
        content = file.read()
        file.close()
        return content
    except IOError:
        return None

def fetch_from_server(hostn,filename,conditionalGet = False,fileTime = 0):
    url = filename
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(url)
    try:
        conn.connect((hostn,5678))
        if conditionalGet:
            # request = ("GET "+url+" HTTP/1.1\r\n"+"Host: "+hostn+"\r\n"+"If-Modified-Since:"+" Tue, 07 Jun 2022 21:39:31"+"\r\n"+"Accept:*/*\r\n"+"\r\n").encode()
            request = ("GET "+url+" HTTP/1.1\r\n"+"Host: "+hostn+"\r\n"+"If-Modified-Since:"+time.strftime(GMT_FORMAT,fileTime).replace("\n","")+"\r\n"+"Accept:*/*\r\n"+"\r\n").encode()
        else:
            request = ("GET "+url+" HTTP/1.1\r\n"+"Host: "+hostn+"\r\n"+"Accept:*/*\r\n"+"\r\n").encode()
        # response = conn.makefile('rb')
        # print(request)
        conn.send(request)
        response = HTTPResponse(conn)
        response.begin()
        # print(response.getheaders())
        print(response.status)
        if response.status == 200:
            return response.read(),True
        elif response.status == 304:
            return None,False
        else:
            return None,True
    except Exception as e:
        print(e)
        return None,True


def save_in_cache(filename,content):
    print('Saving a copy of {} in the cache'.format(filename))
    tar = filename.replace(':','_').replace('/','_').replace("?","_")
    cached_file = open('./cache/' + tar, 'wb')
    # cached_file.write(time+'\n')
    cached_file.write(content)
    cached_file.close()
    print('Saving suceed')
                


if __name__ == '__main__':
    while True:
        main()