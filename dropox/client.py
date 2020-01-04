import sys
import socket
import time

TCP_IP = sys.argv[1]
TCP_PORT=5005
BUFFER_SIZE=1024


def main():
    commandList=['cd <folder name> - enter folder', 'cd.. - go back', 'dir - shows current directory contents', 'download <file name.extension> - downloads file', 'exit - exists dropox']
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP,TCP_PORT))
    s.settimeout(0.1)

    command='dir'
    
    while True:
        textRecieved=''
        fileFound=True
        if(command!='help'):
            totalData=bytes()
            try:
                data=s.recv(BUFFER_SIZE)
                while data:
                    if(command.startswith('download')):
                        data=data.strip()
                    totalData+=data
                    data=s.recv(BUFFER_SIZE)
            except socket.timeout:
                try:
                    textRecieved=totalData.decode()
                    fileFound=False
                except UnicodeDecodeError:
                    pass
                pass
            if(command.startswith('download') and fileFound):
                requestedFile=open(command[9:],'wb')
                requestedFile.write(totalData)
                requestedFile.close()
                print('File downloaded successfully!\n')
            else:
                print(textRecieved,'\n')
            if(textRecieved=='Bye'):
                s.close()
                break
        command=input('What would you like to do?\nEnter "help" for command list\n\n')
        if(command==''):
            command='none'
        if(command=='help'):
            print(*commandList, sep = '\n')
            print('\n')
        else:
            s.sendall(command.encode())
        
    s.close()

if __name__ == '__main__': 
    main()
