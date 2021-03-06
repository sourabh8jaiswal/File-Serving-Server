import socket
import os
import sys
import pathlib
import threading
import Model as mm
from uuid import uuid1

class MyThread(threading.Thread):
    def  __init__(self,clientSocket,model):
        self.socket=clientSocket
        self.model=model
        self.files=model.files_dict
        self.users=model.users_dict
        self.usersId=model.usersId_dict
        self.usersSemaphores=model.usersSemaphores_dict
        threading.Thread.__init__(self)
        self.start()
    def run(self):
        bytesToReceive=4096
        dataBytes=b''
        while len(dataBytes)<bytesToReceive:
            by=self.socket.recv(bytesToReceive-len(dataBytes))
            dataBytes+=by
        bytesToReceive=int(dataBytes.decode('utf-8').strip())
        dataBytes=b''
        while len(dataBytes)<bytesToReceive:
            by=self.socket.recv(bytesToReceive-len(dataBytes))
            dataBytes+=by
        user_info=eval(dataBytes.decode('utf-8'))
        uname=user_info[0]
        pwd=user_info[1]
        status=''
        if uname in self.users and pwd==self.users[uname]: status='correct'
        else: status='incorrect'
        if status=='correct':
            uid=uuid1()
            uid=str(uid)
            self.usersId[uid]=uname
            res=(status,uid)
            res=str(res)
        else:
            res=(status,)
            res=str(res)
        response=bytes(res,encoding='utf-8')
        self.socket.sendall(bytes(str(len(response)).ljust(4096),encoding='utf-8'))
        self.socket.sendall(response)
        if status=="incorrect":return
        while True:
            bytesToReceive=4096
            dataBytes=b''
            while len(dataBytes)<bytesToReceive:
                by=self.socket.recv(bytesToReceive-len(dataBytes))
                dataBytes+=by
            requestSize=int(dataBytes.decode("utf-8").strip())
            bytesToReceive=requestSize
            dataBytes=b''
            while len(dataBytes)<bytesToReceive:
                by=self.socket.recv(bytesToReceive-len(dataBytes))
                dataBytes+=by
            request_tuple=eval(dataBytes.decode("utf-8"))
            request=request_tuple[0]
            userId=request_tuple[1]
            if userId in self.usersId==False:
                status='failed'
            else:
                status='success'
            response_tuple=(status,)
            response_tuple=bytes(str(response_tuple),'utf-8')
            self.socket.sendall(bytes(str(len(response_tuple)).ljust(4096),'utf-8'))
            self.socket.sendall(response_tuple)
            if status=='failed':
                self.socket.close()
                break
            if request=="quit":
                self.usersId.pop(userId)
                response='exit'
                self.socket.sendall(bytes(str(len(response)).ljust(4096),'utf-8'))
                self.socket.sendall(bytes(response,'utf-8'))
                self.socket.close()
                break
            if request=="dir":                
                response=bytes(str(self.files),'utf-8')
                self.socket.sendall(bytes(str(len(response)).ljust(4096),"utf-8"))
                self.socket.sendall(response)
            if request.split()[0]=="get":
                fileName=request[4:]
                response='invalid'
                if fileName in self.files : response='valid'
                responseLengthHeader=bytes(str(len(response)).ljust(4096),"utf-8")
                self.socket.sendall(responseLengthHeader)
                self.socket.sendall(bytes(response,encoding='utf-8'))
                if response=="invalid" : continue
                self.usersSemaphores[fileName].acquire();
                fileSize=self.files[fileName]
                self.socket.sendall(bytes(str(fileSize).ljust(4096),encoding='utf-8'))
                chunkSize=4096
                bytesRead=0
                with open("store"+os.path.sep+fileName,"rb") as file:
                    while bytesRead<fileSize:
                        by=file.read(chunkSize)
                        self.socket.sendall(by)
                        bytesRead+=chunkSize
                        if fileSize-bytesRead<chunkSize : chunkSize=fileSize-bytesRead
                self.usersSemaphores[fileName].release();

model=mm.Model()
serverSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serverSocket.bind(("localhost",5500))
serverSocket.listen()
while True:
    print("server is ready and is listening on port 5500")
    clientSocket,socketName=serverSocket.accept()
    mt=MyThread(clientSocket,model)
serverSocket.close()
