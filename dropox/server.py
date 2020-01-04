import socket
import sys
import threading
import random
import glob
from os import listdir
from os.path import isfile, join, splitext, getsize, getctime
import datetime
import time

#print_lock=threading.Lock()

TCP_IP = '127.0.0.1'
TCP_PORT=5005
BUFFER_SIZE=1024
FILES_DATA={}

def randomMontyPythonAddition():
    switcher={
    0:'must have used the trojan rabbit',
    1:'they used the holy hand grenade! Hallelujah',
    2:"it was the people's front of judea (not to be confused with the judean people's front)"
    }
    return switcher.get(random.randint(0,2))

def getDirectoryTree(path, directoryTree):
    longestFilePathLen=max(len(name[len(name)-name[::-1].index('\\'):]) for name in directoryTree)
    directoryTreeText='\n'+'NAME'.ljust(longestFilePathLen)+'  |EXT         |ISDIR   |SIZE          |CREATE_TIME                   |DOWNLOADS\n'
    for name in directoryTree:
        nameWithoutPath=name[len(name)-name[::-1].index('\\'):]
        if(isfile(name)):
            fileName, fileExtension=splitext(nameWithoutPath)
            fileExtension=fileExtension[1:]
            if(name not in FILES_DATA):
                FILES_DATA[name]=(fileName, fileExtension, str(getsize(name)), str(datetime.datetime.fromtimestamp(getctime(name))), 0)
            directoryTreeText+='\n'+fileName.ljust(longestFilePathLen)+'  |'+fileExtension.ljust(8)+'    |file    |'+FILES_DATA[name][2].ljust(10)+'    |'+FILES_DATA[name][3]+'    |'+str(FILES_DATA[name][4])
        else:
            directoryTreeText+='\n'+nameWithoutPath.ljust(longestFilePathLen)+'  |            |dir     |              |                              |'
    return directoryTreeText

def dealWithClient(conn):
    startClientCommandText='Client '+conn.getpeername()[0]+' requests'
    path=sys.argv[1]
    directoryTree=glob.glob(path+'*')
    printableDirectoryTree=getDirectoryTree(path, directoryTree)
    conn.sendall(('Welcome to dropox!\n'+getDirectoryTree(path, directoryTree)).encode())
    while True:
        command=conn.recv(BUFFER_SIZE).decode()
        if(command=='dir'):
            print(startClientCommandText,'direcotry tree')
            conn.sendall(printableDirectoryTree.encode())
        elif(command=='cd..'):
            print(startClientCommandText,'previous folder')
            if(path.count('\\')>1):
                pathWithNoSlash=(path[:len(path)-1])
                path=pathWithNoSlash[0:len(path) - pathWithNoSlash[::-1].index('\\') - 1]
                directoryTree=glob.glob(path+'*')
                printableDirectoryTree=getDirectoryTree(path, directoryTree)
                conn.sendall(printableDirectoryTree.encode())
            else:
                conn.sendall('Root folder reached. Please choose a different command.'.encode())
        elif(command.startswith('cd ')):
            directory=path+command[3:]
            print(startClientCommandText,'folder ',directory)
            if(directory in directoryTree):
                path=directory+'\\'
                directoryTree=glob.glob(path+'*')
                printableDirectoryTree=getDirectoryTree(path, directoryTree)
                conn.sendall(printableDirectoryTree.encode())
            else:
                conn.sendall('Folder not found. Please choose a different command.'.encode())
        elif(command.startswith('download')):
            filePath=path+command[9:]
            print(startClientCommandText,'file ',filePath)
            if(filePath in directoryTree):
                temp = list(FILES_DATA[filePath])
                temp[4] += 1
                FILES_DATA[filePath] = tuple(temp)
                requestedFile=open(filePath,'rb')
                fileContent=requestedFile.read()
                requestedFile.close()
                printableDirectoryTree=getDirectoryTree(path, directoryTree)
                conn.sendall(fileContent)
            else:
                conn.sendall('File not found. Please choose a different command.'.encode())
        elif(command=='exit'):
            print(startClientCommandText,'to close the connection')
            conn.sendall('Bye'.encode())
            time.sleep(10)
            conn.close()
            break
        else:
            print(startClientCommandText,'unknown command: ', command)
            conn.sendall('Unknown command. Please choose a different command.'.encode())
        

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(10)
    
    while True:
        print('Awaiting connection...')
        conn, addr=s.accept()
        print('Client ',conn.getpeername()[0],' has managed to connect... ', randomMontyPythonAddition())
        #print_lock.acquire()
        threading._start_new_thread(dealWithClient,(conn,))
    s.close()

if __name__ == '__main__': 
    main()