import os
import datetime
from threading import Semaphore
class Model:
    def __init__(self):
        self.files_dict=dict()
        self.users_dict=dict()
        self.usersId_dict=dict()
        self.usersSemaphores_dict=dict()
        self.populateDatastructures()
    def populateDatastructures(self):
        ff=os.scandir("store")
        for entry in ff:
            name=entry.name
            size=entry.stat().st_size
            self.files_dict[name]=size
            self.usersSemaphores_dict[name]=Semaphore(2);
        with open("users.data","r") as file:
            while True:
                a=file.readline()
                if len(a)==0: break
                record=eval(a)
                username=record[0]
                password=record[1]
                self.users_dict[username]=password
            