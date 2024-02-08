from operator import truediv
import PySimpleGUI as sg
import os, json, re
import copy
from natsort import natsorted
import hashlib
class Config(object):
    def __str__(self):
        return str(self.sethash())

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        try:
            self.sethash()
        except Exception as e:
            None
    def __init__(self, data=None):
        self.pypydir = "/home/will/dissertation/pypy_versions"
        self.methodNames = self.get_methodNames()
        self.methods, self.all_methods = self.get_all_methods()
        self.listlength = [1000]
        self.listcount = 100
        self.outputFilePath = ""
        self.insertion = False
        self.data_types = {
            "Few Unique": False,
            "Sorted": False,
            "Reverse Sorted": False,
            "Nearly Sorted": False,
            "Random": False,
        }
        self.data_sizes = {"large": False, "med": False, "small": False, "tiny": False}
        self.set_config(data)
        self.hash = ''
        self.sethash()
    def items(self):
        items = []
        for key in self.methods.keys():
            items.extend(f"{key}_{val}" for val in self.methods[key])
        return items
    def sethash(self):
        self.hash = hashlib.md5(json.dumps(self.as_json(), separators=(",", ":")).encode("utf-8")).hexdigest()
        return self.hash
    def as_json(self):
        return {
            "pypydir": self.pypydir,
            "methods": self.methods,
            "listlength": self.listlength,
            "listcount": self.listcount,
            "outputFilePath": self.outputFilePath,
            "insertion": self.insertion,
            "data_types": self.data_types,
            "data_sizes": self.data_sizes,
        }
    def set_config(self, data):
        try:
            self.pypydir = data["pypydir"]
            self.methods = data["methods"]
            self.listlength = data["listlength"]
            self.listcount = data["listcount"]
            self.outputFilePath = data["outputFilePath"]
            self.insertion = data["insertion"]
            self.data_types = data["data_types"]
            self.data_sizes = data["data_sizes"]
        except Exception as e:
            None
    def get_methodNames(self):
        try:
            pdir = os.listdir(self.pypydir)
            if len(pdir) < 1:
                raise FileNotFoundError("PyPy not in directory. Check config")
            return sorted(
                {
                    re.findall(r"_(.*)$", x[6:])[0]
                    for x in pdir
                    if x != "timsort_timsort"
                }
            )
        except Exception as f:
            None
    def get_all_methods(self):
        pvs = {}
        pvm = {}
        tempv = os.listdir(self.pypydir)
        for v in self.methodNames:
            values = [x[: -len(v) - 1] for x in tempv if x[-len(v) :] == v]
            values = natsorted(values)
            pvm[v] = values
            pvs.setdefault(v, [])
            for m in pvm[v]:
                tempv.remove(f"{m}_{v}")
        return pvs, pvm




class QueueConfig(object):
    def __init__(self):
        self.queue = []
        self.filename='config.json'
        self.get_q_fromFile()
    def __getitem__(self, item):
         return self.queue[item]
    def __setitem__(self, idx, value):
        self.queue[idx] = value
    def __getattr__(self, name):
        return self.queue[0].__getattribute__(name)
    def get_q_fromFile(self):
        with open(self.filename, "r") as f:
            try:
                data = json.load(f)
            except Exception:
                self.queue=[Config()]
                return

        self.queue = [Config(config_item) for config_item in data["queue"]]
        
    def saveQueue(self):
        with open(self.filename, "w") as f:
            outputfile = {"queue" : []}
            for config in self.queue:                
                outputfile["queue"].append(config.as_json())
            outputfile
            json.dump(outputfile, f)
    def new_config(self, i=1):
        for _ in range(i):
            self.queue.insert(0,Config())
    def remove_duplicates(self):
        i=0
        seen = []
        while i < len(self.queue):
            if self.queue[i].hash not in seen:
                seen.append(self.queue[i].hash)
                i+=1
            else:
                del self.queue[i]
             
q = QueueConfig()
print(q.listlength)
print(q[0].listlength)
q.saveQueue()
