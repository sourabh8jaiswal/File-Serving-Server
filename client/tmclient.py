import socket
import os
import sys
import pathlib

clientSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientSocket.connect(("localhost",5500))
username=input("username : ")
password=input("password : ")
user_info=(username,password)
user_info=bytes(str(user_info),"utf-8")
clientSocket.sendall(bytes(str(len(user_info)).ljust(4096),encoding='utf-8'))
clientSocket.sendall(user_info)
bytesToReceive=4096
dataBytes=b''
while len(dataBytes)<bytesToReceive:
    by=clientSocket.recv(bytesToReceive-len(dataBytes))
    dataBytes+=by
bytesToReceive=int(dataBytes.decode('utf-8').strip())
dataBytes=b''
while len(dataBytes)<bytesToReceive:
    by=clientSocket.recv(bytesToReceive-len(dataBytes))
    dataBytes+=by
response=eval(dataBytes.decode('utf-8'))
status=response[0]
userId=''
if status=="incorrect":
    print("invalid username/password")
    clientSocket.close()
    sys.exit()
else :
    userId=response[1]
while True:
    request=input("tmclient>")
    request_tuple=(request,userId)
    request_tuple=str(request_tuple)
    request_tuple=bytes(request_tuple,encoding='utf-8')
    requestLengthHeader=bytes(str(len(request_tuple)).ljust(4096),encoding='utf-8')
    clientSocket.sendall(requestLengthHeader)
    clientSocket.sendall(request_tuple)
    bytesToReceive=4096
    dataBytes=b''
    while len(dataBytes)<bytesToReceive:
        by=clientSocket.recv(bytesToReceive-len(dataBytes))
        dataBytes+=by
    bytesToReceive=int(dataBytes.decode('utf-8').strip())
    dataBytes=b''
    while len(dataBytes)<bytesToReceive:
        by=clientSocket.recv(bytesToReceive-len(dataBytes))
        dataBytes+=by
    response_tuple=eval(dataBytes.decode())
    status=response_tuple[0]
    if status=='failed':
        break
    if request=="quit":
        bytesToReceive=4096
        dataBytes=b''
        while len(dataBytes)<bytesToReceive:
            by=clientSocket.recv(bytesToReceive-len(dataBytes))
            dataBytes+=by
        bytesToReceive=int(dataBytes.decode('utf-8').strip())
        dataBytes=b''
        while len(dataBytes)<bytesToReceive:
            by=clientSocket.recv(bytesToReceive-len(dataBytes))
            dataBytes+=by
        response=dataBytes.decode()
        if response=='exit':
            print("good bye !")
            break
    elif request=="dir":
        bytesToReceive=4096
        dataBytes=b''
        while len(dataBytes)<bytesToReceive:
            by=clientSocket.recv(bytesToReceive-len(dataBytes))
            dataBytes+=by
        bytesToReceive=int(dataBytes.decode("utf-8").strip())
        dataBytes=b''
        while len(dataBytes)<bytesToReceive:
            by=clientSocket.recv(bytesToReceive-len(dataBytes))
            dataBytes+=by
        files=eval(dataBytes.decode())
        for file in files:
            print(file.ljust(60),str(files[file]).rjust(20))
    elif request.split()[0]=="get":
        fileName=request[4:]
        bytesToReceive=4096
        dataBytes=b''
        while len(dataBytes)<bytesToReceive:
            by=clientSocket.recv(bytesToReceive-len(dataBytes))
            dataBytes+=by
        bytesToReceive=int(dataBytes.decode("utf-8").strip())
        dataBytes=b''
        while len(dataBytes)<bytesToReceive:
            by=clientSocket.recv(bytesToReceive-len(dataBytes))
            dataBytes+=by
        response=dataBytes.decode('utf-8')
        if response=="invalid" :
            print("The file, you are looking for, is unavailable")            
        if response=="valid" :
            print("waiting for download to begin ...");
            bytesToReceive=4096
            dataBytes=b''
            while len(dataBytes)<bytesToReceive:
                by=clientSocket.recv(bytesToReceive-len(dataBytes))
                dataBytes+=by
            fileSize=int(dataBytes.decode("utf-8").strip())
            chunkSize=4096
            bytesRead=0
            with open("store"+os.path.sep+fileName,"wb") as file :
                while bytesRead<fileSize:
                        dataBytes=b''
                        while len(dataBytes)<chunkSize:
                            by=clientSocket.recv(chunkSize-len(dataBytes))
                            dataBytes+=by
                        file.write(dataBytes)
                        bytesRead+=chunkSize
                        print("Total bytes received :",bytesRead);
                        if fileSize-bytesRead<chunkSize: chunkSize=fileSize-bytesRead
            saveAs=input("Save as ? : ")
            pth=pathlib.Path("store"+os.path.sep+fileName)
            pth.rename(pathlib.Path("store"+os.path.sep+saveAs))
    else:
        print("invalid request")

clientSocket.close()