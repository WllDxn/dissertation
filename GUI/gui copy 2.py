from operator import truediv
import PySimpleGUI as sg
import os, json, re
import copy
from natsort import natsorted
import hashlib
class Config(object):

    def __setattr__(self, name, value):
        super().__setattr__(name, value)


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

    def items(self):
        return [f"{key}_{val}" for key, vals in self.methods.items() for val in vals]
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
        if data:
            for key in ['pypydir', 'methods', 'listlength', 'listcount', 'outputFilePath', 'insertion', 'data_types', 'data_sizes']:
                setattr(self, key, data.get(key, getattr(self, key)))
    def get_methodNames(self):
        pdir = os.listdir(self.pypydir)
        if not pdir:
            raise FileNotFoundError("PyPy not in directory. Check config")
        return sorted({re.findall(r"_(.*)$", x[6:])[0] for x in pdir if x != "timsort_timsort"})
    def get_all_methods(self):
        tempv = os.listdir(self.pypydir)
        pvm = {v: natsorted([x[: -len(v) - 1] for x in tempv if x.endswith(v)]) for v in self.methodNames}
        pvs = {v: [] for v in self.methodNames}
        return pvs, pvm




class QueueConfig(object):
    def __init__(self):
        self.queue = []
        self.filename = 'config.json'
        self.get_q_fromFile()
    def __getitem__(self, item):
         return self.queue[item]
    def __setitem__(self, idx, value):
        self.queue[idx] = value
    def __getattr__(self, name):
        return getattr(self.queue[0], name)

    def get_q_fromFile(self):
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
            self.queue = [Config(config_item) for config_item in data.get("queue", [])]
        except FileNotFoundError:
            self.queue = [Config()]
        
    def saveQueue(self):
        with open(self.filename, "w") as f:
            outputfile = {"queue": [config.as_json() for config in self.queue]}
            json.dump(outputfile, f)
    def new_config(self, data=None, i=1):
        if data is None:
            data = {}
        for _ in range(i):
            self.queue.insert(0,Config(data))
    def remove_duplicates(self):
        i=0
        seen = []
        while i < len(self.queue):
            h = hashlib.md5(json.dumps(self.queue[i].as_json(), separators=(",", ":")).encode("utf-8")).hexdigest()
            if h not in seen:
                seen.append(h)
                i+=1
            else:
                del self.queue[i]
             
   
q = QueueConfig()







items = []
listbox_size = (max(map(len, q.methodNames)) + 2, len(q.methodNames))



        
prev_method = ""
prev_var = ""


        






sg.theme("DarkAmber")  # Add a touch of color
# All the stuff inside your window.
dt_column = [
    [sg.Text("Data Type:")],
    [
        sg.Checkbox(
            "Few Unique", default=q.data_types["Few Unique"], key="Few Unique", enable_events=True
        )
    ],
    [sg.Checkbox("Sorted", default=q.data_types["Sorted"], key="Sorted", enable_events=True)],
    [
        sg.Checkbox(
            "Reverse Sorted",
            default=q.data_types["Reverse Sorted"],
            key="Reverse Sorted",
            enable_events=True
        )
    ],
    [
        sg.Checkbox(
            "Nearly Sorted",
            default=q.data_types["Nearly Sorted"],
            key="Nearly Sorted",
            enable_events=True
        )
    ],
    [sg.Checkbox("Random", default=q.data_types["Random"], key="Random", enable_events=True)],
]
ds_column = [
    [sg.Text("Data Size:")],
    [sg.Checkbox("large", default=q.data_sizes["large"], key="large", enable_events=True)],
    [sg.Checkbox("med", default=q.data_sizes["med"], key="med", enable_events=True)],
    [sg.Checkbox("small", default=q.data_sizes["small"], key="small", enable_events=True)],
    [sg.Checkbox("tiny", default=q.data_sizes["tiny"], key="tiny", enable_events=True)],
    [sg.Text("")],
]
input_labels = [
    [sg.Text("List length (l)")],
    [sg.Text("List count (n)")],
    [sg.Text("Output file (o)")],
    [sg.Text("Insertion test (s)")],
]
inputs = [
    [
        sg.InputText(
            q.listlength, key="listlength", enable_events=True
        )
    ],
    [sg.InputText(q.listcount, key="listcount", enable_events=True)],
    [sg.InputText(key="pretty_filename", visible=True)],
    [sg.Checkbox("", default=q.insertion, key="insertion", enable_events=True)],
]


layout = [
    [
        sg.Listbox(
            q.methodNames,
            size=listbox_size,
            expand_y=True,
            default_values=q.methodNames[0],
            enable_events=True,
            key="methods_var",
            select_mode="LISTBOX_SELECT_MODE_SINGLE",
            bind_return_key=True,
        ),
        sg.Listbox(
            q.all_methods[q.methodNames[0]],
            default_values=q.methods[q.methodNames[0]],
            size=listbox_size,
            expand_y=True,
            select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
            key="method_imps",
            enable_events=True,
        ),
        sg.Listbox(
            q.items(),
            size=listbox_size,
            expand_y=True,
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            key="methods_selected",
            metadata=[],
            enable_events=True,
            bind_return_key=True,
        ),
    ],
    [
        sg.Column(dt_column),
        sg.Column(ds_column),
        sg.Column(input_labels, size=(100, 100)),
        sg.Column(inputs, size=(200, 100)),
    ],
    [
        [
            sg.Button("Update Output", key="update_button"),
            sg.Button("Save", key="save_config"),
            sg.Button("Sort", key="start_sorting"),
            sg.Button("Queue", key="add_queue"),
            sg.Button("Clear Queue", key="clear_queue"),
            sg.Text(
                str(len(q.queue)), key="queuelen"
            ),
        ],
        [sg.InputText(key="output_filename", visible=False)],
    ],
]


# Create the Window
window = sg.Window("Sorting Helper", layout, location=(500, 500))


# Event Loop to process "events" and get the "values" of the inputs
def methodevent(prev_method):
    for key in q.methods.keys():
        vals = list(q.methods[key])
        for val in vals:
            option = f"{key}_{val}"
            selection = (
                window["methods_selected"].get()[0] if len(window["methods_selected"].get()) > 0 else ""
            )
            if selection == option:
                if prev_method == window["methods_selected"].get()[0]:
                    q.methods[key].remove(val)
                    window["method_imps"].set_value([x for x in window["method_imps"].get() if x != val])
                    window["methods_selected"].update(q.items())
                    prev_method = ""
                else:
                    prev_method = window["methods_selected"].get()[0]
                    window["methods_var"].set_value(
                        [
                            key,
                        ]
                    )
                minevent(window["methods_var"].get()[0], False)
                return prev_method


def maxevent():
    q.methods[window["methods_var"].get()[0]] = window["method_imps"].get()
    items = []
    for key in q.methods.keys():
        items.extend(f"{key}_{val}" for val in q.methods[key])
    window["methods_selected"].update(items)


def minevent(curr, reset=True):
    window["method_imps"].update(q.all_methods[curr])
    window["method_imps"].set_value(q.methods[curr] or [])
    if reset:
        window["methods_selected"].set_value([])


def mindouble():
    global prev_var
    curr_var = window["methods_var"].get()[0]
    if prev_var == curr_var:
        window["method_imps"].update(q.all_methods[curr_var])
        if q.all_methods[curr_var] == q.methods[curr_var]:
            window["method_imps"].set_value([])
        else:
            window["method_imps"].set_value(q.all_methods[curr_var])
        maxevent()
        return ""
    else:
        minevent(curr_var)
        return curr_var




def get_checkboxes(cb):
    if cb == 'insertion':
        q.insertion = window["insertion"].get()
    elif cb in list(q.data_types.keys()):
        q.data_types[cb] = window[cb].get()
    elif cb in list(q.data_sizes.keys()):
        q.data_sizes[cb] = window[cb].get()

def get_filename(name):
    path = os.path.join("/home/will/dissertation/sort_times", f"{name}_0.json")
    uniq = 0
    while os.path.exists(path) or path in [x.outputFilePath for x in q.queue if x.outputFilePath]:
        path = os.path.join(
            "/home/will/dissertation/sort_times", f"{name}_{str(uniq)}.json"
        )
        uniq += 1
    return path


def get_output(force=False):
    methods = [
        key
        for key in q.methods.keys()
        if len(q.methods[key]) > 0
    ]
    if window["pretty_filename"].get() and force == True:
        path = "/home/will/dissertation/sort_times/" + window["pretty_filename"].get()
    else:
        path = (
            (
                get_filename("_".join(methods))
                if len(methods) > 1
                else get_filename(methods[0])
            )
        )
    window["output_filename"].update(path)
    window["pretty_filename"].update(re.findall(r"([^\/]+$)", path)[0])
    q[0].outputFilePath=re.findall(r"([^\/]+$)", path)[0]

def clearitems():
    for cb in ["Few Unique","Sorted","Reverse Sorted","Nearly Sorted","Random","large","med","small","tiny","insertion"]:
        if cb == 'insertion':
            window["insertion"].update(q.insertion)
        elif cb in list(q.data_types.keys()):
            window[cb].update(q.data_types[cb])
        elif cb in list(q.data_sizes.keys()):
            window[cb].update(q.data_sizes[cb])
    window['listlength'].update(q.listlength)
    window['listcount'].update(q.listcount)
    window['methods_var'].set_value(q.methodNames[0])
    window['method_imps'].update(q.all_methods[q.methodNames[0]])
    window['method_imps'].set_value(q.methods[q.methodNames[0]])
    window['methods_selected'].update(q.items())
    window['output_filename'].update(q.outputFilePath)
    window["pretty_filename"].update(re.findall(r"([^\/]+$)", q.outputFilePath)[0])

while True:
    event, values = window.read()
    if event in [sg.WIN_CLOSED, "Cancel"]:  # if user closes window or clicks cancel
        # save_options()
        break
    elif event == "methods_var":
        prev_var = mindouble()
        prev_method = ""
    elif event == "method_imps":
        maxevent()
        prev_method = ""
        prev_var = ""
    elif event == "methods_selected":
        prev_method = methodevent(prev_method)
        prev_var = ""
    elif event == "listcount":
        val = (
            re.sub("[^0-9]", "", window["listcount"].get())
            if window["listcount"].get() != ""
            else 0
        )
        val = min(1000000, max(0, int(val)))
        window["listcount"].update(val)
        q[0].listcount = val
    elif event == "listlength":
        val = re.sub("[^0-9, ]", "", window["listlength"].get()).replace(" ", "")
        end = val[-1] == "," if len(val) != 0 else False
        val = [int(x.strip()) for x in val.split(",") if x.strip() != ""]
        q[0].listlength = val
        out = ", ".join(map(str, val))
        out = f"{out}," if end else out
        window["listlength"].update(out)

    elif event == "update_button":
        try:
            get_output()
        except Exception:
            sg.popup('Add at least 1 method')
    elif event == "save_config":
        get_output(force=True)
        q.saveQueue()
    elif event == "start_sorting":
        if window["output_filename"].get() == "":
            get_output()
        q.saveQueue()
        break
    elif event == "add_queue":
        if window["output_filename"].get() == "":
            get_output()
        get_output(force=True)            
        q.saveQueue()
        q.new_config()
        q.queue[0] = copy.deepcopy(q.queue[1])
        window['queuelen'].update(len(q.queue))
    elif event == "clear_queue":
        q.queue = []
        q.new_config()
        q.saveQueue()
        clearitems()        
        window['queuelen'].update(len(q.queue))
    else:
        get_checkboxes(event)
window.close()
# import itertools

data_sizes = ["large", "med", "small", "tiny"]
data_types = ["Few Unique", "Sorted", "Reverse Sorted", "Nearly Sorted", "Random"]


def get_commands(m, c):
    sizes = str([f"{str(size)}" for size in data_sizes if not c[size]])[1:-1].replace(
        ",", ""
    )
    types = str([f"{str(t)}" for t in data_types if not c[t]])[1:-1].replace(",", "")
    lengths = str([int(x) for x in c["listlength"].split(",")])[1:-1].replace(",", "")
    methodname = re.findall(r"([^\/]+$)", m)[0]
    yield f' sort_timer_gendata_pipe.py -m {methodname} -o {c["output"]} -n {c["listcount"]} -l {lengths} -et {types} -es {sizes} {"-s" if c["insertion"]==True else ""}'


def get_methodCommand():
    methodCommand = []
    for c in queue:
        for method in get_methods(c):
            path = f"/home/will/dissertation/pypy_versions/{method}/bin/pypy"
            methodCommand.extend(
                (path, command, method) for command in get_commands(method, c)
            )
    return methodCommand


qlen = len(queue)
methodCommand = get_methodCommand()
multilinecol = [
    [
        sg.Multiline(
            f"{queue}",
            size=(50, 30),
            echo_stdout_stderr=False,
            reroute_stdout=False,
            autoscroll=True,
            background_color="black",
            text_color="white",
            key="completed",
        )
    ],
    [
        sg.Multiline(
            f"{len(methodCommand)} items, Run to start. Queue length: {qlen}",
            size=(50, 2),
            echo_stdout_stderr=False,
            reroute_stdout=False,
            autoscroll=True,
            background_color="black",
            text_color="white",
            key="-MLINE-",
        )
    ],
]
layout2 = [
    [sg.Column(multilinecol)],
    [sg.Button("Run", bind_return_key=True), sg.Text("Completed: ", key="iters")],
]
window2 = sg.Window("Sorting Helper 2", layout2, location=(500, 500), finalize=True)

import subprocess, sys


def get_outpout(items, method):
    match = re.match(r"(.*?\d+)+", method)
    if match:
        method = match[1]
    if items[0] == "count":
        return ("Green", f"{method}\t {items[1]} {items[2]} \t {items[3]}/{items[4]}")
    elif items[0] == "warming":
        return ("Cyan", f"{method}\t Warming up: \t{items[1]}/{items[2]}")
    elif items[0] == "eval":
        insr = "" if items[6] == "1" else f"/{items[6]}"
        return (
            "Red",
            f'{method} {items[1]} {items[2]} {items[3]} s\t{items[4]}{insr}\t\t {"" if items[5] else "error"}',
        )
    elif items[0] == "Total":
        return ("Purple", f"{method} Total time: {items[1]}")
    else:
        return ("White", str(items))


def runCommand(cmd, method, timeout=None, window=None):
    print(cmd)
    p = subprocess.Popen(
        cmd, shell=True, cwd="/home/will/dissertation", stdout=subprocess.PIPE
    )
    out = ""
    cont = True
    while cont:
        cont = p.poll() is None
        out += p.stdout.read(1 if cont else -1).decode(
            errors="replace" if (sys.version_info) < (3, 5) else "backslashreplace"
        )
        if "\n" in out:
            for o in out.split("\n"):
                colour, text = get_outpout(o.split(","), method)
                if colour == "White":
                    continue
                elif colour == "Red" or colour == "Purple":
                    window["completed"].print(
                        text,
                        end="\n",
                        text_color=colour,
                        autoscroll=True,
                    )
                    window["-MLINE-"].update("", append=False)
                else:
                    window["-MLINE-"].update(
                        text,
                        text_color_for_value=colour,
                        append=False,
                        autoscroll=True,
                    )
                out = out[out.find("\n") + 1 :]
        window.Refresh()


import time
from datetime import timedelta


def dhm(duration):
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours}h : {minutes}m : {seconds}s"


while True:
    event, values = window2.read()
    if event in [sg.WIN_CLOSED, "Cancel"]:  # if user closes window or clicks cancel
        break
    elif event == "Run":
        t = time.time()
        for count, (path, command, method) in enumerate(methodCommand, start=1):
            runCommand(f"{path} {command}", method, window=window2)
            ctime = timedelta(seconds=time.time() - t)
            remtime = (ctime / count) * (len(methodCommand) - count)
            window2["iters"].update(
                value=f"Completed: {count}/{len(methodCommand)} Time used: {dhm(ctime)}  Remaining: {dhm(remtime)}"
            )
window2.close()
